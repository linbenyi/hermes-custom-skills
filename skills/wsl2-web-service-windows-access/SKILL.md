---
name: wsl2-web-service-windows-access
description: Access WSL2 web services (Flask/FastAPI) from Windows browser without localhost issues.
---
# WSL2 Flask Web Service Access from Windows

## Context
When running a Flask web service inside WSL2 (Windows Subsystem for Linux), Windows cannot access it via `localhost` or `127.0.0.1` because WSL2 uses a virtual network adapter with its own internal IP.

## The Problem
Flask starts on `0.0.0.0:5000` inside WSL2, but this binds to the WSL2 virtual adapter's IP, not the Windows host's loopback.

## The Solution
You must get the WSL2 IP address and access it from Windows browser, or set up a port proxy.

### Step 1: Get WSL2 IP
```bash
hostname -I | awk '{print $1}'
# Output: 172.x.x.x (e.g., 172.19.154.123)
```

### Step 2: Access from Windows
Open Windows browser (Chrome/Edge) and go to:
```
http://<WSL2_IP>:5000
# Example: http://172.19.154.123:5000
```

### Step 3: (Optional) Setup Permanent Port Proxy
If you want to use `localhost:5000` on Windows instead of the WSL2 IP, run this command in **Windows CMD or PowerShell (as Administrator)**:
```powershell
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=127.0.0.1 connectport=5000 connectaddress=<WSL2_IP>
```
*Replace `<WSL2_IP>` with the IP from Step 1.*

To remove it later:
```powershell
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=127.0.0.1
```

## Code Snippet for Flask/Dashboard
Ensure the Flask app binds to `0.0.0.0` to accept external connections.
```python
import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(f"Starting Dashboard at http://{ip}:5000")
app.run(host='0.0.0.0', port=5000)
```
