
import urllib.request
import socket
import time
import multiprocessing
import json
import math
from shifter import Shifter
from urllib.parse import unquote_plus  
from Stepper_Lab8_3 import Stepper
from RPi import GPIO

#Initial variable and pin setup
GPIO.setmode(GPIO.BCM)

power = False
laser_state = False
theta_deg = 0.0
phi_deg = 0.0
calib_theta_deg = 0.0
calib_phi_deg = 0.0

laser_pin = 15
GPIO.setup(laser_pin, GPIO.OUT, initial=GPIO.LOW)

# Stepper Motor Setup
Stepper.shifter_outputs = multiprocessing.Value('i')

s = Shifter(data=17,latch=27,clock=22)   # set up Shifter

lock1 = multiprocessing.Lock()
lock2 = multiprocessing.Lock()

m1 = Stepper(s, lock1)
m2 = Stepper(s, lock2)


m1.zero()
m2.zero()


def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4
    data = data[idx:]
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            key = key_val[0]
            value = unquote_plus(key_val[1])
            data_dict[key] = value
    return data_dict


def get_json(url):
  with urllib.request.urlopen(url) as val:
    raw_response = val.read()
    text_response = raw_response.decode("utf-8")
    return text_response
    ##return json.loads(text_response)


def web_page(): # Creating the webpage with HTML code
    global theta_deg, phi_deg, calib_theta_deg, calib_phi_deg

    html = f"""
    <html>
  <head>
    <meta charset="UTF-8" />
    <title>Stepper Motor Turret Control</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        max-width: 650px;
        margin: 20px auto;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: #f9f9f9;
      }}

      h1 {{
        text-align: center;
        font-size: 1.4rem;
        margin-bottom: 20px;
      }}

      .section {{
        margin-bottom: 20px;
        padding: 10px 15px;
        background: #ffffff;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
      }}

      .section-title {{
        font-weight: bold;
        margin-bottom: 8px;
      }}

      .switch-wrapper {{
        display: flex;
        align-items: center;
        gap: 10px;
      }}

      .switch {{
        position: relative;
        display: inline-block;
        width: 50px;
        height: 24px;
      }}

      .switch input {{
        opacity: 0;
        width: 0;
        height: 0;
      }}

      .slider {{
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: 0.2s;
        border-radius: 24px;
      }}

      .slider:before {{
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 0.2s;
        border-radius: 50%;
      }}

      input:checked + .slider {{
        background-color: #4caf50;
      }}

      input:checked + .slider:before {{
        transform: translateX(26px);
      }}

      .slider-label {{
        font-size: 0.95rem;
      }}

      .control-row {{
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 10px;
      }}

      .control-row span {{
        min-width: 120px;
        font-size: 0.95rem;
      }}

      input[type="range"] {{
        flex: 1;
      }}

      #calibrateBtn {{
        width: 100%;
        padding: 8px 0;
        border: none;
        border-radius: 4px;
        background-color: #1976d2;
        color: white;
        font-size: 0.95rem;
        cursor: pointer;
      }}

      #calibrateBtn:hover {{
        background-color: #145ca3;
      }}

      .launch-row {{
        display: flex;
        flex-direction: column;
        gap: 8px;
      }}

      #json_url {{
        width: 100%;
        padding: 6px 8px;
        border-radius: 4px;
        border: 1px solid #ccc;
        font-size: 0.9rem;
      }}

      #launchBtn {{
        margin-top: 6px;
        width: 100%;
        padding: 12px 0;
        border: none;
        border-radius: 6px;
        background-color: #d32f2f;
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: bold;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 1px;
      }}

      #launchBtn:hover {{
        background-color: #b71c1c;
      }}
    </style>
  </head>

  <body>
    <h1>Stepper Motor Turret Control</h1>

    <!-- Power Section -->
    <div class="section">
      <div class="section-title">Power</div>
      <div class="switch-wrapper">
        <span class="slider-label">Stepper Power</span>
        <label class="switch">
          <input type="checkbox" id="powerSwitch" />
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <!-- Laser Control Section -->
    <div class="section">
      <div class="section-title">Laser</div>
      <div class="switch-wrapper">
        <span class="slider-label">Laser Enable</span>
        <label class="switch">
          <input type="checkbox" id="laserSwitch" />
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <!-- Angle Control Section -->
    <div class="section">
      <div class="section-title">Turret Angles</div>

      <div class="control-row">
        <span>Horizontal Angle (θ)</span>
        <input type="range" id="theta_angle" min="0" max="360" value="0" />
        <span id="theta_value">0°</span>
      </div>

      <div class="control-row">
        <span>Vertical Angle (φ)</span>
        <input type="range" id="phi_angle" min="0" max="360" value="0" />
        <span id="phi_value">0°</span>
      </div>
    </div>

    <!-- Calibration Section -->
    <div class="section">
      <div class="section-title">Calibration</div>
      <p>Current Calibration:</p>
      <p>
        θ₀ = {calib_theta_deg:.1f}° <br>
        φ₀ = {calib_phi_deg:.1f}°
      </p>

      <button id="calibrateBtn">Set Calibration</button>
    </div>

    <!-- Automated Targeting Section -->
    <div class="section">
      <div class="section-title">Automated Targeting</div>
      <div class="launch-row">
        <label for="json_url">JSON File URL</label>
        <input
          type="text"
          id="json_url"
          placeholder="input here"
        />
        <button id="launchBtn">LAUNCH</button>
      </div>
    </div>

    <script>
      function sendControl(control, value) {{
        const body = new URLSearchParams({{ control, value }}).toString();
        fetch("/", {{
          method: "POST",
          headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
          body,
        }}).catch(() => {{}});
      }}

      // Power
      document.getElementById("powerSwitch").addEventListener("change", (e) => {{
        sendControl("power", e.target.checked ? "on" : "off");
      }});

      // Laser ON / OFF
      document.getElementById("laserSwitch").addEventListener("change", (e) => {{
        sendControl("laser", e.target.checked ? "on" : "off");
      }});

      // θ angle
      const theta = document.getElementById("theta_angle");
      const thetaLabel = document.getElementById("theta_value");

      // Update display live while sliding
      theta.addEventListener("input", () => {{
          thetaLabel.textContent = theta.value + "°";
      }});

      // Only send command when slider is released
      theta.addEventListener("change", () => {{
          sendControl("theta", theta.value);
      }});

      // φ angle
      const phi = document.getElementById("phi_angle");
      const phiLabel = document.getElementById("phi_value");

      phi.addEventListener("input", () => {{
          phiLabel.textContent = phi.value + "°";
      }});

      // Only send command when slider is released
      phi.addEventListener("change", () => {{
          sendControl("phi", phi.value);
      }});


      // Calibration uses current θ and φ
      document.getElementById("calibrateBtn").addEventListener("click", () => {{
        sendControl("calib_theta", theta.value);
        sendControl("calib_phi", phi.value);
        alert("Calibration set to θ = " + theta.value + "°, φ = " + phi.value + "°");
      }});

      // Automated Launch
      document.getElementById("launchBtn").addEventListener("click", () => {{
        const url = document.getElementById("json_url").value.trim();
        if (!url) {{
          alert("Enter a JSON URL first.");
          return;
        }}
        sendControl("launch", url);
      }});
    </script>
  </body>
</html>
    """
    return html.encode('utf-8')

# Method for receiving a connection and parsing the data from the connection (website)
def serve_web_page():

    global power, laser_state, theta_deg, phi_deg
    global calib_theta_deg, calib_phi_deg

    while True:

        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept() 
        print(f'Connection from {client_ip} on client port {client_port}')
        client_message = conn.recv(4096).decode('utf-8')
        print(f'Message from client:\n{client_message}')
        data_dict = parsePOSTdata(client_message)

        if 'control' in data_dict and 'value' in data_dict:
            control = data_dict.get('control')
            value = data_dict.get('value')
            print(f"Control: {control}, Value: {value}")

            if control == "power":
                if value =="on":
                    print(">>> Power On")
                    power = True
                else:
                    print("Power Off")
                    power = False

            elif control == "theta":
                theta_deg = float(value)
                print(f" Set horizontal angle to {theta_deg} deg")

                if power == True:
                  m1.goAngle(theta_deg)

            elif control == "phi":
                phi_deg = float(value)
                print(f"Set vertical angle (phi) to {phi_deg} deg")
                
                if power == True:
                  m2.goAngle(phi_deg)

            elif control == "calib_theta":
                calib_theta_deg = float(value)
                print(f" Calibration theta set to {calib_theta_deg} deg")
                #store as z axis roation offset

            elif control == "calib_phi":
                calib_phi_deg = float(value)
                print(f" Calibration phi set to {calib_phi_deg} deg")
                #store as z axis roation offset

            elif control == "launch":
                json_url = value.strip()
                
                json_text = get_json(json_url)

                data = json.loads(json_text)

                turret_number_list = []
                turret_r_list = []
                turret_theta_list = []
                turret_dict = {}

                for turret_number, turret_data in data["turrets"].items():
                  turret_number_list.append(int(turret_number))
                  turret_r_list.append(turret_data["r"])
                  turret_theta_list.append(turret_data["theta"])
                  turret_dict[int(turret_number)] = turret_data

                globes_r = []
                globes_theta = []
                globes_z = []
                globes_list = []

                for globe in data["globes"]:
                  globes_r.append(globe["r"])
                  globes_theta.append(globe["theta"])
                  globes_z.append(globe["z"])
                  globes_list.append(globe)

                print("\n==== PARSED JSON DATA ====")

                print("\n--- TURRETS ---")
                print("IDs:", turret_number_list)
                print("r values:", turret_r_list)
                print("theta values:", turret_theta_list)

                print("\n--- GLOBES ---")
                print("r values:", globes_r)
                print("theta values:", globes_theta)
                print("z values:", globes_z)
                
                if power == False:
                  print("Power is OFF")
                else:
                  while power == True:
                    for tid, theta_rad in zip(turret_number_list, turret_theta_list):
                      theta_deg_target = math.degrees(theta_rad)

                      m1.goAngle(theta_deg_target)

                      GPIO.output(laser_pin, GPIO.HIGH)
                      time.sleep(3.0)
                      GPIO.output(laser_pin, GPIO.LOW)
                      time.sleep(0.5)

                    for i, (r, theta_rad, z) in enumerate(zip(globes_r, globes_theta, globes_z)):
                      theta_deg_target = math.degrees(theta_rad)
                      phi_deg_target = math.degrees(math.atan2(z,r))

                      m1.goAngle(theta_deg_target)
                      m2.goAngle(phi_deg_target)

                      GPIO.output(laser_pin, GPIO.HIGH)
                      time.sleep(3)
                      GPIO.output(laser_pin, GPIO.LOW)
                      time.sleep(0.5)




            elif control == "laser":
              laser_state = (value == "on")
              if laser_state == True:
                GPIO.output(laser_pin, GPIO.HIGH)
              else:
                GPIO.output(laser_pin, GPIO.LOW)

            else:
                print("Unknown control:", control)

        conn.send(b'HTTP/1.1 200 OK\r\n')                 
        conn.send(b'Content-Type: text/html\r\n')         
        conn.send(b'Connection: close\r\n\r\n')   
        conn.sendall(web_page())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Set up socket connection
s.bind(('', 80))
s.listen(1)

serve_web_page()







