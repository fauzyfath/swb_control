import time
import cv2
from gpiozero import MotionSensor, DistanceSensor, AngularServo, LED
from datetime import datetime
from LoRaF import SX126X
from classifcation_system import *


# Lora Setup
def SetupLoRA():
    lora = SX126X()
    return

# Pir Function
def objectDetection():
    
    pir = MotionSensor(4)
    
    while True:
        if pir.motion_detected:
            print('Motion Detected\nActivate System')
            time.sleep(2)
            return True
        else:
            print('No Motion\nSystem Deactivate')
            return False

#ultrasonic function        
def distanceDetection():
    sensors = [
        DistanceSensor(echo=23, trigger=24, max_distance=1, threshold_distance=0.2), #first compartment
        DistanceSensor(echo=25, trigger=26, max_distance=1, threshold_distance=0.2), #second compartment
    ]
    
    leds = [
        LED(5),  # LED for the first compartment
        LED(6),  # LED for the second compartment
    ]
    
    while True:
        distances = [sensor.distance for sensor in sensors] 
        print(f"Distances: {[f'{distance:.2f} m' for distance in distances]}")
        
        compartments_full = []
        
        for i, (distance, sensor, led) in enumerate(zip(distances, sensors, leds)):
            if distance >= sensor.max_distance:
                led.on()
                compartments_full.append(True)
                print(f"Compartment {i+1} is full")
            else:
                led.off()
                compartments_full.append(False)
        
        if all(compartments_full):
            message = "All compartments are full"
            # send_lora_message(lora, message)
            # print("All compartments are full. Sent message via LoRa.")
        
        # time.sleep(1)  # Adjust as needed for how often you want to check distance

#camera function   
def takePicture(base_path = '/img_dir/'):

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    
    try:
        time.sleep(2)  # Let the camera warm up

        ret, frame = cap.read()
        if not ret:
            raise IOError('Failed to capture image')
        
        timeStamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = f'{base_path}capture_image_{timeStamp}.jpg'
        
        cv2.imwrite(image_path,frame)

        return image_path
    
    finally:  
        cap.release()

#Servo function
def segregate_valve(predicted_class):
    servo = AngularServo(17, min_angle=-90, max_angle=90)

    if predicted_class in ['paper', 'plastic','cardboard', 'trash']:
        CombustibleMessage = print("combustible is recognize\nopen valve door to combustible compartment")
        # send_lora_message(lora,CombustibleMessage)
        servo.angle = -90
        time.sleep(2)
        servo.angle = 0
    else:
        print("non-combustible is recognize\nopen valve door to non-combustible compartment")
        servo.angle = -90
        time.sleep(2)
        servo.angle = 0

if __name__ == "__main__":
    try:
        while True:
            if objectDetection():
                time.sleep(1) #prepare the system
                image_path = takePicture()
                prediction_class = predict_image(image_path)
                print(f"Predicted Object: {prediction_class}")
                segregate_valve(prediction_class)
                distanceDetection()
            else:
                time.sleep(1)  # Adjust sleep time as needed
            
    except KeyboardInterrupt:
        print("\nMeasurement stopped by user.")