# SPOT-Me API inventory

This document records observations from earlier inspection of the SPOT-Me web portal and browser Network activity. It is an investigation log, **not official API documentation**.

Base URL observed:

`https://spotme.jdn.gov.my`

## Evidence levels

- **Observed in Network / response**: a request was seen during an earlier inspection. This does not guarantee the endpoint is stable or officially supported.
- **Found in portal JavaScript**: a route or feature name was found in downloaded frontend code. Request schema and server behavior are not confirmed.
- **Not verified**: do not integrate or call as an operational feature until tested with an authorized account and documented safely.

The original HAR/response captures are not currently stored in this repository. Historical details below are transcribed from the project investigation notes and should be re-captured before implementation.

## Authentication and account

| Method | Path | Evidence | Notes |
|---|---|---|---|
| POST | `/api/login` | Network test observed | Earlier blank/invalid test returned HTTP 401 with `{"success":false}`. This does not establish the correct request schema or a successful login. |
| POST | `/api/v2/login` | Found in portal JavaScript | Candidate v2 login route; not confirmed end-to-end. |
| — | OTP-related routes | OTP flow found in portal JavaScript | Exact route names, payloads and response schema need re-capture. |
| — | Logout route | Found in portal JavaScript | Exact method and response need re-capture. |
| — | User-related routes | Found in portal JavaScript | Exact paths and access scope need re-capture. |

Fields previously seen or inferred for the login flow include `mykad`, `katalaluan` and `spotme_device_id`. Treat these as **unconfirmed request fields** until matched against a real, authorized browser request. Never put a real MyKad, password, OTP or bearer token in this document, issue tracker, terminal transcript or test fixture.

## Read-only data

| Method | Path | Evidence | Notes |
|---|---|---|---|
| GET | `/api/checking` | Previously called successfully | Historical response indicated setup/eligibility flags such as organization, organization location, home location, supervisor and working hours. Exact schema should be captured again. |
| GET | `/api/harian?tarikh=YYYY-MM-DD` | Previously called successfully | Historical test for 2026-11-10 returned 7 movement-related records. Observed fields included record ID, user ID, time, longitude, latitude, reason, created/updated metadata and attendance ID. |
| GET | `/api/dashboard-harian/{tahun}/{bulan}/{userId}` | Found in portal JavaScript | Candidate monthly dashboard route; not verified against a live response. |

Earlier investigation notes indicate that some read requests require an `Authorization: Bearer` token. The exact token acquisition, lifetime, refresh behavior and permission scope are not documented here.

## Write operations

No check-in, check-out or movement-write endpoint has been verified in this repository. Do not guess endpoint names, payloads, headers or transaction semantics. Do not automate submission of official attendance or movement records based only on frontend route names.

## Required capture before integration

For each route intended for read-only integration, record:

1. Exact HTTP method and path (redact query values that contain personal data).
2. Request headers, excluding cookies, authorization values and device/session secrets.
3. Request body schema with all personal values replaced by placeholders.
4. HTTP status and sanitized response shape.
5. Whether the request works with the user's authorized account and whether it is permitted for this client.
6. Date, portal version/build and capture source (Network tab or JavaScript bundle).

Store no credentials, OTPs, bearer tokens, cookies, MyKad numbers, coordinates or raw personal records in Git.

## Current CLI implementation status

The current `spotme/api.py` contains a prototype for `POST /api/login`, `GET /api/checking` and `GET /api/harian`. It is not integrated into the CLI's Run System flow. Its login payload/token parsing is provisional and must not be described as confirmed. The scheduler currently generates local reminders/context only; it does not submit attendance or movement records.
