Logged in on vulnerable platform provided by CTF using pre-provided credentials

after logging in a text popped up 
```Access level: Guest (ID: 3000). Insufficient privileges to view classified data. Only top-tier users can access the flag.```

understood that the our logged-in session is not privileged enough. Understood have to somehow find or make own account privileged enough to access the flag

noticed Guest (ID: 3000), and then gone to check how request/response looks like in burpsuite to get some clue about what 
```Guest (ID: 3000)``` is?

found nothing related to Guest (ID: 3000) in request... then noticed weird string in request 
```GET /profile/user/e93028bdc1aacdfb3687181f2031765d HTTP/1.1```

scanned weird string using hash-identifier tool and found out that its a MD5 hashed string(32-char hex) 

used MD5 Lookup tool and confirmed ```MD5("3000") = e93028bdc1aacdfb3687181f2031765d```

From previous context from site ```Access level: Guest (ID: 3000). Insufficient privileges to view classified data. Only top-tier users can access the flag.``` confirming the ID is the thing being hashed, and that privilege is tied to ID value

it was hinted in CTF that there are 20 employees on platform so guessed that admin/staff accounts were likely assigned low sequential IDs (1–20ish) while guest/customer accounts started at a higher round number (3000+) **either 0-20 or 3000+-20**

wrote a simple python script to perform attack and test my hypothesis using turbo intruder
```
import hashlib

def md5(s):
    return hashlib.md5(str(s).encode()).hexdigest()

def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                            concurrentConnections=5)

    for uid in range(___, ___):   # <- your actual range goes here
        h = md5(uid)
        engine.queue(target.req, h)

def handleResponse(req, interesting):
    table.add(req)
```
code explaination:
imported hashlib library 
encrypted each ID number with MD5 gave it UID range 0-20 and 3000+-20
filtered interesting requests/responses

Ran the attack and reviewed responses — looked for any response that didn’t say “Guest” / “Insufficient privileges”, which would indicate a hit on a staff/admin ID and looked for 200ok response other than my own account

Found the admin ID, got the flag — successfully landed on an admin-level profile and captured the flag
<img width="785" height="81" alt="image" src="https://github.com/user-attachments/assets/d984da30-2ff0-4097-bd97-408e5d1ee759" />
