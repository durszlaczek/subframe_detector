import av
import cv2
import numpy as np

from tqdm import tqdm

from got_matcher.subframe_detection import analyze_lines_in_frame, reformat_points


def get_got_frames(video_path, expected_subframe, sample_rate=None,
                   keyframes_only=False):
    expected_subframe = reformat_points(expected_subframe)
    container = av.open(video_path)
    stream = container.streams.video[0]
    frame_rate = None

    if sample_rate:
        frame_rate = round(float(stream.framerate) * sample_rate)

    # initial_got_frame = True
    got_frames = []

    for i, frame in enumerate(tqdm(container.decode(stream))):
        frame_time = float(frame.pts * stream.time_base)

        if keyframes_only and not frame.key_frame:
            continue

        elif sample_rate and i % frame_rate != 0:
            continue

        frame = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        got_coords = analyze_lines_in_frame(frame, expected_subframe)
        if got_coords:
            subframe = frame[
                       got_coords[1]:got_coords[3],
                       got_coords[0]:got_coords[2]
                       ]
            got_frames.append((subframe, frame_time))

    return got_frames
