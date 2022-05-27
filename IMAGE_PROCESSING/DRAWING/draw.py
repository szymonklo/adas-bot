import copy

import cv2

from config import bottom_dist, height_step


def draw_lane_and_plates(plates_positions, lane_borders, image, min_plate_y, min_plate_x):
    image = draw_lane(image, lane_borders)
    for plate_position in plates_positions:
        plate_x = (plate_position[0] + plate_position[1]) // 2
        plate_y = (plate_position[2] + plate_position[3]) // 2
        image = cv2.rectangle(image, (plate_position[0], plate_position[2]), (plate_position[1], plate_position[3]),
                              (255, 0, 0), 2)

    image = cv2.circle(image, (min_plate_y, min_plate_x), 3, (255, 0, 0), 2)
    return image


def draw_lane(image, lane_borders, max_diff_internal=None, edge_found_statuses=None):
    image_with_lane = copy.deepcopy(image)
    lane_borders.append(lane_borders[-1])
    bottom = image.shape[0] - bottom_dist  # todo: check if ok to change that value later (shallow copy)
    for i, (lane_border_down, lane_border_up) in enumerate(zip(lane_borders[:-1], lane_borders[1:])):
        thickness = 1
        if edge_found_statuses:
            if edge_found_statuses[i]:
                thickness = 2
        if lane_border_down is not None and lane_border_up is not None:
            # image = cv2.line(image, (bottom, lane_border_down[0]), (bottom + height_step, lane_border_up[0]), (255, 0, 0), 2)
            # image = cv2.line(image, (bottom, lane_border_down[1]), (bottom + height_step, lane_border_up[1]), (255, 0, 0), 2)
            image_with_lane = cv2.line(image_with_lane, (lane_border_down[0], bottom - i * height_step),
                                       (lane_border_up[0], bottom - (i + 1) * height_step), (255, 0, 0), thickness)
            image_with_lane = cv2.line(image_with_lane, (lane_border_down[1], bottom - i * height_step),
                                       (lane_border_up[1], bottom - (i + 1) * height_step), (255, 0, 0), thickness)
            if max_diff_internal is not None:
                image_with_lane = put_diff_res(bottom, i, image_with_lane, lane_border_down, max_diff_internal,
                                               thickness)
    return image_with_lane


def put_diff_res(bottom, i, image_with_lane, lane_border_down, max_diff_internal, thickness):
    max_diff = str(round(max_diff_internal[i], 0))
    image_with_lane = cv2.putText(image_with_lane, max_diff, (lane_border_down[1] + 50, bottom - i * height_step),
                                  fontScale=0.6,
                                  fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                  thickness=thickness,
                                  color=(255, 0, 0))
    return image_with_lane
