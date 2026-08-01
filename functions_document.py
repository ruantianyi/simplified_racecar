"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-prereq-labs

File Name: functions_document.py

Title: RACECAR Functions Document

Author: Tianyi Ruan

Purpose: A document of all of the different functions I have written
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2  # type: ignore
import cv2 as cv  # type: ignore
import numpy as np  # type: ignore


# If this file is nested inside a folder in the labs folder, the relative path should
# be [1, ../../library] instead.
sys.path.insert(0, '../library')
import racecar_core
import racecar_utils as rc_utils


# Load dictionary and parameters from the aruco library
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
arucoParams = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)

########################################################################################
# AR Marker class
########################################################################################

class ARMarker:
    def __init__(self, marker_id, marker_corners, orientation, area):
        self.id = marker_id
        self.corners = marker_corners
        self.orientation = orientation # Orientation of the marker
        self.area = area # Area of the marker
        self.color = ""
        self.color_area = 0

    def find_color_border(self, image):
        # Find the crop points and slice the image to the AR Marker
        crop_points = self.find_crop_points(image)
        image = image[crop_points[0][0]:crop_points[0][1], crop_points[1][0]:crop_points[1][1]]
        
        # Find the colors from the image
        color_name, color_area = self.find_colors(image)
        self.color = color_name
        self.color_area = color_area

    # [FUNCTION] Find the crop points for the AR Marker
    def find_crop_points(self, image):
        ORIENT = {"UP": 0, "LEFT": 1, "DOWN": 2, "RIGHT": 3}
        current_orientation = self.orientation
        
        # Top left corner mappings: UP = 0, LEFT = 1, DOWN = 2, RIGHT = 3
        marker_left, marker_top = self.corners[ORIENT[current_orientation]] # marker.corners are (x, y) -> (col, row) -> (right/left, top/down)
        # Bottom right corner mappings: UP = 3, LEFT = 4, DOWN = 1, RIGHT = 2
        marker_right, marker_bottom = self.corners[(ORIENT[current_orientation] + 2) % 4] # marker.corners are (x, y) -> (col, row)

        # Add half of marker length and marker width to crop points
        half_marker_length = (marker_right - marker_left) // 2
        half_marker_width = (marker_bottom - marker_top) // 2
        
        marker_top = max(0, marker_top - half_marker_width) # max function prevents value from decreasing past 0
        marker_left = max(0, marker_left - half_marker_length)
        marker_bottom = min(image.shape[0], marker_bottom + half_marker_width) + 1 # +1 prevents value from increasing past frame limits
        marker_right = min(image.shape[1], marker_right + half_marker_length) + 1

        return ((int(marker_top), int(marker_bottom)), (int(marker_left), int(marker_right)))

    # [FUNCTION] Find the colors in the image
    def find_colors(self, image):
        color_name = "None" # The detected color from the list of color thresholds
        color_area = 0 # The area of the detected color
        for (hsv_lower, hsv_upper, color) in COLORS:
            contours = rc_utils.find_contours(image, hsv_lower, hsv_upper)
            largest_contour = rc_utils.get_largest_contour(contours)
            if largest_contour is not None:
                contour_area = rc_utils.get_contour_area(largest_contour)
                if contour_area > color_area:
                    color_area = contour_area
                    color_name = color

        return color_name, color_area

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Declare any global variables here
# The last word in each of the variables is the shortened name of the
# function that it is used in, if only used in one function.

speed_smooth = 0
angle_smooth = 0
speed_prev_record = 0
angle_prev_record = 0
time_prev_record = 0
time_abs = 0
time_prev_smooth = 0
first_record = True
detector_ar = None
image_ar = None
ids_ar = None
corners_and_id = ""
markers_print = ""


# HSV Thresholds
BLUE = ((90, 115, 115),(120, 255, 255), "BLUE")
GREEN = ((40, 115, 115),(80, 255, 255), "GREEN")
RED1 = ((170, 115, 115), (179, 255, 255), "RED")
RED2 = ((0, 115, 115),(10, 255, 255), "RED")
COLORS = [BLUE, GREEN, RED1, RED2] # List of colors


########################################################################################
# NOTE: Line following functions are in the lab_f.py file
########################################################################################
# Functions
########################################################################################

# [FUNCTION] Retrieves AR markers using RACECAR library
def rc_ar_marker():
    image = rc.camera.get_color_image()
    markers = rc_utils.get_ar_markers(image)
    rc_utils.draw_ar_markers(image, markers)
    rc.display.show_color_image(image)


# [FUNCTION] Find the colors in the image
def find_colors(image):
    color_name = "None" # The detected color from the list of color thresholds
    color_area = 0 # The area of the detected color
    for (hsv_lower, hsv_upper, color) in COLORS:
        contours = rc_utils.find_contours(image, hsv_lower, hsv_upper)
        largest_contour = rc_utils.get_largest_contour(contours)
        if largest_contour is not None:
            contour_area = rc_utils.get_contour_area(largest_contour)
            if contour_area > color_area:
                color_area = contour_area
                color = color_name

    return color_name, color_area


# [FUNCTION] Find the crop points for the AR Marker
def find_crop_points(marker, image):
    ORIENT = {"UP": 0, "LEFT": 1, "DOWN": 2, "RIGHT": 3}
    current_orientation = marker.orientation
    
    # Top left corner mappings: UP = 0, LEFT = 1, DOWN = 2, RIGHT = 3
    marker_left, marker_top = marker.corners[ORIENT[current_orientation]] # marker.corners are (x, y) -> (col, row) -> (right/left, top/down)
    # Bottom right corner mappings: UP = 3, LEFT = 4, DOWN = 1, RIGHT = 2
    marker_right, marker_bottom = marker.corners[(ORIENT[current_orientation] + 2) % 4] # marker.corners are (x, y) -> (col, row)

    # Add half of marker length and marker width to crop points
    half_marker_length = (marker_right - marker_left) // 2
    half_marker_width = (marker_bottom - marker_top) // 2
    
    marker_top = max(0, marker_top - half_marker_width) # max function prevents value from decreasing past 0
    marker_left = max(0, marker_left - half_marker_length)
    marker_bottom = min(image.shape[0], marker_bottom + half_marker_width) + 1 # +1 prevents value from increasing past frame limits
    marker_right = min(image.shape[1], marker_right + half_marker_length) + 1

    return ((int(marker_top), int(marker_bottom)), (int(marker_left), int(marker_right)))


# [FUNCTION] Finds the area of an object with a set of corners
# NOTE: Only works if object is perfectly level
def find_area(corners):
    c = corners.reshape(4, 2)
    return abs((c[2][0] - c[0][0]) * (c[2][1] - c[0][1]))


# [FUNCTION] Takes in an image and returns a list of detected AR tags
def detect_ar(image):
    global detector_ar

    # Output: A list of detected AR Markers (returns as empty if none)
    markers = []

    # Initialize detector if not already done
    if detector_ar is None:
        arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        arucoParams = cv2.aruco.DetectorParameters()
        detector_ar = cv2.aruco.ArucoDetector(arucoDict, arucoParams)

    # Detect AR Marker from image and return their corners and IDs
    corners, ids, _ = detector_ar.detectMarkers(image)

    # Loop through all corner and ID indexes
    for x in range(len(corners)):
        # Retrieve current corner
        current_corners = corners[x]

        # Find the orientation of the marker
        orientation = find_orientation(current_corners)

        # Find the area of each marker
        area = find_area(current_corners)

        # Create current marker object and add to list
        current_marker = ARMarker(ids[x][0], current_corners, orientation, abs(area))
        
        markers.append(current_marker)

    cv2.aruco.drawDetectedMarkers(image, corners, ids, (0, 255, 0))

    return markers, image


# [FUNCTION] Determine marker orientation from corner positions
def find_orientation(corners):
    c = corners.reshape(4, 2)
    x1, y1 = c[0][0], c[0][1]
    x2, y2 = c[1][0], c[1][1]

    if x1 == x2:  # if x1 = x2, RIGHT or LEFT
        if y1 > y2:  # if y1 > y2, LEFT
            orientation = "LEFT"
        else:  # if y2 > y1, RIGHT
            orientation = "RIGHT"
    else:  # if x1 != x2, UP or DOWN
        if x1 > x2:  # if x1 > x2, DOWN
            orientation = "DOWN"
        else:  # if x2 > x1, UP
            orientation = "UP"

    return orientation


# [FUNCTION] Detects AR markers and labels the detections onto a camera frame
def ar_marker():
    global detector_ar
    global image_ar
    global ids_ar
    global corners_and_id

    image = rc.camera.get_color_image()
    markers, image = detect_ar(image)
    
    # Print the corners and id of the first detected marker to the terminal
    corners_and_id = f"========== Detection Summary =========="
    corners_and_id += f"\nAmount of AR Tags Found: {len(markers)}"
    for marker in markers:
        corners_and_id += f"\nMarker ID: {marker.id} || Marker Orientation: {marker.orientation} || Marker Area: {marker.area}"
    corners_and_id += f"\n========== End of Summary ==========\n"

    # Crop the image to twice the size of the marker, centered around the marker
    if markers:
        current_corners = markers[0].corners
        center_x = np.mean(current_corners[:, 0])
        center_y = np.mean(current_corners[:, 1])
        marker_width = np.max(current_corners[:, 0]) - np.min(current_corners[:, 0])
        marker_height = np.max(current_corners[:, 1]) - np.min(current_corners[:, 1])
        crop_width = int(marker_width * 2)
        crop_height = int(marker_height * 2)
        x1 = int(max(0, center_x - crop_width // 2))
        y1 = int(max(0, center_y - crop_height // 2))
        x2 = int(min(image.shape[1], center_x + crop_width // 2))
        y2 = int(min(image.shape[0], center_y + crop_height // 2))

        # Mark out the contour on the full image
        cv.drawContours(image, [current_corners.astype(np.int32)], -1, (0, 255, 0), 3)

    rc.display.show_color_image(image)


# [FUNCTION] Detects the contours in an image
def contour_detect():
    # Take a frame from the camera stream and store it inside the "image" variable
    image = rc.camera.get_color_image()

    # Crop the image 
    image = rc_utils.crop(image, (180, 0), (rc.camera.get_height(), rc.camera.get_width()))

    # Define lower and upper HSV bounds for the color
    hsv_lower = (95, 100, 100)
    hsv_upper = (120, 255, 255)

    # Change color space from BGR to HSV
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Create a mask based on the hsv threshold
    mask = cv.inRange(hsv, hsv_lower, hsv_upper)

    # Find valid contours in the mask
    contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    # Filter out unnecessary contours by area
    max_contour = contours[0]
    contour_min = 30
    contours_filtered = []
    for contour in contours:
        if cv.contourArea(contour) > contour_min:
            contours_filtered.append(contour)

            # Detects the largest contour
            # NOTE: Do not use if detecting multiple objects
            if cv.contourArea(contour) > cv.contourArea(max_contour):
                max_contour = contour

    # Draw the contours
    cv.drawContours(image, contours_filtered, -1, (0, 255, 0), 3)

    # Draw the center of the largest contour (N/A for multiple object detection)
    contour_center = rc_utils.get_contour_center(max_contour)
    cv.circle(image, (contour_center[1], contour_center[0]), 6, (0, 255, 255), -1)

    # Display the frame to the screen
    rc.display.show_color_image(image)


# [FUNCTION] Convert images between color types
# NOTE: This function can be put into the update_slow() function to
# allow for faster running of other functions only if the interval
# for update_slow() is no more than 0.2 seconds
def color_detect():
    # Take a frame from the camera stream and store it inside the "image" variable
    image = rc.camera.get_color_image()

    # Crop the image (in this case, cropping out the blue sky)
    image = rc_utils.crop(image, (180, 0), (rc.camera.get_height(), rc.camera.get_width()))

    # Define lower and upper HSV bounds for the color orange
    # Change these values to change the color to be detected
    hsv_lower = (80, 50, 50)
    hsv_upper = (125, 255, 255)

    # Change color space from BGR to HSV
    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Create a mask based on the hsv threshold
    mask = cv.inRange(image, hsv_lower, hsv_upper)

    # Display the frame to the screen
    rc.display.show_color_image(mask)


# [Function] process a single pixel in an image
# NOTE: This function can be put into the update_slow() function to
# allow for faster running of other functions only if the interval
# for update_slow() is no more than 0.2 seconds
def process_pixel():
    # Take a frame from the camera stream and store it inside the "image" variable
    image = rc.camera.get_color_image()

    # Store image dimensions
    dimension = image.shape

    # Print info into the terminal
    print("\n=====================================")
    print(f"Height of image: {dimension[0]}")
    print(f"Width of image: {dimension[1]}")
    print(f"Depth of image: {dimension[2]}")
    print("=====================================\n")

    # EXAMPLE: Find pixel in the middle of the screen
    row = dimension[0] // 2
    col = dimension[1] // 2

    # Extract and print blue, green, and red values
    blue = image[row][col][0]
    green = image[row][col][1]
    red = image[row][col][2]
    print(f"BGR: ({blue}, {green}, {red})")

    # Display color to screen
    BGR_color = (blue, green, red)
    BGR_image = np.zeros((300, 300, 3), np.uint8)
    BGR_image[:] = BGR_color
    cv.namedWindow("BGR Color Display", cv.WINDOW_NORMAL)
    cv.imshow("BGR COLOR DISPLAY", BGR_image)

    # Draw a yellow dot in the location of (row, col) on the screen
    cv.circle(image, (col, row), 5, (0, 255, 255), -1)

    # Display the frame to the screen
    rc.display.show_color_image(image)


# [FUNCTION] The movement function allows the RACECAR to more with keyboard input
# TODO: Must declare speed = 0 and angle = 0 at the start of the program
def movement():
    speed = 0
    angle = 0
    
    if rc.controller.is_down(rc.controller.Button.A):
        speed += 1

    if rc.controller.is_down(rc.controller.Button.B):
        speed -= 1

    if rc.controller.is_down(rc.controller.Button.X):
        angle -= 1

    if rc.controller.is_down(rc.controller.Button.Y):
        angle += 1
    
    # print(f"Speed: {speed}, Angle: {angle}")
    rc.drive.set_speed_angle(speed, angle)


# [FUNCTION] movement_smooth() allows for smoother transitions but may be slower and lag
# TODO: Must declare speed = 0, angle = 0, and time_abs = 0 at the start of the program
def movement_smooth():
    global speed_smooth
    global angle_smooth
    global time_abs
    global time_prev_smooth
    
    speed = speed_smooth
    angle = angle_smooth
    delta_time = time_abs - time_prev_smooth

    # Speed controls
    if rc.controller.is_down(rc.controller.Button.LB):
        speed = 0

    elif rc.controller.is_down(rc.controller.Button.A):
        if speed <= 1 - 6 * delta_time:
            speed += 6 * delta_time
        else:
            speed = 1

    elif rc.controller.is_down(rc.controller.Button.B):
        if speed >= -1 + 6 * delta_time:
            speed -= 6 * delta_time
        else:
            speed = -1

    else:
        if speed > 3 * delta_time:
            speed -= 3 * delta_time
        elif speed < -3 * delta_time:
            speed += 3 * delta_time
        else:
            speed = 0

    # Angle controls
    if rc.controller.is_down(rc.controller.Button.RB):
        angle = 0
    
    elif rc.controller.is_down(rc.controller.Button.Y):
        if angle <= 1 - 6 * delta_time:
            angle += 6 * delta_time
        else:
            angle = 1

    elif rc.controller.is_down(rc.controller.Button.X):
        if angle >= -1 + 6 * delta_time:
            angle -= 6 * delta_time
        else:
            angle = -1

    else:
        if angle > 3 * delta_time:
            angle -= 3 * delta_time
        elif angle < -3 * delta_time:
            angle += 3 * delta_time
        else:
            angle = 0

    # Send the speed and angle values to the RACECAR
    rc.drive.set_speed_angle(speed, angle)

    speed_smooth = speed
    angle_smooth = angle

    time_prev_smooth = time_abs
    

# [FUNCTION] Records the commands pressed in the RACECAR to easily replicate a similar pattern
# TODO Declare all global variables except first_record as 0 at the start
# TODO Make first_record equal to True at the start
# TODO Modify the list name to the desired name here in the function
# NOTE: DO NOT RUN ANY MOVEMENT FUNCTIONS ALONGSIDE THIS!
def movement_record():
    global speed_prev_record
    global angle_prev_record
    global time_abs
    global time_prev_record
    global first_record

    list_name = ""
    
    speed = 0
    angle = 0

    if rc.controller.is_down(rc.controller.Button.A):
        speed += 1

    if rc.controller.is_down(rc.controller.Button.B):
        speed -= 1

    if rc.controller.is_down(rc.controller.Button.X):
        angle -= 1

    if rc.controller.is_down(rc.controller.Button.Y):
        angle += 1
    
    rc.drive.set_speed_angle(speed, angle)

    # Track the speed and angle and then print if necessary
    if (speed, angle) != (speed_prev_record, angle_prev_record):
        if first_record:
            first_record = False
        else:
            print(f"{list_name}.append([{time_abs - time_prev_record}, {speed_prev_record}, {angle_prev_record}])")
        time_prev_record = time_abs

    speed_prev_record = speed
    angle_prev_record = angle

    speed = 0
    angle = 0


# [Function] The time function records the absolute time elapsed
# TODO Make sure to declare time_abs = 0 in the global variables
# TODO Ensure that the function rc.get_delta_time is not found elsewhere in the program
# TODO This function should be FIRST in update()
def time():
    global time_abs
    time_abs += rc.get_delta_time()


# [FUNCTION] The start function is run once every time the start button is pressed
def start():
    rc.drive.stop()

    rc.drive.set_max_speed(0.3)
    
    # Sets the update_slow() function to be called once every 0.2 seconds for image processing
    # NOTE: DO NOT MODIFY
    # ,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    rc.set_update_slow_time(1) # <-- Can modify this if there is nothing important in update_slow()
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # More functions can be placed below
    
    

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed  
def update():
    global image_ar
    global ids_ar
    global markers_print
    ##################################################################################
    time()  # <-- DO NOT MODIFY
    ##################################################################################

    movement()

    # The below prints out some stuff about the AR markers
    """
    ar_marker()

    image_ar = rc.camera.get_color_image()
    markers, _ = detect_ar(image_ar)

    if markers:
        markers_print = f"ID: {markers[0].id} || Orientation: {markers[0].orientation} || Corners: {markers[0].corners}"
    else:
        markers_print = ""
    """

# [FUNCTION] update_slow() is similar to update() but is called once per second by
# default. It is especially useful for printing debug messages, since printing a 
# message every frame in update is computationally expensive and creates clutter
# NOTE: The time interval is currently assigned to 0.2 secondsfor image processing.
def update_slow():
    pass

    # The below prints out some stuff about AR markers
    """
    global corners_and_id
    global markers_print

    print(corners_and_id)
    print(markers_print)
    """

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
