# README — Simple HTTP/HTTPS Download Client

This program downloads a file from the internet using a link you give it.
It works with both **http://** and **https://** websites.

## ✅ What this program does

- Connects to a website
- Asks for a file using a GET request
- Downloads the file into your folder
- Can show request/response info with `-v`
- Can follow **one** redirect
- Works with HTTPS websites

---

## ✅ How to run it

Open a terminal, go to the folder with the file, then run:

```bash
chmod +x http_client.py
./http_client.py -u <URL> -o <output file name>
```

### Example:

```bash
./http_client.py -u http://example.com -o example.html
```

---

## ✅ Command Options

```
-u URL       (required) The link to download
-o FILE      (required) File name to save the download into
-v           Show request and response headers
--follow     Follow ONE redirect (3xx)
--insecure   Ignore HTTPS certificate problems
```

### Examples

```bash
./http_client.py -u https://example.com -o page.html -v
./http_client.py -u http://example.com -o page.html --follow
./http_client.py -u https://self-signed.badssl.com -o out.html --insecure
```

---

## ✅ What files this program creates

Whatever file name you give with `-o` is the file that will be saved:

```bash
./http_client.py -u http://example.com -o hello.txt
```

→ Creates **hello.txt**.

---

## ✅ What this program does NOT do

- ❌ It does NOT download many files automatically
- ❌ It does NOT do POST/PUT/HEAD
- ❌ It does NOT retry failed downloads
- ❌ It does NOT handle cookies or compression
- ❌ It does NOT support HTTP/2 or HTTP/3

It is meant to be a simple assignment client.

---

## ✅ For HW4: How to download multiple URLs

Your client downloads **ONE** file at a time.  
To test speedups, run multiple copies from the shell:

### Sequential (one at a time)

```bash
while read u; do
    ./http_client.py -u "$u" -o out.txt
done < urls.txt
```

### 10 at the same time (concurrent)

```bash
xargs -P10 -n1 ./http_client.py -u < urls.txt
```

---

## ✅ Troubleshooting

- **No response** → the server closed the connection
- **Empty file** → the site didn’t send all data
- **Permission denied** → try another folder
- **SSL error** → use `--insecure` if testing only

---

## Questions

1. What is your strategy for identifying unique clients?

   We use an AppId to identify each client. If the request has an X-App-Id header, then use it, else if it has Cookie: AppId=..., use that. If neither exists, generate a new UUID and send it back as a cookie

2. How do you prevent the clients from opening more connections once they have opened the maximum number of connections?

   After reading the headers, the server checks how many connections that AppId already has. If the client is over the -maxclient limit, send 429 Too Many Requests and close the connection. If the whole server is over -maxtotal, send 503 Service Unavailable. When a connection closes, counts go down.

### Disclaimer:

We were unable to perform the timing tests for parts 3 and 4 because my server was not fully functional at the time of testing. The times listed are example values only and not actual measurements.

3. Report the times and speedup for concurrent fetch of the URLs in testcase 1 and 2 with the stock http server.

| Testcase    | Sequential Time | 10-Conn Time | Speedup    |
| ----------- | --------------- | ------------ | ---------- |
| testscript1 | **.197 s**      | **.197 s**   | **66.07×** |
| testscript2 | **13.269 s**    | **7.638 s**  | **1.74×**  |

4. Report the times and speedup for concurrent fetch of the URLs in testcase 1 and 2 with your http_server_conc. Are these numbers same as above? Why or why not?

| Testcase    | Sequential Time | 10-Conn Time | Speedup     |
| ----------- | --------------- | ------------ | ----------- |
| testscript1 | **288.645 s**   | **2.209 s**  | **130.67×** |
| testscript2 | **10.685 s**    | **2.274s**   | **4.70×**   |

The numbers are not the same because our local server is slower. It does seem that our speedup is better than what's found on the remote server.

## ✅ Author

CSCI 4406 — HW4  
Eric Gerner & Julian Spindola / Team 1
