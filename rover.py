import numpy as np

class RoverState():
    def __init__(self):
        self.start_time = None 
        self.total_time = None 
        self.img = None 
        self.pos = None 
        self.yaw = None 
        self.pitch = None 
        self.roll = None 
        self.vel = None 
        self.steer = 0 
        self.throttle = 0 
        self.brake = 0 
        self.nav_angles = None 
        self.nav_dists = None 
        self.ground_truth = ground_truth_3d 
        self.mode = 'forward' 
        self.throttle_set = 0.2 
        self.brake_set = 10 
        self.stop_forward = 50 
        self.go_forward = 500 
        self.max_vel = 2 
        self.vision_image = np.zeros((160, 320, 3), dtype=np.float) 
        self.worldmap = np.zeros((200, 200, 3), dtype=np.float) 
        self.samples_pos = None 
        self.samples_found = 0 
        self.near_sample = False 
        self.pick_up = False 

Rover = RoverState()
Rover.vel = new_velocity_from_telemetry
Rover.yaw = new_yaw_from_telemetry
