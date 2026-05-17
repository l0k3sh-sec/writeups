# Lab: Basic SSRF Against the Local Server

**Difficulty:** Apprentice | **Category:** SSRF

The lab has a stock check feature that fetches data from an internal system. 
The goal was to access the admin interface at `http://localhost/admin` and delete carlos.

I opened the site and immediately went to the stock check feature. I captured 
the request in Burp Suite's HTTP history — it was a POST request with a vulnerable 
parameter `stockApi` that controlled which URL the server fetches:
'stockApi=http%3A%2F%[2Fstock.weliketoshop.net](http://2fstock.weliketoshop.net/)%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D1%26storeId%3D1'
'stockApi=http://stock.weliketoshop.net:8080/product/stock/check?productId=1&storeId=1'<--Decoded
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/fe34f737-cb06-4f4a-b9c7-dc8f87557704" />

Sent it to Repeater and replaced the value with:
'stockApi=http://localhost/admin/delete?username=carlos'
<img width="1915" height="1079" alt="image" src="https://github.com/user-attachments/assets/fb53c363-6135-4e1f-b42b-6df76f22b009" />

The server fetched it internally on my behalf — carlos got deleted. Done.

**Key takeaway:** No validation on the `stockApi` parameter, and the admin panel 
automatically trusted requests coming from localhost. Classic SSRF.

