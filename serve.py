#!/usr/bin/env python3
"""
HandBoard HTTPS Server
Serves the project over HTTPS so phone cameras work.
"""
import http.server, ssl, socket, os, subprocess, sys

PORT = 8443
CERT = os.path.join(os.path.dirname(__file__), 'cert.pem')
KEY  = os.path.join(os.path.dirname(__file__), 'key.pem')

# Auto-detect LAN IP
def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

ip = get_lan_ip()

# Update config.js with current IP + port
config_path = os.path.join(os.path.dirname(__file__), 'config.js')
with open(config_path, 'w') as f:
    f.write(f"window.HANDBOARD_IP = '{ip}'; window.HANDBOARD_PORT = '{PORT}';")
print(f"✦ config.js updated: {ip}:{PORT}")

# Generate cert if missing
if not os.path.exists(CERT) or not os.path.exists(KEY):
    print("✦ Generating self-signed SSL certificate...")
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
        '-keyout', KEY, '-out', CERT, '-days', '365',
        '-nodes', '-subj', f'/CN={ip}'
    ], check=True)

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

handler = http.server.SimpleHTTPRequestHandler
server  = http.server.HTTPServer(('0.0.0.0', PORT), handler)

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(CERT, KEY)
server.socket = ctx.wrap_socket(server.socket, server_side=True)

print(f"\n  ┌─ HandBoard HTTPS Server ─────────────────────┐")
print(f"  │                                              │")
print(f"  │  PC browser :  https://localhost:{PORT}       │")
print(f"  │  QR page    :  https://localhost:{PORT}/qr.html │")
print(f"  │  Phone URL  :  https://{ip}:{PORT}     │")
print(f"  │                                              │")
print(f"  │  ⚠  On phone: tap 'Advanced' → 'Proceed'   │")
print(f"  │     to bypass the self-signed cert warning  │")
print(f"  │                                              │")
print(f"  └──────────────────────────────────────────────┘\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n✦ Server stopped.")
