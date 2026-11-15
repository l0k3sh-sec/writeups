# CTF Writeup: Secret Box

- *Platform:* CyLab / picoCTF 2026
- *Difficulty:* Medium
- *Category:* Web Exploitation
- *Vulnerability/Concept:* SQL Injection (stacked queries) → content hijack via UPDATE

Read the provided source code and confirmed
- **app/src/server.js** — the /secrets/create handler builds its query with a raw template literal: 
```javascript
const query = await db . raw ( `INSERT INTO secrets(owner_id, content) VALUES (' ${ userId } ', ' ${ content } ')` ) ; 
```
Every other query in the app uses ? placeholders — this one line is the only unparameterized one.
- **db/initdb.sql** — admin's user row is hardcoded: `id = 'e2a66f7d-2ce6-4861-b4aa-be8e069601cb'`.
- **db.js** — on startup, overwrites admin's secret content with `process.env.FLAG`. So the flag's exact location (table + row) is known with zero recon: `secrets where owner_id = 'e2a66f7d-...'`.
- **/** route runs a *safe, parameterized* `SELECT * FROM secrets WHERE owner_id = ?` filled with the current user's own id — this is the only thing standing between "my secrets" and "everyone's secrets."

As always first, clicked through every possible buttons on web and found /secrets/create where a user can store an secret content which is not visible to other users. and goal was to get content of admin.
In response of this same request noticed that web-server uses stack "postgres/MySQL/mongo" to store content from response header X-Powered-By: Express (already confirmed this from reading source code)

Probed the content field with a single ' (quote) as a fingerprint test. Logic: if the app safely parameterizes/escapes input, a stray quote gets neutralized and nothing breaks. If the app concatenates raw input into SQL, the quote "escapes the box" and corrupts the query grammar, resulting in conformation of SQL in usage.

Sent content='OR=1 → got a *500 Internal Server Error* , and the error page echoed the *entire* final SQL statement back, including the stack trace naming pg-protocol — confirming Postgres as the engine and confirming string-context injection. Including my owner ID (96046b2e-791d-415f-a9f9-b8574f793432)

Upon confirming unsanitized input at content filed i wrote this SQL String 
```sql
'); UPDATE secrets SET owner_id='96046b2e-791d-415f-a9f9-b8574f793432' WHERE owner_id='e2a66f7d-2ce6-4861-b4aa-be8e069601cb'; --'
```

How Payload works:
To execute the attack, we inject a payload that breaks out of the original INSERT statement using `');`, executes an UPDATE command, and ends with a `--` comment to neutralize the application's residual closing characters and prevent a syntax error. The injected UPDATE successfully reassigns ownership of the admin's secret to our own UUID, satisfying the database's foreign-key constraints because our user actually exists. As a result, when we visit the homepage, the application's secure, parameterized SELECT query fetches and displays the flag for us, as our account is now its legitimate owner in the database. Note that this multi-statement injection (stacked queries) relies on the Postgres driver operating in "simple mode," which allows multiple semicolon-separated commands to run at once, rather than the stricter prepared statement mode.

in reponse of using this payload in content field i got 302 means my payload worked and upon visiting the secret as a user i got to know secret of admin and solved the CTF.

flag: academy{sq1_1nject10n_a6e12f86}
