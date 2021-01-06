from mss import mss


def capture_image(window):
    screenshot = mss().grab(window)
    return screenshot
