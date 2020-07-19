import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
from perspectivetf import perspectiveTF, color_thresh,rover_centric_coord
image = mpimg.imread('sample.jpg')
rover_yaw = np.random.random(1)*360
rover_xpos = np.random.random(1)*160 + 20
rover_ypos = np.random.random(1)*160 + 20

def rot(x_pixel, y_pixel, yaw):
    yaw_rad= yaw*np.pi/180
    xrot = x_pixel* np.cos(yaw_rad) - y_pixel* np.sin(yaw_rad)
    yrot = x_pixel* np.cos(yaw_rad) + y_pixel* np.sin(yaw_rad)    
    return xrot, yrot
def trans( x_pos, y_pos, xrot, yrot, scale):
    xw= np.int_(x_pos + (xrot/scale))
    yw= np.int_(y_pos + (yrot/scale))
    #truncating transalted values between 0 and 200 (world size taken 200)
    x_ts= np.clip(xw,0,199)
    y_ts= np.clip(yw,0,199)
    return x_ts, y_ts
def transform(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    xpix_rot, ypix_rot = rot(xpix, ypix, yaw)
    xpix_tran, ypix_tran = trans(xpos, ypos,xpix_rot, ypix_rot,scale)
    #x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    #y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    return xpix_tran, ypix_tran

dst_size= 5
bottom_offset =6
u= image.shape[1]/2
v= image.shape[0]/2

source= np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
dest =np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],[image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],[image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],])

warp= perspectiveTF(image, source, dest)
color_sel= color_thresh(warp, rgb_thresh=(160,160,160))
xpix, ypix = rover_centric_coord(color_sel)

worldmap = np.zeros((200,200))
scale =10

x_world, y_world= transform(xpix, ypix,rover_xpos, rover_ypos, rover_yaw, worldmap[0], scale)
worldmap[y_world, x_world]+=1

f, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
f.tight_layout()
ax1.plot(xpix, ypix, '.')
ax1.set_title('Rover Space', fontsize=40)
ax1.set_ylim(-160, 160)
ax1.set_xlim(0, 160)
ax1.tick_params(labelsize=20)

ax2.imshow(worldmap, cmap='gray')
ax2.set_title('World Space', fontsize=40)
ax2.set_ylim(0, 200)
ax2.tick_params(labelsize=20)
ax2.set_xlim(0, 200)