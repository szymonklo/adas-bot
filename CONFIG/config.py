window_line = {
    'left':   600,
    'top':    460-50-15,    # -15 to cut steering wheel
    'width':  980,
    'height': 220,
}

# 2021-06-27 window 1920x1080
window_speed = {
    'left':   1496,
    'top':    770 - 60,   # for window mode: 770-27, for 1080 full screen: 770-60   'top':    710,
    'width':  30,
    'height': 18,
}

window_signs = {
    'left':   1000,
    'top':    310,      # 'top':    250,
    'width':  600,
    'height': 250,
}


class Keys:
    left = 'a'
    right = 'd'
    up = 'w'
    down = 's'


# ref_digits.py init_ref_digits
class RefDigitsPath:
    cluster = r'C:\PROGRAMOWANIE\auto_data\photos\ref_digits'
    signs = r'C:\PROGRAMOWANIE\auto_data\photos\ref_digits_signs'


# DETECTIONS

# find_edge.py  find_curvy_edge
bottom_dist = 0
lane_width_decrement_per_step = 29
default_half_search_width = 150
height_step = 20
steps = 7
min_diff = 8.5  # per pixel height   # 60 px -> diff thresh 600
# find_edge.py  find_edge
default_y1 = -60
min_line_search_half_width = 60
default_right_margin = 300
default_x1 = 379
default_x2 = 679 + 100
min_x1 = default_x1 - 100
default_lane_width = 409


# ACTIONS

# lane_centering.py steer
target_distance = 600 +  50
target_degree = 66

# cruise_control.py change speed
speed_tolerance_up = 6
target_plate_distance = 100
