import json
import pandas as pd

yt_data = pd.read_csv('./data/movies_metadata.csv')
yt_data = yt_data[~yt_data['got_frame_coord'].isna()]
yt_data = yt_data[yt_data['got_frame_coord'] != 'do wyrzucenia']
yt_data.groupby('episode').apply(lambda x: dict(zip(x['video_id'], x['got_frame_coord'])))

yt_json = yt_data.groupby('episode').apply(lambda x: dict(zip(x['video_id'], x['got_frame_coord'])))

with open('./data/movies_metadata.json', 'w') as f:
    json.dump(dict(yt_json), f, sort_keys=True, indent=2)

