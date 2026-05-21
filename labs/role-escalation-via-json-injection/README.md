Vulnerability: User role can be modified via JSON body parameter injection in the change-email endpoint. The server accepts and processes unvalidated fields in the request body, allowing a low-privilege user to escalate their role to admin.
Steps to Reproduce:

Log in as a regular user (wiener:peter)
Navigate to account settings and trigger a change-email request
Intercept the POST request to /my-account/change-email in Burp Suite
The original request body:

`json{"email":"wiener1@normal-user.net"}`

Add roleid as an integer field to the JSON body:

`json{
  "email": "wiener1@normal-user.net",
  "roleid": 2
}`

Forward the request
Navigate to /admin — admin access is now granted
Send the following request to delete carlos:

`GET /admin/delete?username=carlos HTTP/2`
Result: Regular user account was escalated to admin role. Admin panel became accessible and user carlos was deleted successfully.

Impact: Any authenticated user can escalate privileges to administrator level by injecting the roleid field into the change-email request body. Full admin panel access is achieved.


Mitigation: Server should whitelist accepted JSON fields and ignore or reject any unrecognized parameters. Role assignment should never be controlled by user-supplied input.
