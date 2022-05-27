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
