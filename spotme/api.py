from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import date

BASE_URL = "https://spotme.jdn.gov.my"


class SpotMeAPIError(RuntimeError):
    pass


class SpotMeAPI:
    """Provisional HTTP client for previously observed SPOT-Me routes.

    This client is not wired into Run System. Login payload/token parsing is
    unverified and must be checked against an authorized, current portal
    request before relying on it.
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
            # Do not include the response body: it may contain personal data,
            # account details or server diagnostics.
            raise SpotMeAPIError(f"HTTP {exc.code}: request was rejected.") from exc
        except urllib.error.URLError as exc:
            raise SpotMeAPIError("Network request failed.") from exc
        except TimeoutError as exc:
            raise SpotMeAPIError("Network request timed out.") from exc
        except json.JSONDecodeError as exc:
            raise SpotMeAPIError("API returned invalid JSON.") from exc

    def login(self, user: str, password: str) -> dict:
        data = self._request(
            "/api/login",
            "POST",
            {"mykad": user, "katalaluan": password},
        )
        if not isinstance(data, dict):
            raise SpotMeAPIError("Login returned an unexpected response structure.")

        # Candidate token keys from earlier inspection; not an established contract.
        token = data.get("token") or data.get("access_token")
        if not token:
            token = data.get("authce9d77b308c149d5992a80073637e4d5")
        if not isinstance(token, str) or not token:
            raise SpotMeAPIError(
                "Login response did not contain a recognized token field."
            )
        self.token = token
        return data

    def check_eligibility(self) -> dict:
        result = self._request("/api/checking")
        if not isinstance(result, dict):
            raise SpotMeAPIError("Checking endpoint returned an unexpected structure.")
        return result

    def daily_movements(self, date_iso: str) -> list | dict:
        if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", date_iso or ""):
            raise ValueError("Date must use YYYY-MM-DD format.")
        try:
            date.fromisoformat(date_iso)
        except ValueError as exc:
            raise ValueError("Date is not a valid calendar date.") from exc

        result = self._request("/api/harian?tarikh=" + date_iso)
        if not isinstance(result, (dict, list)):
            raise SpotMeAPIError("Daily endpoint returned an unexpected structure.")
        return result
