#=============================================================================//
# Project                - CompanionCare: Empowering Independence
# Author                 - https://www.hackster.io/maheshyadav216
# Hardware               - UNIHIKER, M5StickC Plus, XIAO ESP32S3       
# Sensors                - Fermion BLE Sensor Beacon
# Software               - Arduino IDE, PlatformIO
# GitHub Repo of Project - https://github.com/maheshyadav216/Project-CompanionCare-Empowering-Independence 
# Code last Modified on  - 24/08/2024
# Code/Content license   - (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
#============================================================================//

# Project code for UNIHIKER
# This is Main Controller Device, attached to Lanyard and to be worn around 
# neck by person with special needs
# Assistive technologies for people with disabilities

# With this device person can locate, track their important items like -
# medicine bag, Walking stick, Keychain etc. if misplaced in house
# But before that **Special Tag Devices should be permanantly attached to 
# these daily use important items/things

# This device can be used by person with limmited movement (physically)
# Using Touchscreen panel
# Peoples with Partial/full Visual impairments can also use this device 
# by use of Voice commands - Like, "Hello Robot" "Find my medicine bag"
# CompanionCare system will find that device location and display on screen,
# as well as Announce its location on speaker. Send Buzzer signal to Tag device

import time
from pinpong.board import Board, Pin
from pinpong.extension.unihiker import *
from unihiker import GUI
import paho.mqtt.client as mqtt
import threading
from DFRobot_DF2301Q import *
from unihiker import Audio  # Import the Audio module from the unihiker package

# MQTT settings
broker = "192.168.0.107"
port = 1883
topic_subscribe_medicine_bag = "home/medicine_bag"
topic_subscribe_keychain = "home/keychain"
topic_publish_medbag_buzzer = "home/UNIHIKER/medbag_buzzer"
topic_publish_keychain_buzzer = "home/UNIHIKER/keychain_buzzer"
topic_publish_careTaker_buzzer = "home/UNIHIKER/caretaker_buzzer"
topic_publish_careTaker_fallAlert = "home/UNIHIKER/caretaker_fallAlert"

username = "siot"
password = "dfrobot"

# Initialize the UNIHIKER
Board().begin()

# Instantiate the GUI class
gui = GUI()

# Instantiate the Audio class
audio = Audio()  

# Initialize location variables
medicine_bag_location = "Unknown"
keychain_location = "Unknown"

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(username, password)

# The callback for when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic_subscribe_medicine_bag)
        client.subscribe(topic_subscribe_keychain)
    else:
        print(f"Failed to connect, return code {rc}")

# The callback for when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    global medicine_bag_location, keychain_location
    message = msg.payload.decode()
    if msg.topic == topic_subscribe_medicine_bag:
        medicine_bag_location = message
    elif msg.topic == topic_subscribe_keychain:
        keychain_location = message
    print(f"Message received from {msg.topic}: {message}")

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT Broker...")
client.connect(broker, port, 60)

# Publish a message to a specific topic
def publish_message(topic, message):
    print(f"Publishing message to {topic}: {message}")
    client.publish(topic, message)

# Start the MQTT loop in a separate thread
def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

# Function to process voice Assistant Response
def asstResponseMBE(str):
    # lets process 
    if (medicine_bag_location == "Unknown"):
        audio.play('MB-NoSignal-E.mp3')
    if (medicine_bag_location == "Bedroom"):
        audio.play('MB-bed-E.mp3')
    if (medicine_bag_location == "Kitchen"):
        audio.play('MB-Kit-E.mp3')
    if (medicine_bag_location == "Living Room"):
        audio.play('MB-LR-E.mp3')
    if (medicine_bag_location == "Office"):
        audio.play('MB-Off-E.mp3')

# Function to process voice Assistant Response
def asstResponseMBH(str):
    # lets process 
    if (medicine_bag_location == "Unknown"):
        audio.play('MB-NoSignal-H.mp3')
    if (medicine_bag_location == "Bedroom"):
        audio.play('MB-bed-H.mp3')
    if (medicine_bag_location == "Kitchen"):
        audio.play('MB-Kit-H.mp3')
    if (medicine_bag_location == "Living Room"):
        audio.play('MB-LR-H.mp3')
    if (medicine_bag_location == "Office"):
        audio.play('MB-Off-H.mp3')

# Function to process voice Assistant Response
def asstResponseKE(str):
    # lets process 
    if (medicine_bag_location == "Unknown"):
        audio.play('key-NoSignal-E.mp3')
    if (medicine_bag_location == "Bedroom"):
        audio.play('key-bed-E.mp3')
    if (medicine_bag_location == "Kitchen"):
        audio.play('key-kit-E.mp3')
    if (medicine_bag_location == "Living Room"):
        audio.play('key-LR-E.mp3')
    if (medicine_bag_location == "Office"):
        audio.play('key-Off-E.mp3')

# Function to process voice Assistant Response
def asstResponseKH(str):
    # lets process 
    if (medicine_bag_location == "Unknown"):
        audio.play('key-NoSignal-H.mp3')
    if (medicine_bag_location == "Bedroom"):
        audio.play('key-bed-H.mp3')
    if (medicine_bag_location == "Kitchen"):
        audio.play('key-kit-H.mp3')
    if (medicine_bag_location == "Living Room"):
        audio.play('key-LR-H.mp3')
    if (medicine_bag_location == "Office"):
        audio.play('key-Off-H.mp3')


# DF2301Q device handling
DF2301Q = DFRobot_DF2301Q_I2C()
DF2301Q.set_volume(12)
DF2301Q.set_mute_mode(0)
DF2301Q.set_wake_time(5)

def df2301q_thread():
    print("DF2301Q Thread Started")
    while True:
        DF2301Q_CMDID = DF2301Q.get_CMDID()
        time.sleep(0.05)
        if not DF2301Q_CMDID == 0:
            if (DF2301Q_CMDID==5):
                btclick(1)
                asstResponseMBE(medicine_bag_location)
            if (DF2301Q_CMDID==6):
                btclick(3)
                asstResponseMBE(medicine_bag_location)            
            if (DF2301Q_CMDID==7 or DF2301Q_CMDID==20):
                btclick(1)
                asstResponseMBH(medicine_bag_location)
            if (DF2301Q_CMDID==8):
                btclick(3)
                asstResponseMBH(medicine_bag_location)
            if (DF2301Q_CMDID==9):
                btclick(2)
                asstResponseKE(keychain_location)
            if (DF2301Q_CMDID==10):
                btclick(4)
                asstResponseKE(keychain_location)
            if (DF2301Q_CMDID==11 or DF2301Q_CMDID==21):
                btclick(2)
                asstResponseKH(keychain_location)
            if (DF2301Q_CMDID==12):
                btclick(4)
                asstResponseKH(keychain_location)
            if (DF2301Q_CMDID==13):
                btclick(2)
                asstResponseKH(keychain_location)
            if (DF2301Q_CMDID==14):
                btclick(4)
                asstResponseKH(keychain_location)            
            if (DF2301Q_CMDID==15 or DF2301Q_CMDID==16 or DF2301Q_CMDID==17 or DF2301Q_CMDID==18 or DF2301Q_CMDID==19):
                btclick(5)

df2301q_thread = threading.Thread(target=df2301q_thread)
df2301q_thread.start()

# Fall detection in a separate thread
def fall_detection_thread():
    print("Fall Detection Thread Started")
    while True:
        Ax = accelerometer.get_x() / 16384.0
        Ay = accelerometer.get_y() / 16384.0
        Az = accelerometer.get_z() / 16384.0

        Gx = gyroscope.get_x() / 131.0
        Gy = gyroscope.get_y() / 131.0
        Gz = gyroscope.get_z() / 131.0

        x = Ax * Ax
        y = Ay * Ay
        z = Az * Az
        acc = x + y + z
        a = acc ** 0.5 * 10000

        if a < 1:
            fall = False
        elif a > 1:
            fall = True
            publish_message(topic_publish_careTaker_fallAlert, "Fall Alert")
            buzzer.play(buzzer.POWER_DOWN, buzzer.Once)

        time.sleep(0.5)

fall_detection_thread = threading.Thread(target=fall_detection_thread)
fall_detection_thread.start()


# Button Press Alert Detection thread
def button_monitor_thread():
    print("Button Monitor thread started")
    while True:
        # Check if button A is pressed
        if (button_a.is_pressed() == True) or (button_b.is_pressed() == True): 
            btclick(5)

button_monitor_thread = threading.Thread(target=button_monitor_thread)
button_monitor_thread.start()


# Define button click handlers
def btclick(data):
    if data == 1:
        gui.fill_rect(x=20, y=280, w=199, h=34, color="green")
        gui.draw_text(text=f"Medicine Bag is in: {medicine_bag_location}", x=120, y=300, font_size=10, origin="center", color="black")
    elif data == 2:
        gui.fill_rect(x=20, y=280, w=199, h=34, color="green")
        gui.draw_text(text=f"Keys are in: {keychain_location}", x=120, y=300, font_size=10, origin="center", color="black")
    elif data == 3:
        gui.fill_rect(x=20, y=280, w=199, h=34, color="green")
        gui.draw_text(text=f"Medicine Bag is in: {medicine_bag_location}", x=120, y=300, font_size=10, origin="center", color="black")
        publish_message(topic_publish_medbag_buzzer, "Buzzer: Medicine Bag")
    elif data == 4:
        publish_message(topic_publish_keychain_buzzer, "Buzzer: Keychain")
        gui.fill_rect(x=20, y=280, w=199, h=34, color="green")
        gui.draw_text(text=f"Keys are in: {keychain_location}", x=120, y=300, font_size=10, origin="center", color="black")
    elif data == 5:
        publish_message(topic_publish_careTaker_buzzer, "Buzzer: SOS Alert")
        gui.fill_rect(x=20, y=280, w=199, h=34, color="red"), 
        gui.draw_text(text="SOS Alert Sent !!", x=120, y=300, font_size=10, origin="center", color="white")
    print(data)

# GUI setup
gui.fill_rect(x=0, y=0, w=240, h=320, color="cyan", onclick=lambda: gui.fill_rect(x=20, y=280, w=199, h=34, color="cyan"))
gui.fill_circle(x=120, y=40, r=35, color="red", onclick=lambda: print("fill circle clicked"))
gui.draw_circle(x=120, y=40, r=35, width=5, color="yellow", onclick=lambda: print("Out circle clicked"))
gui.draw_rect(x=20, y=280, w=200, h=35, width=2, color=(255, 0, 0), onclick=lambda: print("rect clicked"))
gui.draw_text(text="SOS", x=120, y=40, font_size=16, origin="center", color="white", onclick=lambda: btclick(5))
txt2 = gui.draw_text(text="", x=120, y=300, font_size=10, origin="center", color="black")

# Add buttons
gui.add_button(x=120, y=100, w=200, h=30, text="Find Medicine Bag", origin='center', onclick=lambda: btclick(1))
gui.add_button(x=120, y=150, w=200, h=30, text="Find Keys", origin='center', onclick=lambda: btclick(2))
gui.add_button(x=120, y=200, w=200, h=30, text="Buzzer: Medicine Bag", origin='center', onclick=lambda: btclick(3))
gui.add_button(x=120, y=250, w=200, h=30, text="Buzzer: Keychain", origin='center', onclick=lambda: btclick(4))

while True:
    time.sleep(1)


#=============================== hackster.io/maheshyadav216 ======================================================#