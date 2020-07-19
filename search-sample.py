import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

filename = 'sample.jpg'
image = mpimg.imread(filename)
#print(image.dtype,image.shape, np.min(image), np.max(image))
# uint8, 160,320,3 0-255 8bit coloring
plt.imshow(image)
plt.show()

