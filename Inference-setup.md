# 🧠 Smart Agriculture Inference System – Setup & Deployment Notes

This file contains essential information to run pest detection inference using a Raspberry Pi and Edge Impulse.

---

## 💡 Overview

- Raspberry Pi runs a custom inference script to detect pests via a USB camera.
- When a pest (e.g., grasshopper) is detected, a GPIO pin is set **HIGH**.
- ESP32 reads this pin and updates the **Blynk IoT dashboard** alongside other agricultural sensor values.

---

## 🔁 Inference Model Files

Two models are available on the Raspberry Pi:

```
/home/pi/modelfile.eim          # More accurate, slightly higher inference time
/home/pi/modelfile_clean.eim    # Optimized for speed
```
# 🚀 Inference Script Execution (Via SSH)
Make sure the Raspberry Pi and host system are on the same network.
ssh pi@raspberrypi
# Password: [Hidden for GitHub – Ask Developer]

# To run inference manually:
python3 /home/pi/inference_script.py /home/pi/modelfile_clean.eim

# 🔃 Systemd Service (Auto Start on Boot)
The inference script is registered as a systemd service.
```
Manual Service Commands:
sudo systemctl start inference.service         # Start manually
sudo systemctl stop inference.service          # Stop service
sudo systemctl restart inference.service       # Restart (after code update)
sudo systemctl status inference.service        # Check status
sudo systemctl disable inference.service       # Disable auto-start
```
# Edge Impulse CLI Commands:
```
edge-impulse-linux                    # Connect Pi to Edge Impulse account
edge-impulse-linux-runner            # Run inference online (live)
edge-impulse-linux-runner --download modelfile.eim   # Download trained model
```
# 📡 Blynk & ESP32 Integration (Field Hardware)
ESP32 reads the pest detection line from Raspberry Pi via GPIO and publishes the result to Blynk.

## GPIO Mapping
Component	ESP32 GPIO  
RS485 TX	17  
RS485 RX	16  
RS485 DE/RE	18  
DS18B20 Temp Sensor	19  
Soil Moisture	21  
Water Pump	22  
Pest Detection In	23  

Blynk credentials, Wi-Fi SSID, and password are hidden for security.

🔐 Credentials
All credentials (Blynk Token, Wi-Fi SSID, password) are excluded from this file for GitHub security. See .ino file or contact developer if deploying.

# Maintained by: Engr. Psalmol
Email: akpsalmol@gmail.com  
LinkedIn: olalekan-samuel-akadiri
