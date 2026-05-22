# URL-Based Access Control Bypass via X-Original-URL Header

## Lab Details

| Field      | Info                              |
|------------|-----------------------------------|
| Platform   | PortSwigger Web Security Academy  |
| Category   | Access Control                    |
| Difficulty | Practitioner                      |
| Vulnerability | Frontend Access Control Bypass via Custom Headers |

---

## Objective

I already had admin credentials and could log in, but the server was blocking me from accessing any actual admin functionality — specifically deleting the user carlos. The goal was to bypass that restriction and perform the delete action.

---

## Initial Recon

Since I already had access to the account, the issue wasn't authentication — it was authorization at the routing level. Requesting `/admin` directly returned a `403 Forbidden`, which meant the frontend was intercepting and blocking access before the request even reached the backend logic.

The lab instructions specifically mentioned the `X-Original-URL` header, so I knew that was the intended attack surface. The hypothesis was that while the frontend was enforcing the block, the backend might still trust and process this custom rewrite header — routing me internally to whatever path I supplied in it.

---

## Hypothesis

The frontend proxy was performing path-based access control, but the backend application was separately processing the `X-Original-URL` header to determine where to route the request. If the backend trusted this header without verifying frontend-level restrictions, I could use it to access protected routes by keeping the main request line clean.

---

## Testing Process

### Problem: HTTP/2 Lowercasing the Header

The first thing I ran into was that my header `X-Original-URL` kept getting converted to `x-original-url` (all lowercase). This matters because I wasn't sure if the backend was doing a case-sensitive header lookup.

After some research I figured out the reason — my request was using **HTTP/2**, which by spec enforces lowercase header names. The header name wasn't being modified by anything malicious; that's just how HTTP/2 works.

**Fix:** I manually downgraded the request to **HTTP/1.1**, which allows mixed-case headers. After that, `X-Original-URL` stayed exactly as written.

This was actually important because the lab instructions specifically mentioned `X-Original-URL` by that exact name, so I suspected the backend was doing a case-sensitive match.

---

## Exploitation

### Step 1 — Confirming the bypass works

I sent:

```http
GET / HTTP/1.1
Host: TARGET
X-Original-URL: /admin
```

The server responded with `200 OK` and returned the admin panel HTML, including this link:

```html
<a href="/admin/delete?username=carlos">
```

The frontend allowed the request because the request line only said `GET /`. The backend used the `X-Original-URL` value to route me internally to `/admin`. Bypass confirmed.

---

### Step 2 — Attempting to delete carlos (failed attempts)

Now I needed to actually hit `/admin/delete?username=carlos`. This is where it got interesting because the obvious payloads didn't work.

**Attempt A — Putting everything in the header**

```http
GET / HTTP/1.1
X-Original-URL: /admin/delete?username=carlos
```

Result: `404 Not Found`

The backend parsed the entire header value as the path, including the query string. It tried to find a route literally named `/admin/delete?username=carlos` — and since query parameters aren't valid in route paths, it found nothing.

---

**Attempt B — Query in request line, path in header**

```http
GET /admin?username=carlos HTTP/1.1
X-Original-URL: /admin/delete
```

Result: `403 Forbidden`

The frontend saw `/admin` in the request line and blocked it immediately. The backend never even saw the request. The frontend's path check was based on what was in the request line, not the header.

---

**Attempt C — Reversed logic**

```http
GET /delete HTTP/1.1
X-Original-URL: /admin?username=carlos
```

Result: `200 OK` — but no deletion happened.

This was the most interesting failed attempt. The frontend allowed `/delete` in the request line (oddly), and the backend routed me to `/admin` via the header. I successfully reached the admin panel again. But `/admin` is just a dashboard — it doesn't have the deletion logic. I was in the right building, wrong room.

---

### Step 3 — The working payload

After mapping out what the frontend and backend were each checking, the logic became clear:

- **Frontend** checks: the request line path. It blocks anything containing `/admin`.
- **Backend** routes: based on `X-Original-URL`. It processes query parameters from the **request line**, not the header value.

So the correct split was:

- Request line: keep it clean (`/`), but attach the query parameter here
- Header: provide only the clean path (`/admin/delete`)

```http
GET /?username=carlos HTTP/1.1
Host: TARGET
X-Original-URL: /admin/delete
```

The frontend saw `GET /` — nothing suspicious, request passed through. The backend took `X-Original-URL: /admin/delete` as the route and merged `?username=carlos` from the request line into it. Carlos was deleted.

---

## Why This Works

The application had a **split trust model** — the frontend proxy and the backend application each enforced access control independently, but they didn't share the same logic.

- The frontend proxy blocked access based on the **request line path**
- The backend application trusted the **`X-Original-URL` header** to determine the actual route
- Query parameters were pulled from the **request line**, not the header

Because the frontend never inspected the `X-Original-URL` header, and the backend never re-validated the header value against frontend restrictions, I could supply a forbidden path through the header while keeping the request line completely clean. Neither layer caught the full picture.

---

## Real-World Impact

In a real application, this kind of misconfiguration could expose:

- Admin dashboards and management panels
- Internal APIs not meant to be externally accessible
- User management endpoints (create, delete, privilege escalation)
- Debug or diagnostic routes left enabled in production

The impact here is critical because it allows full admin functionality bypass with nothing more than a custom header. No exploitation of authentication, no advanced tooling required.

---

## Detection Methodology

**Behavioral clues that suggested this was exploitable:**
- Direct `/admin` access returned `403` even with valid credentials — indicating frontend-layer enforcement, not backend
- Lab instructions explicitly named `X-Original-URL` as the relevant header
- HTTP/2 was silently lowercasing my headers — a behavior that would mask the attack unless I understood why it was happening

**Headers worth testing in similar scenarios:**
- `X-Original-URL`
- `X-Rewrite-URL`
- `X-Forwarded-For`
- `X-Forwarded-Host`
- `X-Override-URL`

**Pattern to remember:** When a path is blocked at the proxy/frontend level but the app uses a reverse proxy, check whether the backend trusts upstream rewrite headers. The two layers enforcing rules independently is the vulnerability.

---

## Mitigation

- Never trust user-supplied rewrite headers (`X-Original-URL`, `X-Rewrite-URL`, etc.) — strip them at the proxy before forwarding
- Enforce authorization on the **backend**, not just at the frontend proxy layer
- Both layers should use the same consistent routing logic
- Access control decisions should be made after the full request is assembled, not split across layers

---

## Key Takeaways

- HTTP/2 enforces lowercase headers — if a header isn't working, check your HTTP version first
- Frontend access control alone is not sufficient; backend must independently enforce it too
- When a path is blocked, check if rewrite headers let you supply it a different way
- Query parameters and the routed path can come from different parts of the request — understanding this split is what makes the final payload work
- Mapping what each failed attempt tells you about the system is how you build the working payload, not guessing

**Tags:** `#access-control` `#portswigger` `#header-injection` `#x-original-url` `#proxy-bypass` `#practitioner`
