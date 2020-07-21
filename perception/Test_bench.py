import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.misc 
import glob  
import pandas as pd 
import imageio
imageio.plugins.ffmpeg.download()

from generate_map import perspect_transform, color_thresh, rover_coords, rotate_pix, translate_pix, pix_to_world
from angleToSteer import polar_coord

dst_size =5
bottom_offset = 6

df= pd.read_csv('robot_log.csv', delimiter= ';', decimal='.')
csv_img_list= df["Path"].tolist()   
ground_map = mpimg.imread('map_bw.png')
ground_map_3d = np.dstack((ground_map*0, ground_map*255, ground_map*0))

class Databucket():
    def __init__(self):
        self.images = csv_img_list  
        self.xpos = df["X_Position"].values
        self.ypos = df["Y_Position"].values
        self.yaw = df["Yaw"].values
        self.count = 0
        self.worldmap = np.zeros((200, 200, 3)).astype(np.float)
        self.ground_map = ground_map_3d

data = Databucket()

def process_image(img):
    output_image = np.zeros((img.shape[0] + data.worldmap.shape[0], img.shape[1]*2, 3))
    output_image[0:img.shape[0], 0:img.shape[1]] = img
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[img.shape[1]/2 - dst_size, img.shape[0] - bottom_offset],[img.shape[1]/2 + dst_size, img.shape[0] - bottom_offset],[img.shape[1]/2 + dst_size, img.shape[0] - 2*dst_size - bottom_offset], [img.shape[1]/2 - dst_size, img.shape[0] - 2*dst_size - bottom_offset],])
    
    warped = perspect_transform(img, source, destination)
    output_image[0:img.shape[0], img.shape[1]:] = warped
    
    map_add = cv2.addWeighted(data.worldmap, 1, data.ground_map, 0.5, 0,dtype = cv2.CV_32F)
    output_image[img.shape[0]:, 0:data.worldmap.shape[1]] = np.flipud(map_add)
    
    cv2.putText(output_image,"Populate this image with your analyses to make a video!", (20, 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
    if data.count < len(data.images) - 1:
        data.count += 1
    return output_image

from moviepy.editor import VideoFileClip
from moviepy.editor import ImageSequenceClip

output = 'test_mapping.mp4'
data = Databucket()
clip = ImageSequenceClip(data.images, fps=60) 
                                          
new_clip = clip.fl_image(process_image)
new_clip.write_videofile(output, audio=False)

from IPython.display import HTML
HTML("""<video width="960" height="540" controls><source src="{0}"></video>""".format(output))

