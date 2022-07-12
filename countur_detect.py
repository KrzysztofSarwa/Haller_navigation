import cv2 as cv
import numpy as np


def contour_detection(mask_vertical_bar, frame):
    (contours, _) = cv.findContours(mask_vertical_bar, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    box_points = list()
    for contour in contours:
        rect = cv.minAreaRect(contour)
        box = cv.boxPoints(rect)
        if True: #contour_filter(contour, rect, box):
            box = np.int0(box)
            box_points.append(box)
            cv.drawContours(frame, [box], 0, (0, 0, 255), 2)


    # DEBUGGING:
    """if len(box_points) > 3:
        print("BREAKPOINT")
        print(box_points)
        for box in box_points:
            cv.drawContours(frame, [box], 0, (0, 0, 255), 10)
        cv.imshow("frame", frame)
        cv.waitKey(0)"""


def contour_filter(contour, rect, box):

    # remove contours that are too small
    perimeter = cv.arcLength(contour, True)
    if perimeter < 60:
        return False

    # remove contours that are too small again
    area = cv.contourArea(contour)
    if area < 2000:
        return False

    # Remove 'boxy' contours - keep rod-like ones
    # src says this is fast way to calc distance betw two points.
    # src: https://stackoverflow.com/questions/1401712/how-can-the-euclidean-distance-be-calculated-with-numpy
    # Since contour's 0-index is the lowest (greatest y-val) point, and goes clockwise, 0-1 and 1-2 must refer
    # to height and width (in any order)
    sides = [np.linalg.norm(box[0] - box[1]), np.linalg.norm(box[1] - box[2])]
    height = np.amax(sides)
    width = np.amin(sides)
    aspect_ratio = height / width
    if aspect_ratio < 1:
        return False


    # Our rods should fit tightly inside its bounding box. If not, then its probably distorted surface reflection
    # Solidity can be thought of as an approximation of the fit
    hull = cv.convexHull(contour)
    hull_area = cv.contourArea(hull)
    solidity = float(area) / hull_area
    if solidity < 0.8:
        return False

    # We want our rod to be vertical i.e. long side should be vertical.
    # src says angle in rect[2] (from minAreaRect)is calculated from first edge counterclockwise from horizontal (edge between box[0] and box[3]).
    # src: https://namkeenman.wordpress.com/2015/12/18/open-cv-determine-angle-of-rotatedrect-minarearect/
    transformed_angle = calc_minAreaRect_orientation(rect, sides)
    if transformed_angle < -135 or transformed_angle > -45:
        return False

    return True


# Transforms the [-90, 0] range of rect[2] to [-180, 0]
# designate 'height' as edge between box[0] and box[1]
# 'width' as edge between box[1] and box[2]
def calc_minAreaRect_orientation(rect, sides):
    if sides[1] < sides[0]:
        return rect[2] - 90
    else:
        return rect[2]