# Requirements — newpush-labs-template-server

> Canonical specification for the Portainer Template Server. This document is the primary source of truth for what needs to be built, tested, and maintained.

## 1. Project Overview

**newpush-labs-template-server** is a lightweight Python Flask application that acts as a dynamic Portainer template proxy. It fetches Portainer JSON template definitions from a remote URL, performs variable substitution based on query parameters, and returns the modified JSON. This enables environment-specific customization of Portainer templates (e.g., setting ingress domains, custom labels) without maintaining multiple static template files.

### Target Users

- NewPush Labs infrastructure administrators deploying services via Portainer
- DevOps engineers managing multi-environment Portainer deployments
- Developers cloning this template as a starting point for similar proxy services

### Deployment Model

- Deployed as a Procfile-based web service (Heroku, Railway, Render, or similar)
- Production server: Gunicorn WSGI
- Development server: Flask built-in server on port 8080

---

## 2. Core Functional Requirements

### FR-1: Template Fetching

| ID | Requirement | Status |
|----|-------------|--------|
| FR-1.1 | Accept a `portainer_template_url` query parameter pointing to a remote JSON template | Implemented |
| FR-1.2 | Fetch the JSON template via HTTP GET | Implemented |
| FR-1.3 | Append a random cache-busting query parameter to bypass upstream caches | Implemented |
| FR-1.4 | Return HTTP 400 if `portainer_template_url` is missing | Implemented |
| FR-1.5 | Return HTTP 500 with error details if the upstream fetch fails | Implemented |

### FR-2: Variable Substitution

| ID | Requirement | Status |
|----|-------------|--------|
| FR-2.1 | Accept arbitrary query parameters as key-value pairs for substitution | Implemented |
| FR-2.2 | Replace `{$key}` placeholders in the fetched JSON with the corresponding values | Implemented |
| FR-2.3 | Replace `${key}` placeholders in the fetched JSON with the corresponding values | Implemented |
| FR-2.4 | Process all query parameters (except `portainer_template_url` itself) as substitution variables | Implemented |
| FR-2.5 | Return the modified JSON with `Content-Type: application/json` | Implemented |

### FR-3: Health / Availability

| ID | Requirement | Status |
|----|-------------|--------|
| FR-3.1 | Provide a health-check endpoint (e.g., `GET /` or `GET /health`) returning HTTP 200 | Implemented |

---

## 3. Non-Functional Requirements

### NFR-1: Performance

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-1.1 | Respond within 5 seconds under normal upstream latency | Implemented (10s timeout) |
| NFR-1.2 | Support concurrent requests via Gunicorn worker processes | Implemented (Gunicorn) |

### NFR-2: Reliability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-2.1 | Gracefully handle upstream HTTP errors (4xx, 5xx) and return meaningful error messages | Implemented |
| NFR-2.2 | Gracefully handle network timeouts or connection failures to upstream | Implemented |

### NFR-3: Security

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-3.1 | Do not log or expose sensitive substitution values in production | Implemented (logging module, DEBUG-only values) |
| NFR-3.2 | Validate that `portainer_template_url` points to an allowed domain or URL scheme (HTTPS only) | Implemented |
| NFR-3.3 | Set a request timeout when fetching upstream templates to prevent hanging connections | Implemented (10s default, configurable) |

### NFR-4: Operability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-4.1 | Configurable listen port via `PORT` environment variable | Implemented |
| NFR-4.2 | Deployable via Procfile on PaaS platforms | Implemented |
| NFR-4.3 | All Python dependencies pinned to exact versions | Implemented |

### NFR-5: Maintainability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-5.1 | Codebase remains minimal and easy to understand (template project) | Implemented |
| NFR-5.2 | Automated test suite covering core functionality | Implemented (pytest) |
| NFR-5.3 | CI pipeline for linting and testing | Implemented (GitHub Actions) |

---

## 4. Integration Requirements

### IR-1: Portainer

| ID | Requirement | Status |
|----|-------------|--------|
| IR-1.1 | Output must be valid Portainer V2 template JSON | Implemented (pass-through) |
| IR-1.2 | Compatible with Portainer's custom template URL feature | Implemented |

### IR-2: Ingress / Traefik

| ID | Requirement | Status |
|----|-------------|--------|
| IR-2.1 | Support `TRAEFIK_INGRESS_DOMAIN` as a first-class substitution variable | Implemented |
| IR-2.2 | Template labels should integrate with Traefik for automatic routing | Implemented (via template content) |

---

## 5. API Reference

### `GET /modify`

Fetches a remote Portainer template JSON and performs variable substitution.

**Required Parameters:**

| Parameter | Description |
|-----------|-------------|
| `portainer_template_url` | URL of the remote Portainer JSON template to fetch |
| `TRAEFIK_INGRESS_DOMAIN` | Domain to substitute into Traefik ingress labels (conventionally required) |

**Optional Parameters:**

Any additional query parameter is treated as a substitution variable. Both `{$key}` and `${key}` placeholder formats are replaced.

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Modified JSON template returned successfully |
| 400 | Missing required `portainer_template_url` or `TRAEFIK_INGRESS_DOMAIN` parameter |
| 500 | Failed to fetch the upstream JSON template |

**Example:**

```
GET /modify?portainer_template_url=https://example.com/templates.json&TRAEFIK_INGRESS_DOMAIN=lab.example.com&CUSTOM_VAR=myvalue
```

---

## 6. Implementation Gaps & Roadmap

*All previously identified gaps have been addressed as of 2026-04-08:*

1. **Health-check endpoint (FR-3.1):** Add `GET /health` returning `{"status": "ok"}` for platform health checks and load balancer probes.

2. **Request timeout (NFR-3.3):** Add an explicit `timeout` parameter to the `requests.get()` call to prevent indefinite hangs when upstream is unresponsive.

3. **URL validation (NFR-3.2):** Validate that `portainer_template_url` uses HTTPS and optionally restrict to an allowlist of trusted domains.

4. **Production logging (NFR-3.1):** Replace `print()` statements with Python `logging` module; ensure sensitive substitution values are not logged at INFO level in production.

5. **Test suite (NFR-5.2):** Add pytest-based tests covering the `/modify` endpoint (happy path, missing params, upstream errors, variable substitution).

6. **CI pipeline (NFR-5.3):** Add GitHub Actions workflow for linting (`flake8` or `ruff`) and running tests on PR.

---

## 7. Acceptance Criteria

A pull request is considered complete when:

1. All "Implemented" requirements continue to pass (no regressions)
2. New code includes corresponding tests
3. `pip install -r requirements.txt && gunicorn app:app` starts without errors
4. Documentation (this file and README.md) is updated to reflect changes
5. PR targets the `develop` branch per the branching workflow
