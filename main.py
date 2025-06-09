#!/usr/bin/env python3

"""
Smart Pest Detection System using Raspberry Pi, Edge Impulse, and Blynk
Author: Engr. Psalmol
"""

import device_patches  # Jetson Nano patches (keep for compatibility)
import cv2
import os
import sys, getopt
import signal
import time
import RPi.GPIO as GPIO
from edge_impulse_linux.image import ImageImpulseRunner

runner = None
show_camera = True

# Disable camera preview in headless mode
if sys.platform == 'linux' and not os.environ.get('DISPLAY'):
    show_camera = False

def now():
    return round(time.time() * 1000)

def get_webcams():
    """Detect available camera ports."""
    port_ids = []
    for port in range(5):
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print(f"Camera {backendName} ({h} x {w}) found in port {port}")
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted. Cleaning up...')
    if runner:
        runner.stop()
    GPIO.cleanup()
    sys.exit(0)

# Register interrupt handler
signal.signal(signal.SIGINT, sigint_handler)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)     # Trigger input
GPIO.setup(27, GPIO.OUT)    # Output to buzzer or alert LED
GPIO.output(27, GPIO.LOW)

def help():
    print('Usage: python3 main.py <model.eim> [camera_id]')

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, _ in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]
    modelfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), model)
    print(f'Loading model: {modelfile}')

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print(f'Loaded model: {model_info["project"]["owner"]} / {model_info["project"]["name"]}')
            labels = model_info['model_parameters']['labels']

            if len(args) >= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if not port_ids:
                    raise Exception("No camera found.")
                if len(port_ids) > 1:
                    raise Exception("Multiple cameras found. Specify port ID.")
                videoCaptureDeviceId = port_ids[0]

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if not ret:
                raise Exception("Camera init failed.")
            camera.release()

            next_frame = 0

            # Start real-time classification
            for res, img in runner.classifier(videoCaptureDeviceId):
                if next_frame > now():
                    time.sleep((next_frame - now()) / 1000)

                if "classification" in res["result"]:
                    print('Classification results:', end=' ')
                    for label in labels:
                        score = res['result']['classification'][label]
                        print(f'{label}: {score:.2f}', end='\t')
                    print('', flush=True)

                elif "bounding_boxes" in res["result"]:
                    print(f'Found {len(res["result"]["bounding_boxes"])} bounding boxes')
                    for bb in res["result"]["bounding_boxes"]:
                        print(f'\t{bb["label"]} ({bb["value"]:.2f}): x={bb["x"]} y={bb["y"]} w={bb["width"]} h={bb["height"]}')
                        
                        if bb['label'] == "Grasshopper" and bb['value'] >= 0.70:
                            print("\n[ALERT] Grasshopper detected!")
                            GPIO.output(27, GPIO.HIGH)
                            time.sleep(5)
                            GPIO.output(27, GPIO.LOW)

                        img = cv2.rectangle(
                            img,
                            (bb['x'], bb['y']),
                            (bb['x'] + bb['width'], bb['y'] + bb['height']),
                            (255, 0, 0), 1
                        )

                if show_camera:
                    cv2.imshow('Smart Pest Detection', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) == ord('q'):
                        break

                next_frame = now() + 100

        finally:
            if runner:
                runner.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
