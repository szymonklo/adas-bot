import cv2

from config import bottom_dist, height_step


def draw_lane_and_plates(plates_positions, lane_borders, image, plate_y, plate_x):
    bottom = bottom_dist  # todo: check if ok to change that value later (shallow copy)
    for lane_border_down, lane_border_up in lane_borders[:-1], lane_borders[1:]:
        if lane_border_down is not None and lane_border_up is not None:
            image = cv2.line(image, (bottom, lane_border_down[0]), (bottom + height_step, lane_border_up[0]), (255, 0, 0), 2)
            image = cv2.line(image, (bottom, lane_border_down[1]), (bottom + height_step, lane_border_up[1]), (255, 0, 0), 2)
    for plate_position in plates_positions:
        plate_x = (plate_position[0] + plate_position[1]) // 2
        plate_y = (plate_position[2] + plate_position[3]) // 2
        image = cv2.rectangle(image, (plate_position[0], plate_position[2]), (plate_position[1], plate_position[3]), (255, 0, 0), 2)

    image = cv2.circle(image, (plate_y, plate_x), 3, (255, 0, 0), 2)
    pass
