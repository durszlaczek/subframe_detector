import math

import cv2
import numpy as np


def detect_lines(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 0, 0)
    lines = cv2.HoughLinesP(edges, 1, math.pi / 2, 2, None, 30, 1)
    if lines is not None:
        lines = [x[0] for x in lines]
    return lines


def filter_lines(lines, top_n=3, min_length=50, max_length=2000):
    line_lengths = [max(abs(line[0] - line[2]), abs(line[1] - line[3])) for line in lines]
    lines = [[y, x] for y, x in sorted(zip(line_lengths, lines), key=lambda pair: pair[0])]

    lines = [val for len, val in lines if
             min_length < len < max_length]

    return lines[-top_n:]


def vertical_horizontal_split(lines):
    horizontal = []
    vertical = []
    for line in lines:
        if is_vertical(line):
            vertical.append(line)
        else:
            horizontal.append(line)

    return horizontal, vertical


def get_xmin(line):
    return min(line[0], line[2])


def get_xmax(line):
    return max(line[0], line[2])


def get_ymin(line):
    return min(line[1], line[3])


def get_ymax(line):
    return max(line[1], line[3])


def get_horizontal_distance(line1, line2):
    """
    Approximate distance
    :param line1:
    :param line2:
    :return:
    """
    return max(abs(get_xmax(line1) - get_xmin(line2)),
               abs(get_xmax(line2) - get_xmin(line1)))


def get_vertical_distance(line1, line2):
    """
    Approximate distance
    :param line1:
    :param line2:
    :return:
    """
    return max(abs(get_ymax(line1) - get_ymin(line2)),
               abs(get_ymax(line2) - get_ymin(line1)))


def is_vertical(line):
    if line[0] == line[2]:  # xmin == xmax
        return True
    return False


def is_subline_horizontal(line, horizontal_line, error=2):
    """

    :param line:
    :param horizontal_line:
    :param error: ... in pixels
    :return:
    """
    if get_vertical_distance(line, horizontal_line) > error:
        return False
    if get_xmax(line) > get_xmax(horizontal_line) + error:
        return False
    if get_xmin(line) < get_xmin(horizontal_line) - error:
        return False

    return True


def is_subline_vertical(line, vertical_line, error=10):
    """

    :param line:
    :param vertical_line:
    :param error: ... in pixels
    :return:
    """

    if get_horizontal_distance(line, vertical_line) > error:
        return False
    if get_ymax(line) > get_ymax(vertical_line) + error:
        # line's bottom end exceeds hor_line's bottom end
        return False
    if get_ymin(line) < get_ymin(vertical_line) - error:
        return False

    return True


def reformat_points(points):
    # points like here: https://www.mobilefish.com/services/record_mouse_coordinates/record_mouse_coordinates.php
    assert len(points) == 4
    x = sorted([p[0] for p in points])
    y = sorted([p[1] for p in points])

    # AAAA! I will die soon...
    # return [
    #     [x[0], y[0], x[2], y[1]],
    #     [x[2], y[1], x[3], y[3]],
    #     [x[0], y[0], x[1], y[2]],
    #     [x[1], y[2], x[3], y[3]]
    # ]
    return [
        [x[0], y[0], x[3], y[0]],
        [x[3], y[0], x[3], y[3]],
        [x[0], y[0], x[0], y[3]],
        [x[0], y[3], x[3], y[3]]
    ]


def reformat_back(lines):
    x = list(np.unique([x[0] for x in lines]))
    y = list(np.unique([x[1] for x in lines]))
    return [x[0], y[0], x[1], y[1]]


def analyze_lines_in_frame(frame, expected_subframe):
    """

    :param frame:
    :param expected_subframe: ((xmin1, ymin1, xmax1, ymin2),
                                (xmax1, ymin2, xmax2, ymax2),
                                (xmin1, ymin1, xmin2, ymax1),
                                (xmin2, ymax1, xmax2, ymax2))
    :return:
    """
    lines_detected = detect_lines(frame)
    height, width = frame.shape[:2]
    if lines_detected:
        horizontal_lines, vertical_lines = vertical_horizontal_split(lines_detected)
        horizontal_lines = filter_lines(horizontal_lines, top_n=5, max_length=width / 2)
        vertical_lines = filter_lines(vertical_lines, top_n=5, max_length=height / 2)
        horizontal_expected, vertical_expected = vertical_horizontal_split(expected_subframe)

        for line in horizontal_lines:
            for expected_line in horizontal_expected:
                if is_subline_horizontal(line, expected_line):
                    return reformat_back(expected_subframe)

        for line in vertical_lines:
            for expected_line in vertical_expected:
                if is_subline_vertical(line, expected_line):
                    return reformat_back(expected_subframe)

    return None


if __name__ == '__main__':
    # This example should work
    frame = cv2.imread('./got_detector/f09.png')
    expected_frame = reformat_points([[130, 120], [268, 122], [273, 197], [131, 198]])
    print(analyze_lines_in_frame(frame, expected_frame))

    # This shouldn't work
    expected_frame = reformat_points([[130, 1000], [268, 1200], [273, 1000], [131, 1200]])
