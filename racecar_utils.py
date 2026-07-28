import numpy as np
import cv2

def get_lidar_closest_point(samples, window):
    # Find the closest point in a given window of lidar samples
    # If samples is empty or window is invalid, return 0.0
    if len(samples) == 0: return 0.0
    return np.min(samples)

def color_image_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

def crop(image, top_left, bottom_right):
    return image[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]
