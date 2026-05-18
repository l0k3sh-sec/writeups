# Lab: SSRF Against Another Backend System

**Difficulty:** Apprentice | **Category:** SSRF

The goal was to scan the internal network range `192.168.0.X`, find a hidden admin 
interface running on port `8080`, and delete carlos.

Opened the site, went to the stock check feature and captured the POST request in 
Burp Suite's HTTP history. Sent it to Repeater — the `stockApi` parameter was the 
vulnerable input controlling which URL the server fetches internally.

The lab hinted the admin panel lives somewhere in the `192.168.0.0/24` range on 
port `8080`, but the exact IP was unknown. Manually trying all 256 values wasn't 
realistic, so I used **Burp Intruder** with a Sniper attack. Modified the `stockApi` 
parameter and tagged the last octet:
`stockApi=http://192.168.0.§X§:8080/admin`

Set the payload type to **Numbers** (0–255) and launched the attack. Most responses 
came back `500` or `404`, but one hit returned `200 OK` — that was the admin panel 
at `192.168.0.205`.

Took that IP back to Repeater and fired:
`stockApi=http://192.168.0.205:8080/admin/delete?username=carlos`
Server processed it internally — carlos deleted. Lab done.

**Key takeaway:** The server made requests to any internal IP I gave it with zero 
validation. Combined with Intruder, you can enumerate the entire internal network 
through a single SSRF parameter.

