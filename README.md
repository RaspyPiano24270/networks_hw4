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

2. How do you prevent the clients from opening more connections once they have opened the maximum number of connections?

3. Report the times and speedup for concurrent fetch of the URLs in testcase 1 and 2 with the stock http server.

4. Report the times and speedup for concurrent fetch of the URLs in testcase 1 and 2 with your http_server_conc. Are these numbers same as above? Why or why not?

## ✅ Author

CSCI 4406 — HW4  
Eric Gerner & Julian Spindola / Team 1
