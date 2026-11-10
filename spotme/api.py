from __future__ import annotations
import json
import urllib.error
import urllib.request

BASE_URL = "https://spotme.jdn.gov.my"

class SpotMeAPIError(RuntimeError):
    pass

class SpotMeAPI:
    """HTTP client for login and read-only account/status endpoints."""
    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.token = ""

    def _request(self, path: str, method: str = "GET", payload: dict | None = None):
        headers = {"Accept": "application/json", "User-Agent": "spotme-cli/0.2.0"}
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(BASE_URL + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise SpotMeAPIError(f"HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise SpotMeAPIError(str(exc)) from exc

    def login(self, user: str, password: str) -> dict:
        data = self._request("/api/login", "POST", {"mykad": user, "katalaluan": password})
        token = data.get("token") or data.get("access_token")
        if not token:
            # The observed API may return its token under a nonstandard key.
            token = data.get("authce9d77b308c149d5992a80073637e4d5")
        if not token:
            raise SpotMeAPIError("Login memberi respons tetapi token tidak ditemui. Semak struktur respons API.")
        self.token = token
        return data

    def check_eligibility(self) -> dict:
        return self._request("/api/checking")

    def daily_movements(self, date_iso: str) -> dict:
        return self._request("/api/harian?tarikh=" + date_iso)
