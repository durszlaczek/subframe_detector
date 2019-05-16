import json
import os
from collections import defaultdict

from got_matcher.searcher import dict_to_arrays, frame_to_time
from got_matcher.video_frames_detection import get_got_frames

if __name__ == '__main__':
    with open('./data/movies_metadata.json', 'r') as f:
        yt_info = json.load(f)  # {episode: {{'id': subframe}, ...}, ...}
    info_path = '/Users/aga/Documents/Projects/subframe_detector/data'
    videos_path = '/Users/aga/Documents/Projects/ai_got/data/movies/8th_season'

    result = defaultdict()

    for episode in range(1, 6):
        episode_yt_info = yt_info[str(episode) + '.0']

        with open(os.path.join(info_path, '8_{}.json'.format(str(episode))), 'r') as f:
            episode_info = json.load(f)

        keys, vals = dict_to_arrays(episode_info)

        result[episode] = defaultdict()

        for video_id in episode_yt_info:
            current_time = 0
            if video_id == 4:
                print('4')
                continue
            video_path = os.path.join(videos_path, str(video_id) + '.mp4')
            try:
                subframe_expected = eval(episode_yt_info[video_id])
            except:
                print(video_id, 'Something wrong with the frame.')
            got_keyframes = get_got_frames(video_path,
                                           subframe_expected,
                                           keyframes_only=True)
            result[episode][video_id] = []
            if got_keyframes:
                for got_keyframe, frame_id in got_keyframes:
                    scene_time = frame_to_time(got_keyframe, keys, vals)
                    if scene_time and scene_time > current_time:
                        # minutes, seconds = seconds_to_time(scene_time)
                        result[episode][video_id].append({'got_scene_time': scene_time,
                                                          'yt_scene_time': frame_id})
                        current_time = scene_time
                    else:
                        continue

            with open('./data/results.json', 'w') as f:
                json.dump(dict(result), f, sort_keys=True, indent=2)

