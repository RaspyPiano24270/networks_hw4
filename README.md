CSCI 4406 – HW4: Concurrent Connection HTTP Server
Team: <teamid>
Members: <names>
Instructor: Zechun Cao
Due: Nov 5, 2025

Build & Run (Server)
--------------------
gcc -O2 -pthread -Wall -Wextra -o http_server_conc http_server_conc.c
./http_server_conc -p <port> -maxclient <N> -maxtotal <M>

Example:
./http_server_conc -p 20001 -maxclient 10 -maxtotal 64

Design Summary
--------------
Concurrency: fixed thread pool + blocking I/O + bounded job queue.
Limits: system-wide cap (maxtotal) and per-client cap (maxclient).
On accept, we pre-read HTTP headers (3s timeout), derive a client_key, and
atomically increment that client’s open-connection counter. If over the
per-client cap -> respond 429 Too Many Requests and close. If over maxtotal
-> 503 Service Unavailable and close. We serve files from the current
working directory. Responses use "Connection: close".

Unique Client Identification
----------------------------
Priority order:
1) "X-App-Id" header (preferred if the client sends it on every request).
2) Cookie "AppId=..." (server can set on first request; client echoes back).
3) Fallback: (remote IP, User-Agent) tuple.

This distinguishes multiple apps behind one IP (NAT) better than IP alone.
Since we don’t know app identity at TCP accept time, we pre-read headers
to decide.

Preventing Over-Limit Connections
---------------------------------
- Per client: accept -> pre-read headers -> build client_key -> ++count.
  If count > maxclient: send 429, close, then --count.
- System-wide: if current_total_open >= maxtotal at accept/queue boundaries:
  send 503, close. Counters decrement on every connection close.

http_client.py (Provided Minimal Client)
----------------------------------------
File: http_client.py (Python 3)

How to run:
    chmod +x http_client.py
    ./http_client.py -u <URL> -o <output file name> -v

Key flags:
  -u / --url         URL to download (http:// or https://)
  -o / --output      Output file path
  -v / --verbose     Print request and response headers
  --insecure         Skip TLS certificate verification (HTTPS)
  --follow           Follow one redirect (3xx with Location)

Notes:
- The client uses HTTP/1.0 with "Connection: close", which is fine for our
  throughput experiments (we are measuring the effect of concurrency, not
  keep-alive).
- HTTPS works; use --insecure in lab environments with self-signed certs.

(Optional) Send X-App-Id from our client
----------------------------------------
To ensure our per-client cap uses application identity (not IP/UA fallback),
we can add one header in http_client.py:

In build_request(...), insert this line before the blank terminator:

    f"X-App-Id: <teamid-or-uuid>",

For example:

def build_request(host, path, user_agent="CSCI4406-HTTP-Client/1.0"):
    lines = [
        f"GET {path} HTTP/1.0",
        f"Host: {host}",
        f"User-Agent: {user_agent}",
        "Accept: */*",
        "X-App-Id: <teamid-or-uuid>",
        "Connection: close",
        "", ""
    ]
    return CRLF.join(lines).encode("ascii")

If you prefer not to modify the client, the server’s fallback (IP, User-Agent)
still enforces a reasonable per-client limit.

Test Inputs (Instructor URLs)
-----------------------------
- Script 1: https://zechuncao.com/teaching/csci4406/testfiles/testscript1.txt
- Script 2: https://zechuncao.com/teaching/csci4406/testfiles/testscript2.txt

(Download these two text files into your working directory before testing.)

Benchmarking with Our Client (Stock Server)
-------------------------------------------
We measure sequential vs concurrent (10 connections) fetch using our
http_client.py. Because the client downloads a single URL per process, we
use xargs to run 10 parallel client processes.

1) Sequential (1 connection total):
   While reading each URL line, we derive an output filename and run one
   client at a time.

# testscript1.txt -> sequential
while read -r u; do
  base="$(basename "$u")"
  ./http_client.py -u "$u" -o "seq1_$base"
done < testscript1.txt

# testscript2.txt -> sequential
while read -r u; do
  base="$(basename "$u")"
  ./http_client.py -u "$u" -o "seq2_$base"
done < testscript2.txt

(Optionally time them)
 /usr/bin/time -f "elapsed=%E" bash -c 'while read -r u; do base="$(basename "$u")"; ./http_client.py -u "$u" -o "seq1_$base"; done < testscript1.txt'

2) Concurrent (10 parallel client processes):
   We use xargs -P10 to launch ten downloads at once.

# testscript1.txt -> 10-way parallel
cat testscript1.txt | awk '{print $0"\tpar1_"$0}' | \
  xargs -n2 -P10 bash -c './http_client.py -u "$0" -o "$1"' 

# testscript2.txt -> 10-way parallel
cat testscript2.txt | awk '{print $0"\tpar2_"$0}' | \
  xargs -n2 -P10 bash -c './http_client.py -u "$0" -o "$1"'

(Optionally time them)
 /usr/bin/time -f "elapsed=%E" bash -c 'cat testscript1.txt | awk '\''{print $0"\tpar1_"$0}'\'' | xargs -n2 -P10 bash -c '\''./http_client.py -u "$0" -o "$1"'\'''

Compute speedup:  Speedup = T_sequential / T_parallel

Benchmarking with Our Server (Local Hosting)
--------------------------------------------
1) Place the same test files (from the instructor tarballs) into the directory
   where you start the server (so GET /path maps to local files).

2) Start server with a per-client cap of 10:
   ./http_server_conc -p 20001 -maxclient 10 -maxtotal 64

3) Convert the instructor test scripts to local URLs (one-time transform):

# For script1 (public URLs -> localhost URLs)
sed -E 's~https?://[^/]+~http://localhost:20001~' testscript1.txt > testscript1_local.txt
sed -E 's~https?://[^/]+~http://localhost:20001~' testscript2.txt > testscript2_local.txt

4) Run the same sequential vs parallel experiments against localhost:

# Sequential (script1_local)
while read -r u; do
  base="$(basename "$u")"
  ./http_client.py -u "$u" -o "loc_seq1_$base"
done < testscript1_local.txt

# 10-way parallel (script1_local)
cat testscript1_local.txt | awk '{print $0"\tloc_par1_"$0}' | \
  xargs -n2 -P10 bash -c './http_client.py -u "$0" -o "$1"'

Repeat for script2_local. Time these runs and compute speedup.

Q&A (Fill These for Submission)
-------------------------------

Q1) What is your strategy for identifying unique clients?
    - Primary: "X-App-Id" header if sent by the client.
    - Secondary: Cookie "AppId=..." set by server and echoed by client.
    - Fallback: (remote IP, User-Agent) tuple.
    Rationale: Distinguishes multiple apps behind one NAT and the same app
    across changing IPs; implemented via a header pre-read after accept.

Q2) How do you prevent clients from opening more than the maximum connections?
    - On new connection: accept -> pre-read headers -> derive client_key ->
      atomically increment per-client counter. If counter > -maxclient:
      respond 429 Too Many Requests and close; decrement afterwards.
    - If system-wide current_total_open >= -maxtotal: respond 503 Service
      Unavailable and close. All counters decrement on connection close,
      guaranteed in worker teardown paths.

Q3) Report times and speedup for concurrent fetch of testcase 1 and 2
    with the STOCK http server (public URLs).
    - testcase1: T_seq = ______ ; T_par(10) = ______ ; Speedup = ______
    - testcase2: T_seq = ______ ; T_par(10) = ______ ; Speedup = ______
    (Measured with http_client.py; parallel via xargs -P10.)

Q4) Report times and speedup for concurrent fetch of testcase 1 and 2
    with our http_server_conc (localhost).
    - testcase1: T_seq = ______ ; T_par(10) = ______ ; Speedup = ______
    - testcase2: T_seq = ______ ; T_par(10) = ______ ; Speedup = ______

    Are these the same as above? Why or why not?
    - They typically differ because localhost removes WAN latency and
      bandwidth variability; disk caching may benefit repeated reads;
      our server’s implementation details (thread count, sendfile,
      header timeout) also affect overhead. Public servers may enforce
      their own per-host connection limits and have different I/O stacks,
      changing parallel efficiency.

Limitations / Notes
-------------------
- Minimal HTTP/1.1 handling; we serve GET with "Connection: close".
- Header pre-read timeout = 3s to avoid resource hoarding by idle clients.
- Fallback identity (IP, User-Agent) may over/under-count in shared/rare
  UA scenarios if X-App-Id is not used.
- Tested on Linux; uses sendfile when available.

References
----------
- Steve Souders, “Roundup on Parallel Connections”, context for why parallel
  connections improve perceived load times.
- curl manual (if you choose to compare/validate with curl’s --parallel),
  but our grading uses the provided http_client.py runs above.

