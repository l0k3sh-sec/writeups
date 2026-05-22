# Lab: URL-Based Access Control Can Be Circumvented

**Difficulty:** Practitioner | **Category:** Access Control

The goal was to bypass access control restrictions on the admin panel and delete the user `carlos` using the `X-Original-URL` custom header.

The application was blocking direct access to admin functionality even with an admin account — requests to `/admin` returned a forbidden response. The hint was in the lab itself: the `X-Original-URL` header can be used to override the URL the backend routes to, while the frontend only sees the request line.

Captured a request in Burp Suite and sent it to Repeater. Added the `X-Original-URL` header, but noticed it kept getting lowercased automatically — that's because the request was using HTTP/2, which enforces lowercase headers by spec. Switched the HTTP version to HTTP/1.1, which preserves header casing.

With that fixed, sent:

```

GET / HTTP/1.1

X-Original-URL: /admin

```

The server returned the admin panel response, which included this in the HTML:

![image.png](attachment:13fad131-ecd5-411a-94bc-e5f7122a14c0:image.png)

```html

<a href="/admin/delete?username=carlos">

```

This confirmed `carlos` exists and revealed the exact deletion endpoint. The key insight here was understanding how the request was being processed — the frontend validates the request line (`GET /`) and blocks anything containing `/admin` there, while the backend routes based on `X-Original-URL`. This means the query parameters need to stay in the request line, and the path goes in the header.

Sent the final payload:

```

GET /?username=carlos HTTP/1.1

X-Original-URL: /admin/delete

```

![image.png](attachment:13fad131-ecd5-411a-94bc-e5f7122a14c0:image.png)

The frontend saw `GET /` — a normal request — and allowed it through. The backend routed to `/admin/delete` via the custom header and picked up `?username=carlos` from the request line. Carlos was deleted — lab solved.

**Key takeaway:** The frontend and backend were processing different parts of the request. By keeping the sensitive path in `X-Original-URL` and the query parameters in the request line, it was possible to bypass frontend access controls entirely while still passing the required parameters to the backend.

## Mitigation

Access control decisions should never be made solely on the frontend based on the request line. The backend should enforce its own access control checks regardless of what headers are present. Custom headers like `X-Original-URL` and `X-Rewrite-URL` should be stripped or ignored unless explicitly required, and privileged endpoints should validate the authenticated user's role server-side on every request.
