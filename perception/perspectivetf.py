import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
import numpy as np
import cv2


image = mpimg.imread('example_grid1.jpg')
#plt.imshow(image)
#plt.show()

## source LL (14.7,140); (118,96); (200,96); 300,140
## destination()
dst_size= 5
bottom_offset =6
u= image.shape[1]/2
v= image.shape[0]/2

source= np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
dest =np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],[image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],[image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],])

def perspectiveTF(image, src, dst):
    M = cv2.getPerspectiveTransform(src,dst)    
    warped= cv2.warpPerspective(image, M, (image.shape[1], image.shape[0]))
    return warped

def color_thresh(img, rgb_thresh =(0,0,0)):
    color_sel = np.zeros_like(img[:,:,0])
    above_thresh =above_thresh = (img[:,:,0] > rgb_thresh[0])& (img[:,:,1] > rgb_thresh[1])& (img[:,:,2] > rgb_thresh[2])
    color_sel[above_thresh]=1
    return color_sel
def rover_centric_coord(img):
    y_pos, x_pos = img.nonzero()
    x_pixel = -(y_pos -img.shape[0]).astype(np.float)
    y_pixel = -(x_pos - img.shape[1]/2).astype(np.float)
    return x_pixel, y_pixel

warp= perspectiveTF(image, source, dest)
#cv2.polylines(image, np.int32([source]), True, (0, 0, 255), 3)
#cv2.polylines(warp, np.int32([dest]), True, (0, 0, 255), 3)

color_sel= color_thresh(warp, rgb_thresh=(160,160,160))

xrc, yrc = rover_centric_coord(color_sel)

'''
f, (ax1,ax2) = plt.subplots(1,2,figsize=(24,6), sharey= True)
ax1.imshow(warp)
ax1.set_title('original')
ax2.imshow(thresh)
ax2.set_title('transformed')
ypos, xpos = color_sel.nonzero()
plt.plot(xpos, ypos, '.')
plt.xlim(0, 320)
plt.ylim(0, 160)'''
fig = plt.figure(figsize=(5, 7.5))
plt.plot(xrc, yrc, '.')
plt.ylim(-160, 160)
plt.xlim(0, 160)
plt.title('Rover-Centric Map', fontsize=20)
plt.show() 

#plt.imshow(color_sel, cmap = 'gray')
#plt.show()

