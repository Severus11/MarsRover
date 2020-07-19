import numpy as np

def rot(x_pos, y_pos, yaw):
    yaw_rad= yaw*np.pi/180
    xrot = x_pos* np.cos(yaw_rad) - y_pos* np.sin(yaw_rad)
    yrot = x_pos* np.cos(yaw_rad) + y_pos* np.sin(yaw_rad)    
    return xrot, yrot
def trans( x_pos, y_pos, xrot, yrot, scale)
    xw= np.int_(x_pos + (xrot/scale))
    yw= np.int_(y_pos + (yrot/scale))
    #truncating transalted values between 0 and 200 (world size taken 200)
    x_world= np.clip(xw,0,199)
    y_world= np.clip(yw,0,199)
    return x_world, y_world