import argparse
import json

import cv2
import numpy as np


def dhash(image, hashSize=8):
    # resize the input image, adding a single column (width) so we
    # can compute the horizontal gradient
    resized = cv2.resize(image, (hashSize + 1, hashSize))

    # compute the (relative) horizontal gradient between adjacent
    # column pixels
    diff = resized[:, 1:] > resized[:, :-1]

    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def bitfield(n, size=None):
    if isinstance(n, str):
        n = int(n)

    bits = [1 if digit == '1' else 0 for digit in bin(n)[2:]]

    if size and len(bits) < size:
        template = [0] * size
        template[-len(bits):] = bits
        bits = template
    return bits


def hamming_distances(hashes_master, hash_query):
    distances = np.sum(np.bitwise_xor(hashes_master, hash_query),
                       axis=1)
    return distances


def dict_to_arrays(info_dict, hash_size=64):
    keys = []
    vals = []

    for i, (key, val) in enumerate(info_dict.items()):
        keys.append(bitfield(key, hash_size))
        vals.append(val)

    return np.asarray(keys), np.asarray(vals)


def frame_to_time(query_image, v_dict_keys, v_dict_vals, threshold=20):

    # Assumes RGB array
    query_img = cv2.cvtColor(query_image, cv2.COLOR_RGB2GRAY)
    query_img_hash = dhash(query_img)
    query_img_hash = bitfield(query_img_hash, 64)

    distances = hamming_distances(v_dict_keys, query_img_hash)

    if np.min(distances) > threshold:
        return None

    scene_time = v_dict_vals[np.argmin(distances)]

    return scene_time


def seconds_to_time(time_seconds):
    minutes = int(np.floor(time_seconds / 60))
    seconds = time_seconds % 60

    return minutes, seconds


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hashed_video_path",
                    required=True,
                    help="Path to the hashed video file.")
    ap.add_argument("--query_image_path")

    return ap.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    with open(args.hashed_video_path, 'r') as f:
        info_dict = json.load(f)

    keys, vals = dict_to_arrays(info_dict)

    image = cv2.imread(args.query_image_path)
    scene_time = frame_to_time(image, keys, vals)

    minutes, seconds = seconds_to_time(scene_time)
    print("The frame appeared at {}:{}".format(minutes, seconds))
