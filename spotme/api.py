from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser

BASE_URL = "https://spotme.jdn.gov.my"
MAX_HTML_BYTES = 1_000_000
MAX_SCRIPT_BYTES = 1_500_000
MAX_SCRIPTS = 15


class SpotMeAPIError(RuntimeError):
    pass


class _ScriptSourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        values = dict(attrs)
        src = values.get("src")
        if src:
            self.sources.append(src)


class SpotMeAPI:
    """Read-only portal diagnostics and provisional API client.

    Portal inspection downloads only the public landing page and same-origin
    JavaScript assets. It reports candidate routes; it never submits login,
    attendance, movement, or other write requests.
    """

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.token = ""

    def _request(self, path: str, method: str = "GET", payload: dict | None = None):
        headers = {
            "Accept": "application/json",
            "User-Agent": "spotme-cli/0.2.0",
        }
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = urllib.request.Request(
            BASE_URL + path, data=body, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                result = json.loads(raw) if raw else {}
                if not isinstance(result, (dict, list)):
                    raise SpotMeAPIError("API returned an unexpected JSON structure.")
                return result
        except urllib.error.HTTPError as exc:
            raise SpotMeAPIError(f"HTTP {exc.code}: request was rejected.") from exc
        except urllib.error.URLError as exc:
            raise SpotMeAPIError("Network request failed.") from exc
        except TimeoutError as exc:
            raise SpotMeAPIError("Network request timed out.") from exc
        except json.JSONDecodeError as exc:
            raise SpotMeAPIError("API returned invalid JSON.") from exc

    def check_portal_connection(self) -> tuple[bool, int | None]:
        """Check basic portal reachability without authenticating or changing data."""
        req = urllib.request.Request(
            BASE_URL + "/",
            headers={"Accept": "text/html,application/json", "User-Agent": "spotme-cli/0.2.0"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return True, response.status
        except urllib.error.HTTPError as exc:
            return True, exc.code
        except (urllib.error.URLError, TimeoutError):
            return False, None

    @staticmethod
    def _read_limited(response, limit: int) -> str:
        raw = response.read(limit + 1)
        if len(raw) > limit:
            raw = raw[:limit]
        return raw.decode("utf-8", errors="replace")

    def inspect_portal(self) -> dict:
        """Inspect public frontend assets and return API route candidates only."""
        result = {
            "reachable": False,
            "http_status": None,
            "scripts_found": 0,
            "scripts_scanned": 0,
            "routes": [],
            "login_hints": {"post_method_seen": False, "request_fields": [], "token_keys": []},
            "warnings": [],
        }
        request = urllib.request.Request(
            BASE_URL + "/",
            headers={"Accept": "text/html", "User-Agent": "spotme-cli/0.2.0"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result["reachable"] = True
                result["http_status"] = response.status
                html = self._read_limited(response, MAX_HTML_BYTES)
        except urllib.error.HTTPError as exc:
            result["reachable"] = True
            result["http_status"] = exc.code
            result["warnings"].append("Portal returned an HTTP error; frontend scan skipped.")
            return result
        except urllib.error.URLError:
            result["warnings"].append("Network connection failed.")
            return result
        except TimeoutError:
            result["warnings"].append("Portal request timed out.")
            return result

        parser = _ScriptSourceParser()
        try:
            parser.feed(html)
        except Exception:
            result["warnings"].append("Some landing-page markup could not be parsed.")

        origin = urllib.parse.urlparse(BASE_URL)
        script_urls = []
        for source in parser.sources:
            url = urllib.parse.urljoin(BASE_URL + "/", source)
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ("http", "https") or parsed.netloc != origin.netloc:
                continue
            if url not in script_urls:
                script_urls.append(url)

        result["scripts_found"] = len(script_urls)
        sources = [html]
        for url in script_urls[:MAX_SCRIPTS]:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/javascript,text/javascript,*/*",
                         "User-Agent": "spotme-cli/0.2.0"},
                method="GET",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    final = urllib.parse.urlparse(response.geturl())
                    if final.netloc != origin.netloc:
                        continue
                    sources.append(self._read_limited(response, MAX_SCRIPT_BYTES))
                    result["scripts_scanned"] += 1
            except (urllib.error.URLError, TimeoutError, urllib.error.HTTPError):
                continue

        route_pattern = re.compile(
            r"""(?<![A-Za-z0-9])((?:/)?api/[A-Za-z0-9_./{}:-]{1,120})"""
        )
        routes = set()
        login_contexts = []
        for source in sources:
            for match in route_pattern.findall(source):
                route = "/" + match.lstrip("/")
                route = route.rstrip(".,;:)]}'\\"")
                if route.startswith("/api/"):
                    routes.add(route)
                if "login" in route.lower():
                    for found in re.finditer(re.escape(match), source, flags=re.IGNORECASE):
                        login_contexts.append(source[max(0, found.start() - 1200):found.end() + 1800])

        result["routes"] = sorted(routes)[:100]
        login_text = "\\n".join(login_contexts)
        if login_text:
            hints = result["login_hints"]
            hints["post_method_seen"] = bool(
                re.search(r"""(?:method\s*[:=]\s*['"]POST|\.post\s*\\()""", login_text, re.IGNORECASE)
            )
            known_fields = (
                "mykad", "katalaluan", "password", "username",
                "user_id", "spotme_device_id", "device_id", "otp",
            )
            hints["request_fields"] = [
                field for field in known_fields
                if re.search(r"""['"]""" + re.escape(field) + r"""['"]""", login_text, re.IGNORECASE)
            ]
            token_pattern = re.compile(
                r"""['"]([A-Za-z_][A-Za-z0-9_]{1,80}(?:token|auth)[A-Za-z0-9_]*)['"]""",
                re.IGNORECASE,
            )
            hints["token_keys"] = sorted(set(token_pattern.findall(login_text)))[:20]
        if len(script_urls) > MAX_SCRIPTS:
            result["warnings"].append(
                f"Scan limited to the first {MAX_SCRIPTS} same-origin JavaScript files."
            )
        if not result["routes"]:
            result["warnings"].append(
                "No API route strings were detected; this does not prove that no API exists."
            )
        return result

    def login(self, user: str, password: str) -> dict:
        """Provisional only: do not call until the live login contract is verified."""
        data = self._request(
            "/api/login",
            "POST",
            {"mykad": user, "katalaluan": password},
        )
        if not isinstance(data, dict):
            raise SpotMeAPIError("Login returned an unexpected response structure.")
        token = data.get("token") or data.get("access_token")
        if not token:
            token = data.get("authce9d77b308c149d5992a80073637e4d5")
        if not isinstance(token, str) or not token:
            raise SpotMeAPIError("Login response did not contain a recognized token field.")
        self.token = token
        return data

    def check_eligibility(self) -> dict:
        result = self._request("/api/checking")
        if not isinstance(result, dict):
            raise SpotMeAPIError("Checking endpoint returned an unexpected structure.")
        return result

    def daily_movements(self, date_iso: str) -> list | dict:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_iso or ""):
            raise ValueError("Date must use YYYY-MM-DD format.")
        try:
            date.fromisoformat(date_iso)
        except ValueError as exc:
            raise ValueError("Date is not a valid calendar date.") from exc
        result = self._request("/api/harian?tarikh=" + date_iso)
        if not isinstance(result, (dict, list)):
            raise SpotMeAPIError("Daily endpoint returned an unexpected structure.")
        return result
