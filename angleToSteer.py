import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg

from generate_map import perspect_transform, color_thresh, rover_coords

image = mpimg.imread('angle_example.jpg')
dst_size =5
bottom_offset=6
source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],[image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],[image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],])


def polar_coord(xpix, ypix):
    mag = np.sqrt(xpix**2 + ypix**2)
    angle = np.arctan(ypix,xpix)
    return mag, angle
warped = perspect_transform(image, source, destination)
color_sel = color_thresh(warped, rgb_thresh=(170,170,170))
xpix, ypix = rover_coords(color_sel)

distance, angle = polar_coord(xpix, ypix)
avg_turning = np.mean(angle)

avg_turning_deg= avg_turning * 180/np.pi
steering_angle = np.clip(avg_turning_deg, -15 ,15)

fig = plt.figure(figsize=(12,9))
plt.subplot(221)
plt.imshow(image)
plt.subplot(222)
plt.imshow(warped)
plt.subplot(223)
plt.imshow(color_sel, cmap='gray')
plt.subplot(224)
plt.plot(xpix, ypix, '.')
plt.ylim(-160, 160)
plt.xlim(0, 160)
arrow_length = 100
x_arrow = arrow_length * np.cos(avg_turning)
y_arrow = arrow_length * np.sin(avg_turning)
plt.arrow(0, 0, x_arrow, y_arrow, color='red', zorder=2, head_width=10, width=2)
plt.show()
