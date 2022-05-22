import math
import time
import keyboard

from CONFIG.config import target_distance, Keys, tolerance, min_diff, target_degree


def steer(distance, degree, last_distance, edge_found_status, simulate=False):
    if not edge_found_status:
        return None, 0, 0, 0, 0
    if last_distance is not None:
        change_dist = distance - last_distance
    else:
        change_dist = 0
    deviation = distance - target_distance
    # if abs(deviation) < 50:
    # deviation = 0.02 * deviation * deviation * math.copysign(1, deviation)
    deviation_deg = degree - target_degree

    # # coefficients when saving images
    # dist_correction = deviation * 1 / 1000
    # degree_correction = 0#deviation_deg * 2 / 1000
    # change_correction = change_dist * 4 / 1000

    # coefficients when not saving images
    # dist_correction = 0.0001 * deviation
    dist_correction = 3e-6 * deviation * deviation * math.copysign(1, deviation)
    degree_correction = 0  # deviation_deg * 2 / 1000
    change_correction = 0.001 * change_dist
    # if abs(change_dist) < 6.25:
    #     change_correction = 0.08 * change_dist * 4 / 1000 * change_dist * math.copysign(1, change_dist)
    # else:
    #     change_correction = 0.004 * change_dist - 0.025 + 2e-7
    # change_correction *= 2  # 20220521

    correction = dist_correction + degree_correction + change_correction
    time_s = min(abs(correction), 0.08)

    if correction > 0:
        direction_key = Keys.right
    else:
        direction_key = Keys.left
    if not simulate:
        keyboard.press(direction_key)
        # time.sleep(time_s)
        # keyboard.release(direction_key)
        keyboard.call_later(keyboard.release, direction_key, time_s)
    return direction_key, time_s, dist_correction, degree_correction, change_correction
