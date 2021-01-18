window = {
    'left':   600,
    'top':    400,
    'width':  980,
    'height': 220,
}

window_speed = {
    'left':   1496,
    'top':    710,
    'width':  30,
    'height': 18,
}

window_signs = {
    'left':   1000,
    'top':    250,
    'width':  600,
    'height': 250,
}

ref_digits_path = r'C:\PROGRAMOWANIE\auto_data\photos\ref_digits'

# find_edge
default_x1 = 379
default_x2 = 679
default_y1 = -60

min_diff = 600

target_distance = 600
target_degree = 66
tolerance = 10

keys = {
    'left': 'a',
    'right': 'd',
    'up': 'w',
    'down': 's',
}
speed_tolerance_up = 5

x_margin = 200
x_min = 620
x_max = 1211
y_min = 410
y_max = 550
x_size = x_max - x_min
y_size = y_max - y_min

points_before_transform = [
    [172, y_size],
    [460, 0],
    [573, 0],
    [746, y_size],
]

points_after_transform = [
    [172, y_size],
    [172, 0],
    [746, 0],
    [746, y_size],
]

window_crop_margin = {
    'left': x_min - x_margin,
    'top': y_min,
    'width': x_size + 2*x_margin,
    'height': y_size,
}
