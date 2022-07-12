import pyzed.sl as sl
import numpy as np
import sys
import cv2 as cv
import ogl_viewer.tracking_viewer as gl
from ZED.orange_mask_tuning import mask_bounds

do_u_want_zed = 1
perform_mask_tuning = 0

min_step = 0.1
xcen_of_view = 960
ycen_of_view = 540
set_position= {'x': 0, 'y': 0, 'z': 0, 'roll': 0, 'pitch': 0, 'yaw': 0}
#global_cor_now = {'x': 0, 'y': 0, 'z': 0, 'roll': 0, 'pitch': 0, 'yaw': 0}

if perform_mask_tuning:
    lower_bound, upper_bound = mask_bounds()
else:
    lower_bound = np.array([0, 128, 126])
    upper_bound = np.array([255, 255, 255])

zed = sl.Camera()

# ZED initialization for depth sensing
# ------------------------------------------------------------------------------------------

# Create a InitParameters object and set configuration parameters
init_params = sl.InitParameters()
init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Use PERFORMANCE depth mode
init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
init_params.camera_resolution = sl.RESOLUTION.HD720

# Open the camera
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    exit(1)

# Create and set RuntimeParameters after opening the camera
runtime_parameters = sl.RuntimeParameters()
runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode
# Setting the depth confidence parameters
runtime_parameters.confidence_threshold = 100
runtime_parameters.textureness_confidence_threshold = 100


# Create an RGBA sl.Mat object
image_zed = sl.Mat(zed.get_camera_information().camera_resolution.width, zed.get_camera_information().camera_resolution.height, sl.MAT_TYPE.U8_C4)
# Retrieve data in a numpy array with get_data()
image_ocv = image_zed.get_data()

# Create a sl.Mat with float type (32-bit)
depth_zed = sl.Mat(zed.get_camera_information().camera_resolution.width, zed.get_camera_information().camera_resolution.height, sl.MAT_TYPE.F32_C1)

# Create an RGBA sl.Mat object
image_depth_zed = sl.Mat(zed.get_camera_information().camera_resolution.width, zed.get_camera_information().camera_resolution.height, sl.MAT_TYPE.U8_C4)

# ZED initialization for positional tracking
# ------------------------------------------------------------------------------------------

# Set configuration parameters
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD720 # Use HD720 video mode (default fps: 60)
init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP # Use a right-handed Y-up coordinate system
init_params.coordinate_units = sl.UNIT.METER # Set units in meters

# Enable positional tracking with default parameters
tracking_parameters = sl.PositionalTrackingParameters()
err = zed.enable_positional_tracking(tracking_parameters)




while True:
    if zed.grab() == sl.ERROR_CODE.SUCCESS :
        #       NORMAL IMAGE
        # Retrieve the left image in sl.Mat
        zed.retrieve_image(image_zed, sl.VIEW.LEFT)
        # Use get_data() to get the numpy array
        image_ocv = image_zed.get_data()
        # Display the left image from the numpy array
        #cv.imshow("Image", image_ocv)

        #       DEPTH SENSING - FOR FURTHER PROCESSING
        # Retrieve depth data (32-bit)
        zed.retrieve_measure(depth_zed, sl.MEASURE.DEPTH)
        # Load depth data into a numpy array
        depth_ocv = depth_zed.get_data()
        # Print the depth value at the center of the image
        #print(depth_ocv[int(len(depth_ocv) / 2)][int(len(depth_ocv[0]) / 2)])

        #       DEPTH SENSING IMAGE - ONLY FOR DISPLAY
        # Retrieve the normalized depth image
        zed.retrieve_image(image_depth_zed, sl.VIEW.DEPTH)
        # Use get_data() to get the numpy array
        image_depth_ocv = image_depth_zed.get_data()
        # Display the depth view from the numpy array
        cv.imshow("Image", np.hstack([image_depth_ocv,image_ocv]))

    zed_pose = sl.Pose()
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        # Get the pose of the camera relative to the world frame
        state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
        # Display translation and timestamp
        py_translation = sl.Translation()
        tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
        ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
        tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
        print("Translation: tx: {0}, ty:  {1}, tz:  {2}, timestamp: {3}\n".format(tx, ty, tz, zed_pose.timestamp))
        # Display orientation quaternion
        py_orientation = sl.Orientation()
        ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
        oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
        oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
        ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
        print("Orientation: ox: {0}, oy:  {1}, oz: {2}, ow: {3}\n".format(ox, oy, oz, ow))

    if cv.waitKey(1) == ord('q'):
        break

    if do_u_want_zed == 1:
        frame = image_ocv[:, :, 0:3]
        image_depth= image_depth_ocv[:, :, 0:3]
        depth_frame = depth_ocv

    cv.waitKey(1000)
"""
    if bounds is not None:
        if any(bound.Class == "gman" for bound in bounds):
            for i in range(0, len(bounds)):
                if bounds[i].Class == "gman":
                    ymin = bounds[i].ymin
                    ymax = bounds[i].ymax
                    ycen = int((ymin + ymax) / 2)
                    if ycen >= self.ycen_of_view - 50 and ycen >= self.ycen_of_view + 50:
                        gate_found = 1
                    elif ycen <= self.ycen_of_view - 50:
                        self.global_cor_end['yaw'] += 15
                    elif ycen >= self.ycen_of_view + 50:
                        self.global_cor_end['yaw'] -= 15
        else:
            self.global_cor_end['yaw'] += 30


"""


viewer.exit()
zed.close()