import argparse
import shutil
import base64
from datetime import datetime
import os
import cv2
import numpy as np
import socketio
import eventlet
import eventlet.wsgi
from PIL import Image
from flask import Flask
from io import BytesIO, StringIO
import json
import pickle
import matplotlib.image as mpimg
import time
from perception import perception_step
from decision import decision_step
from supporting_functions import update_rover, create_output_images

sio = socketio.Server()
app = Flask(__name__)


ground_truth = mpimg.imread('D:\Docs\projects\python\MarsRover\perception\map_bw.png')
ground_truth_3d = np.dstack((ground_truth*0, ground_truth*255, ground_truth*0)).astype(np.float)

class RoverState():
    def __init__(self):
        self.start_time = None 
        self.total_time = None 
        self.img = None
        self.vision_image = np.zeros((160, 320, 3), dtype=np.float) 
        
        # Rover properties
        self.start_pos = None
        self.pos = None 
        self.yaw = None 
        self.pitch = None
        self.roll = None 
        self.vel = None 
        self.steer = 0        
        self.throttle = 0 
        self.brake = 0 
        self.mode = 'start' 
        self.throttle_set = 0.2 
        self.brake_set = 10 
        
        # Maximum values
        self.max_vel = 3 
        self.max_pitch = 1
        self.max_roll = 1
        
        # Navigation
        self.nav_angles = None 
        self.nav_dists = None 
        self.stop_forward = 50
        self.go_forward = 400 
        self.stop_time = 0
        self.max_time = 2000
        self.p_pos = None
        
        # Map
        self.ground_truth = ground_truth_3d
        self.worldmap = np.zeros((200, 200, 3), dtype=np.float) 
        
        
        # Samples
        self.samples_pos = None 
        self.samples_pos_collected = None
        self.min_dist_to_sample = 5
        self.samples_to_find = 0 
        self.samples_located = 0 
        self.samples_collected = 0 
        self.near_sample = 0 
        self.picking_up = 0 
        self.send_pickup = False 

Rover = RoverState()
frame_counter = 0
second_counter = time.time()
fps = None

@sio.on('telemetry')
def telemetry(sid, data):
    global frame_counter, second_counter, fps
    frame_counter+=1
    
    if (time.time() - second_counter) > 1:
        fps = frame_counter
        frame_counter = 0
        second_counter = time.time()
    
    if data:
        global Rover
        Rover, image = update_rover(Rover, data)
        if np.isfinite(Rover.vel):
            Rover = perception_step(Rover)
            Rover = decision_step(Rover)
            out_image_string1, out_image_string2 = create_output_images(Rover)
            if Rover.send_pickup and not Rover.picking_up:
                send_pickup()
                Rover.send_pickup = False
            else:
                commands = (Rover.throttle, Rover.brake, Rover.steer)
                send_control(commands, out_image_string1, out_image_string2)
        else:
            send_control((0, 0, 0), '', '')

        if args.image_folder != '':
            timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
            image_filename = os.path.join(args.image_folder, timestamp)
            image.save('{}.jpg'.format(image_filename))

    else:
        sio.emit('manual', data={}, skip_sid=True)

@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    send_control((0, 0, 0), '', '')
    sample_data = {}
    sio.emit(
        "get_samples",
        sample_data,
        skip_sid=True)

def send_control(commands, image_string1, image_string2):
    data={'throttle': commands[0].__str__(),
        'brake': commands[1].__str__(),
        'steering_angle': commands[2].__str__(),
        'inset_image1': image_string1,
        'inset_image2': image_string2,
        }
    sio.emit("data",data,skip_sid=True)
    eventlet.sleep(0)

def send_pickup():
    print("Picking up")
    pickup = {}
    sio.emit("pickup",pickup,skip_sid=True)
    eventlet.sleep(0)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument(
        'image_folder',
        type=str,
        nargs='?',
        default='',
        help='Path to image folder. This is where the images from the run will be saved.'
    )
    args = parser.parse_args()
    #os.system('rm -rf IMG_stream/*')
    if args.image_folder != '':
        print("Creating image folder at {}".format(args.image_folder))
        if not os.path.exists(args.image_folder):
            os.makedirs(args.image_folder)
        else:
            shutil.rmtree(args.image_folder)
            os.makedirs(args.image_folder)
        print("Recording this run ...")
    else:
        print("NOT recording this run ...")
    
    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)
# deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)

