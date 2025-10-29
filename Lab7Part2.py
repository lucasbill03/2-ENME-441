import socket
import RPi.GPIO as GPIO

LED_PINS = {"LED1":17, "LED2":27, "LED3":22}
pwms = {}

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

for key, value in LED_PINS.items():
    obj = GPIO.PWM(value, 500)
    obj.start(0)
    pwms[key] = obj

brightness = [0, 0, 0]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 80))
s.listen(1)

def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4
    if idx < 4:
        return data_dict
    data = data[idx:]
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

def web_page():
    html = """
    <html>
    <head><title>LED Control - Part 2</title></head>
    <body>
      <p>LED1: <input type="range" id="LED1" min="0" max="100" value="0"></p>
      <p>LED2: <input type="range" id="LED2" min="0" max="100" value="0"></p>
      <p>LED3: <input type="range" id="LED3" min="0" max="100" value="0"></p>

      <script>
        function postValue(led, value) {
          const body = new URLSearchParams({ led: led, value: String(value) }).toString();
          fetch("/", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body
          }).catch(() => {});
        }

        ["LED1","LED2","LED3"].forEach(id => {
          const el = document.getElementById(id);
          el.addEventListener("input", () => postValue(id, el.value));
        });
      </script>
    </body>
    </html>
    """
    return bytes(html, 'utf-8')

def serve_web_page():
    while True:
        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept()     # blocking call

        print(f'Connection from {client_ip} on client port {client_port}')
        client_message = conn.recv(2048).decode('utf-8', errors='ignore')
        print(f'Message from client:\n{client_message}')
        data_dict = parsePOSTdata(client_message)

        led = data_dict.get("led", "")
        val = data_dict.get("value", "0")

        if led in LED_PINS and val.isdigit():
            duty = max(0, min(100, int(val)))
            pwms[led].ChangeDutyCycle(duty)

        conn.send(b'HTTP/1.1 200 OK\r\n')
        conn.send(b'Content-Type: text/html\r\n')
        conn.send(b'Connection: close\r\n\r\n')
        conn.sendall(web_page())


serve_web_page()
for x in pwms.values():
    x.ChangeDutyCycle(0)
    x.stop()
GPIO.cleanup()