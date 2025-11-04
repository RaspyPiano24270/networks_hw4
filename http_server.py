# --- 1. Import Necessary Modules ---                                                                       <- Section 1
import sys
import socket
import os

# --- 2. Define Helper Functions ---                                                                        <- Section 2

# Take raw request data and extracts the essential parts, specifically:
#          1) The requested file path
#          2) The HTTP method
#          3) The 'User-Agent' header
def parse_request(request_data):
    lines = request_data.splitlines()
    if not lines:
        return None, None, None

    # Parse the request line: e.g., "GET /index.html HTTP/1.0"
    parts = lines[0].split()
    if len(parts) < 2:
        return None, None, None

    method = parts[0]
    path = parts[1]

    # Extract User-Agent header if available
    user_agent = None
    for line in lines:
        if line.lower().startswith("user-agent:"):
            user_agent = line.split(":", 1)[1].strip()
            break

    return method, path, user_agent

# Based on the file extension (e.g., .html, .png, .pdf), determine the correct
#          Content-Type string for the HTTP response header. (Q2 in README)
def get_content_type(file_path):
    extension_map = {
        ".html": "text/html",
        ".htm": "text/html",
        ".txt": "text/plain",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".css": "text/css",
        ".js": "application/javascript",
        ".pdf": "application/pdf",
    }

    for ext, content_type in extension_map.items():
        if file_path.endswith(ext):
            return content_type
    return "application/octet-stream"

# Construct the complete HTTP response message, including headers and the body.
#          Handles Success and Failure cases
def build_response(status_code, content_type=None, body=None):
    reasons = {
        200: "OK",
        403: "Forbidden",
        404: "Not Found",
    }

    reason = reasons.get(status_code, "Unknown")
    response = f"HTTP/1.0 {status_code} {reason}\r\n"

    if content_type:
        response += f"Content-Type: {content_type}\r\n"

    response += "\r\n"  # End of headers

    if body:
        if isinstance(body, str):
            body = body.encode()
        return response.encode() + body
    else:
        return response.encode()


# --- 3. Client Connection Handler ---                                                                      <- Section 3

def handle_client(client_socket):
    try:
        # 1. Read Request: Read all incoming data from the 'client_socket'.
        request_data = client_socket.recv(1024).decode()
        if not request_data:
            return
        
        # 2. Print Debug Info: Print the inbound request message.
        print("----- Incoming Request -----")
        print(request_data)

        # 3. Parse Request: Call 'parse_request' to get the requested file path and User-Agent.
        method, path, user_agent = parse_request(request_data)
        if not method or not path:
            return
        
        # 4. Security Check: If the browser is not allowed, send a 403 response
        if user_agent and "curl" in user_agent.lower():
            body = "<html><body><h1>403 Forbidden</h1></body></html>"
            response = build_response(403, "text/html", body)
            client_socket.sendall(response)
            return
        
        # 5. File Handling:
        #    a. Check if the file exists on the server's file system
        #    b. If the file doesn't exist, build and send a 404 Not Found response.
        #    c. If the file exist, read its binary content.
        if path == "/":
            path = "/index.html"

        file_path = "." + path  # Serve from current directory

        #6. Builds and sends response
        if not os.path.isfile(file_path):
            body = "<html><body><h1>404 Not Found</h1></body></html>"
            response = build_response(404, "text/html", body)
            client_socket.sendall(response)
            return

        # File exists
        with open(file_path, "rb") as f:
            content = f.read()

        content_type = get_content_type(file_path)
        response = build_response(200, content_type, content)
        client_socket.sendall(response)

    except Exception as e:
        print(f"Error handling client: {e}")

    finally:
        # 7. Close Connection
        client_socket.close()


# --- 4. Main Server Loop ---  <- Section 4
# Initialize the server and keeps it running indefinitely.
def main():
    # 1. Argument Check: Verify the command was run correctly (e.g., `./http_server -p 20001`).
    if len(sys.argv) != 3 or sys.argv[1] != "-p":
        print(f"Usage: {sys.argv[0]} -p <port>")
        sys.exit(1)

    port = int(sys.argv[2])

    # 2. Socket Creation: Create a TCP socket (`socket.socket(socket.AF_INET, socket.SOCK_STREAM)`).
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 3. Bind and Listen: Bind the socket to the specified port and start listening for incoming connections.
    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"HTTP Server running on http://localhost:{port}/")

    # 4. Infinite Loop: Start a `while True:` loop to handle connections sequentially (per **Requirement 132**).
    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"Connected: {client_addr}")
            handle_client(client_socket)

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        server_socket.close()

# --- 5. Execution Block ---                                                                                <- Section 5
if __name__ == "__main__":
    main()