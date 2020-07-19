import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

filename = 'sample.jpg'
image = mpimg.imread(filename)
#print(image.dtype,image.shape, np.min(image), np.max(image))
# uint8, 160,320,3 0-255 8bit coloring
#plt.imshow(image)
#plt.show()
def color_thresh(img, rgb_thresh=(0,0,0)):
    color_sel = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] > rgb_thresh[0])& (img[:,:,1] > rgb_thresh[1])& (img[:,:,2] > rgb_thresh[2])
    #if(img[:,:,0]>rgb_thresh[0] & img[:,:,1]>rgb_thresh[1] & img[:,:,2]>rgb_thresh[2]):
    color_sel[above_thresh]=1
    return color_sel

plt.imshow(color_thresh(image, rgb_thresh=(160,160,160)))
plt.show()
