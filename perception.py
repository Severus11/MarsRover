import numpy as np
import cv2
from enum import Enum

class Mode(Enum):
    GROUND = "ground"
    OBSTACLE = "obstacle"
    SAMPLE = "sample"
    
sample_low_thresh = (120, 110, 0) 
sample_high_thresh = (205, 180, 70)
dst_size = 5
bottom_offset = 6
map_scale = 10

def color_thresh(img, low_thresh=(0, 0, 0), high_thresh=(160, 160, 160), mode=Mode.GROUND):
    color_select = np.zeros_like(img[:,:,0])

    final_thresh = None
    if (mode == Mode.OBSTACLE):
        final_thresh = (img[:,:,0] < high_thresh[0]) \
                    & (img[:,:,1] < high_thresh[1]) \
                    & (img[:,:,2] < high_thresh[2])
    elif (mode == Mode.SAMPLE):        
        final_thresh = (np.logical_and(img[:,:,0] >= low_thresh[0], img[:,:,0] <= high_thresh[0])) \
                    &  (np.logical_and(img[:,:,1] >= low_thresh[1], img[:,:,1] <= high_thresh[1])) \
                    &  (np.logical_and(img[:,:,2] >= low_thresh[2], img[:,:,2] <= high_thresh[2]))
    else:
        final_thresh = (img[:,:,0] > high_thresh[0]) \
                    & (img[:,:,1] > high_thresh[1]) \
                    & (img[:,:,2] > high_thresh[2])
    color_select[final_thresh] = 1
    return color_select

def rover_coords(binary_img):
    ypos, xpos = binary_img.nonzero()  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel

def to_polar_coords(x_pixel, y_pixel):
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    angles = np.arctan2(y_pixel, x_pixel)
    min_distance = 30
    max_distance = 60
    idx = np.where(min_distance < dist)
    idy = np.where(max_distance > dist)
    dist = np.delete(dist, idx)
    dist = np.delete(dist, idy)
    angles = np.delete(angles, idx)
    angles = np.delete(angles, idy)
    
    return dist, angles

def rotate_pix(xpix, ypix, yaw):
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))                      
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    return xpix_translated, ypix_translated

def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    return x_pix_world, y_pix_world

def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))  
    return warped

def perception_step(Rover):
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])
    warped = perspect_transform(Rover.img, source, destination)
    ground_thresh = color_thresh(warped, mode=Mode.GROUND)
    obstacle_thresh = color_thresh(warped, mode=Mode.OBSTACLE)
    sample_thresh = color_thresh(
        warped, 
        mode=Mode.SAMPLE, 
        low_thresh=sample_low_thresh, 
        high_thresh=sample_high_thresh
    )
    
    Rover.vision_image[:,:,0] = obstacle_thresh * 255
    Rover.vision_image[:,:,1] = sample_thresh * 255
    Rover.vision_image[:,:,2] = ground_thresh * 255  
    
    ground_x, ground_y = rover_coords(ground_thresh)
    obstacle_x, obstacle_y = rover_coords(obstacle_thresh)
    sample_x, sample_y = rover_coords(sample_thresh)
     
    w_ground_x, w_ground_y = pix_to_world(ground_x, 
                                          ground_y, 
                                          Rover.pos[0], 
                                          Rover.pos[1], 
                                          Rover.yaw, 
                                          Rover.worldmap.shape[0], 
                                          map_scale)
    w_obstacle_x, w_obstacle_y = pix_to_world(obstacle_x, 
                                              obstacle_y,
                                              Rover.pos[0], 
                                              Rover.pos[1], 
                                              Rover.yaw, 
                                              Rover.worldmap.shape[0],
                                              map_scale)
    w_sample_x, w_sample_y = pix_to_world(sample_x, 
                                          sample_y,
                                          Rover.pos[0], 
                                          Rover.pos[1], 
                                          Rover.yaw, 
                                          Rover.worldmap.shape[0],
                                          map_scale)
    
    if Rover.pitch < Rover.max_pitch and Rover.roll < Rover.max_roll:
        Rover.worldmap[w_obstacle_y, w_obstacle_x, 0] += 1
        Rover.worldmap[w_sample_y, w_sample_x, 1] += 1
        Rover.worldmap[w_ground_y, w_ground_x, 2] += 1
    
    polar = to_polar_coords(ground_x, ground_y)
    Rover.nav_dists = polar[0]
    Rover.nav_angles = polar[1]

    return Rover