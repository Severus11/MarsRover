import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
import numpy as np
import cv2


image = mpimg.imread('example_grid1.jpg')
plt.imshow(image)
plt.show()

## source LL (14.7,140); (118,96); (200,96); 300,140
## destination()
dst_size= 5
bottom_offset =6
u= image.shape[1]/2
v= image.shape[0]/2

source= np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
dest =np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])

def perspectiveTF(image, src, dst):
    M = cv2.getPerspectiveTransform(src,dst)    
    warped= cv2.warpPerspective(image, M, (image.shape[1], image.shape[0]))
    return warped

warp= perspectiveTF(image, source, dest)
cv2.polylines(image, np.int32([source]), True, (0, 0, 255), 3)
cv2.polylines(warp, np.int32([dest]), True, (0, 0, 255), 3)

f, (ax1,ax2) = plt.subplots(1,2,figsize=(24,6), sharey= True)
ax1.imshow(image)
ax1.set_title('original')
ax2.imshow(warp)
ax2.set_title('transformed')
plt.show()
