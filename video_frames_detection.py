import argparse
import os

import av
import cv2
import numpy as np
import pandas as pd

from tqdm import tqdm

from .subframe_detection import analyze_lines_in_frame, reformat_points


def process_video(video_path, outfile, expected_subframe, sample_rate=None,
                  keyframes_only=False):
    expected_subframe = reformat_points(expected_subframe)
    container = av.open(video_path)
    stream = container.streams.video[0]
    frame_rate = None

    if sample_rate:
        frame_rate = round(float(stream.framerate) * sample_rate)

    initial_got_frame = True

    for i, frame in enumerate(tqdm(container.decode(stream))):

        if keyframes_only and not frame.key_frame:
            continue

        elif sample_rate and i % frame_rate != 0:
            continue

        frame = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        got_coords = analyze_lines_in_frame(frame, expected_subframe)
        if got_coords and initial_got_frame:
            subframe = frame[
                       got_coords[1]:got_coords[3],
                       got_coords[0]:got_coords[2]
                       ]
            initial_got_frame = False
            frame_id_start = i
        elif not got_coords and not initial_got_frame:
            cv2.imwrite(outfile + str(frame_id_start) + '-' + str(i) + '.jpg', subframe)
            initial_got_frame = True


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--subframes_data_path')
    parser.add_argument('--outdir')
    parser.add_argument('--movies_dir')

    args = parser.parse_args()

    subframe_data = pd.read_csv(args.subframes_data_path)
    for i, row in subframe_data.iterrows():

        if row['got_frame_coord']:

            try:
                os.mkdir(os.path.join(args.outdir, str(row['video_id'])))
            except FileExistsError:
                print('File {} exists'.format(row['video_id']))
                continue

            try:
                points = eval(row['got_frame_coord'])
            except Exception as e:
                print('Something wrong with subframe definition')

            process_video(args.movies_dir + '/' + str(row['video_id']) + '.mp4',
                          os.path.join(args.outdir, str(row['video_id'])),
                          points, keyframes_only=True)
