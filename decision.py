import numpy as np
import time


def initial_setup(Rover):
    if 90<Rover.yaw<95:
        Rover.throttle = Rover.throttle_set
        Rover.brake =0
        Rover.steer =0
        if len(Rover.nav_angles)<Rover.go_forward:
            Rover.mode= 'stop'
    else:
        Rover.brake =0
        Rover.throttle =0
        if Rover.yaw<90 or Rover.yaw >=270:
            Rover.steer = 10
        else:
            Rover.steer =-10

   
def decision_step(Rover): 
    if Rover.p_pos == None:
        Rover.p_pos = Rover.pos
    else:
        if Rover.p_pos != Rover.pos:
            Rover.stop_time = Rover.total_time
            
    if Rover.total_time - Rover.stop_time > Rover.max_time:
        Rover.throttle = 0
        Rover.brake = 0
        Rover.steer = -15
        time.sleep(1) 
        
    if Rover.nav_angles is not None:
        if Rover.mode == 'start':
            initial_setup(Rover)               
        if Rover.mode == 'sample':
            recover_sample(Rover, nearest_sample)
        if Rover.mode == 'forward':
            move(Rover) 
        if Rover.mode == 'tostop':
            stop(Rover) 
        if Rover.mode == 'stop':
            find_and_go(Rover)          
    return Rover

def stop(Rover):
    if Rover.vel >0.2:
        Rover.throttle =0
        Rover.brake = Rover.brake_set
        Rover.steer=0
    elif Rover.vel<0.2:
        Rover.mode = "stop"

def find_and_go(Rover):
    if Rover.near_sample and Rover.vel ==0 and not Rover.picking_up:
        Rover.send_pickup =True
    else:
        if len(Rover.nav_angles)< Rover.go_forward:
            Rover.throttle =0
            Rover.brake =0
            Rover.steer = -25
        elif len(Rover.nav_angles)>= Rover.go_forward:
            Rover.throttle = Rover.throttle_set
            Rover.brake =0
            Rover.mode= "forward"

def move(Rover):
    if Rover.near_sample:
        Rover.mode = 'tostop'

    if len(Rover.nav_angles)>= Rover.stop_forward:
        if Rover.vel <Rover.max_vel:
            Rover.throttle= Rover.throttle_set
        else:
            Rover.throttle =0
        Rover.brake =0
        Rover.p_steer = Rover.steer
        Rover.steer = np.max((Rover.nav_angles)*180/np.pi)-50
    else:
        Rover.mode = 'tostop'

