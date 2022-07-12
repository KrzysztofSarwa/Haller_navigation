
def zed_frame():
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        #       NORMAL IMAGE
        # Retrieve the left image in sl.Mat
        zed.retrieve_image(image_zed, sl.VIEW.LEFT)
        # Use get_data() to get the numpy array
        image_ocv = image_zed.get_data()
        # Display the left image from the numpy array
        # cv.imshow("Image", image_ocv)

        #       DEPTH SENSING - FOR FURTHER PROCESSING
        # Retrieve depth data (32-bit)
        zed.retrieve_measure(depth_zed, sl.MEASURE.DEPTH)
        # Load depth data into a numpy array
        depth_ocv = depth_zed.get_data()
        # Print the depth value at the center of the image
        print(depth_ocv[int(len(depth_ocv) / 2)][int(len(depth_ocv[0]) / 2)])

        #       DEPTH SENSING IMAGE - ONLY FOR DISPLAY
        # Retrieve the normalized depth image
        zed.retrieve_image(image_depth_zed, sl.VIEW.DEPTH)
        # Use get_data() to get the numpy array
        image_depth_ocv = image_depth_zed.get_data()
        # Display the depth view from the numpy array
        # cv.imshow("Image", np.hstack([image_depth_ocv, image_ocv]))
        return image_ocv, depth_ocv, image_depth_ocv