import cv2 as cv
import os
import numpy as np
from mss import mss
from PIL import Image
from color_correction import color_corr


def smoothing(frame):
    avg_blurr = cv.blur(frame, (5, 5))
    gaus_blurr = cv.GaussianBlur(avg_blurr, (5, 5), 0)
    med_blurr = cv.medianBlur(gaus_blurr, 9)

    return med_blurr


# From https://stackoverflow.com/questions/46390779/automatic-white-balancing-with-grayworld-assumption/46391574
def white_balance(LAB_frame):
    result = cv.cvtColor(LAB_frame, cv.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)

    return result

"""
# Return orange mask - NEED TUNING
def orange_mask(LAB_frame):
    lower_bound = np.array([0, 128, 126])
    upper_bound = np.array([255, 255, 255])
    orange_mask_frame = cv.inRange(LAB_frame, lower_bound, upper_bound)
    return orange_mask_frame
"""

def mask_morph(mask):
    kernel = np.ones((5, 5), np.uint8)
    opening = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    closing = cv.morphologyEx(opening, cv.MORPH_CLOSE, kernel)
    dilation = cv.dilate(closing, kernel, iterations=1)
    return dilation


def gate_preprocessing(frame, lower_bound, upper_bound):
    #ref = cv.imread('ref_imgs/ref_img3.png')
    #frame_color_corr = color_corr(frame, ref)
    frame = smoothing(frame)
    # White balance and transform from RGB -> LAB
    white_bal_LAB = white_balance(frame)

    orange_mask_frame = cv.inRange(white_bal_LAB, lower_bound, upper_bound)
    orange_mask_morph = mask_morph(orange_mask_frame)

    # convert binary img to BGR just to show with BGR in one window
    orange_maks_in_rgb = cv.cvtColor(orange_mask_morph, cv.COLOR_GRAY2BGR)
    # convert back LAB img into BGR
    converted_BGR = cv.cvtColor(white_bal_LAB, cv.COLOR_LAB2BGR)

    return orange_mask_morph, orange_maks_in_rgb, converted_BGR

