import math

import cv2


def find_circles(mask, image):
    # todo - 1. circle vs triangle vs rectangle
    #        2. join split contours?
    # circles = cv2.HoughCircles(image=mask, method=cv2.HOUGH_GRADIENT, dp=1, minDist=1)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_filtered = [cnt for cnt in contours if cnt.shape[0] > 40]

    # img = cv2.drawContours(image, contours_filtered, -1, (0, 255, 0), 1)
    # cv2.imshow('cnt', img)
    # cv2.waitKey(0)

    if len(contours_filtered) > 0:
        contour_desc = sorted(contours_filtered, key=len, reverse=True)
        for cnt in contour_desc:

            x, y, w, h = cv2.boundingRect(cnt)
            perimeter = cv2.arcLength(cnt, closed=True)
            (x_mec, y_mec), radius = cv2.minEnclosingCircle(cnt)
            x_mec, y_mec, radius = int(x_mec), int(y_mec), int(radius)

            max_additional_length_vs_circle = 0.08
            circle_perieter = 2 * math.pi * radius

            if abs(perimeter - circle_perieter) < max_additional_length_vs_circle * circle_perieter:
                x = x_mec - radius
                y = y_mec - radius
                w = 2 * radius
                h = 2 * radius

                sign_image = image[y: y + h, x: x + w, :]

                return x, y, w, h, sign_image

    return None, None, None, None, None

    m = cv2.moments(contour_max)
    cx = int(m["m10"] / m["m00"])
    cy = int(m["m01"] / m["m00"])

    image_cm = cv2.circle(image, (cx, cy), 1, (255, 0, 0), 1)

    # cv2.imshow('center_of_mass', image_cm)
    # cv2.waitKey(0)

    (x, y), radius = cv2.minEnclosingCircle(contour_max)
    center = (int(x), int(y))
    radius = int(radius)

    dist_cm_to_cmec = int(((x-cx)**2 + (y-cy)**2)**(1/2))
    print(dist_cm_to_cmec)

    img_circle = cv2.circle(image_cm, center, radius, (0, 0, 255), 1)
    img_circle = cv2.circle(img_circle, center, 1, (0, 0, 255), 1)
    cv2.imshow('circle', img_circle)
    cv2.waitKey(0)


    pass
