window = {
    'left':   0,
    'top':    0,
    'width':  1920,
    'height': 1080
}

window_lc = {
    'left':   600,
    'top':    440,
    'width':  640,
    'height': 210,
}



target_distance = 127
tolerance = 20
min_diff = 6

keys = {
    'left': 'a',
    'right': 'd',
}

x_margin = 200
x_min = 620
x_max = 1211
y_min = 410
y_max = 550
x_size = x_max - x_min
y_size = y_max - y_min

points_before_transform = [
    [0 + x_margin, y_size],
    [955 + x_margin - x_min, 0],
    [1063 + x_margin - x_min, 0],
    [x_size + x_margin, y_size],
]

points_after_transform = [
    [0 + x_margin, y_size],
    [0 + x_margin, 0],
    [x_size + x_margin, 0],
    [x_size + x_margin, y_size],
]

window_crop_margin = {
    'left': x_min - x_margin,
    'top': y_min,
    'width': x_size + 2*x_margin,
    'height': y_size,
}

