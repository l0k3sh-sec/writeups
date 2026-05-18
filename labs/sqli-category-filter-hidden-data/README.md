# SQL Injection Vulnerability in WHERE Clause — Retrieving Hidden Data

**Difficulty:** Apprentice | **Category:** SQL Injection

Retrieve hidden/unreleased products by injecting into the `category` parameter of the product filter.

---

I started by visiting the target site and exploring the product filter. The shop had category links — Accessories, Clothing, Food & Drink, Pets, etc. I clicked on **Pets** and captured that request in Burp Suite's HTTP history, then sent it to the Repeater.

The original request looked like this:

```
GET /filter?category=Pets HTTP/2
```

My first move was to test if the parameter was injectable and see what `'--` would do — the single quote breaks out of the string literal, and the `--` comments out everything after it, essentially stripping any extra conditions the query had (like `AND released = 1`). I modified the request to:

```
GET /filter?category=Pets'-- HTTP/2
```

The response returned one extra product that wasn't showing up before — so the injection was working and there were hidden products in the database. But the lab needed me to dump *all* products across all categories, visible and hidden.

So I upgraded the payload to `OR 1=1--`:

```
GET /filter?category=Pets'+OR+1=1-- HTTP/2
```

That solved it. The response came back with **20 products** total — where normally only 12 were visible. The lab was marked solved.

The SQL logic behind this: the backend was probably running something like:

```sql
SELECT * FROM products WHERE category = 'Pets' AND released = 1
```

When I injected `' OR 1=1--`, it became:

```sql
SELECT * FROM products WHERE category = 'Pets' OR 1=1--' AND released = 1
```

The `'` broke out of the string. `OR 1=1` made the WHERE clause always true — so every row in the table matched, regardless of category or release status. The `--` commented out the `AND released = 1` part completely, exposing everything.

**Key takeaway:** SQL injection in a filter parameter can bypass both category filtering and release status checks in a single payload. The `OR 1=1--` pattern works because it doesn't just bypass one condition — it makes the entire WHERE clause unconditionally true.
