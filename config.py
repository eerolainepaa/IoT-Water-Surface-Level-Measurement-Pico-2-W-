# config_server.py – puhdas konfigurointipalvelin
import network
import socket
import time
import machine

AP_SSID = "PicoConfig"
AP_PASSWORD = "password"
AP_IP = "192.168.4.1"
CONFIG_FILE = "wlan_config.txt"

def url_decode(s):
    s = s.replace('+', ' ')
    i = 0
    result = ""
    while i < len(s):
        if s[i] == '%' and i+2 < len(s):
            try:
                result += chr(int(s[i+1:i+3], 16))
                i += 3
                continue
            except:
                pass
        result += s[i]
        i += 1
    return result

def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    print(f"AP running: {AP_SSID} – go to http://{AP_IP}")

def save_and_reboot(ssid, password):
    with open(CONFIG_FILE, "w") as f:
        f.write(ssid + "\n" + password + "\n")
    print("Credentials saved – rebooting...")
    time.sleep(2)
    machine.reset()

def web_page():
    return """<html><head><title>Pico W Configuration</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta charset="utf-8">
                </head>
                <body>
                  <h1>Pico W WLAN Configuration</h1>
                  <form action="/save" method="post">
                	<label for="ssid">Network name (SSID):</label><br>
                	<input type="text" id="ssid" name="ssid" required><br><br>
                	<label for="password">Password:</label><br>
                	<input type="password" id="password" name="password"><br><br>
                	<label for="url">Server URL:</label><br>
                	<input type="text" id="url" name="url"><br><br>
                	<input type="submit" value="Save and reset">
                  </form>
                </body></html>"""

# --- Start AP and server ---
setup_ap()
s = socket.socket()
s.bind(('', 80))
s.listen(1)

print("Configuration server online - awaiting for connection...")

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()

    if "POST" in request:
        body = request.split("\r\n\r\n", 1)[1]
        params = {}
        for part in body.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k] = url_decode(v)
        if "ssid" in params:
            save_and_reboot(params["ssid"], params.get("password", ""))
        response = "HTTP/1.1 200 OK\r\n\r\n<h2>Saved! Rebooting...</h2>"
    else:
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + web_page()

    conn.send(response)
    conn.close()
