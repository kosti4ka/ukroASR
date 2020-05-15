import subprocess
from pathlib import Path
from tools.utils import get_list
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import json
import uuid

anchor_dict = {
    32:273,
    109:939,
    127:1174,
    275:2473,
    362:3594,
    485:5503,
    566:6665,
    804:10132,
    1017:13561,
    1079:14444
}
total_lines = 1171
total_len = 15558
in_audio = '/Users/mac/Datasets/ukrainian/nestaiko/nestaiko_1.wav'
in_text = '/Users/mac/Datasets/ukrainian/nestaiko/nestaiko_1.txt'
out_json = '/Users/mac/Datasets/ukrainian/nestaiko/nestaiko_1.json'

parts = []
current_line = 0
current_time = 0
for k in anchor_dict:
    parts.append((current_line, k + 1, current_time, anchor_dict[k]))
    current_line = k + 1
    current_time = anchor_dict[k]
parts.append((current_line, total_lines, current_time, total_len))

# init work dir
tmp_dir = Path('/tmp/work_dir')
tmp_dir.mkdir(parents=True, exist_ok=True)

# read text files
text = get_list(in_text)

# split audio and text into chunks
# for i, part in enumerate(parts):
#     # split audio
#     out_audio = tmp_dir / f'{i}.wav'
#     start_time = part[2]
#     duration = part[3] - start_time
#     ffmpeg_cmd = f'ffmpeg -y -ss {start_time} -i {in_audio} -t {duration} {out_audio}'
#     subprocess.call(ffmpeg_cmd, shell=True)
#
#     # split text
#     text_i = text[part[0]:part[1]]
#     out_text = tmp_dir / f'{i}.txt'
#     with open(out_text, 'w') as text_f:
#         for l in text_i:
#             text_f.write(f'{l}\n')
#
#     out_alignent = tmp_dir / f'{i}.json'
#     config_string = 'task_language=rus|is_text_type=plain|os_task_file_format=json'
#     task = Task(config_string=config_string)
#     task.audio_file_path_absolute = out_audio
#     task.text_file_path_absolute = out_text
#     task.sync_map_file_path_absolute = out_alignent
#     ExecuteTask(task).execute()
#     task.output_sync_map_file()

# combining jsons
resulting_alignment = {'fragments':[]}
for i, part in enumerate(parts):

    out_alignent = tmp_dir / f'{i}.json'
    j = json.load(open(out_alignent, 'r', encoding='utf8'))

    # generate a dictionary of utterances by utt_id
    for f in j['fragments']:
        utt_id = str(uuid.uuid4())
        utt_start = float(f['begin']) + part[2]
        utt_end = float(f['end']) + part[2]

        utt = {'id':utt_id,
               'begin':utt_start,
               'end':utt_end,
               'lines':f['lines']
               }
        resulting_alignment['fragments'].append(utt)

with open(out_json, 'w') as fp:
    json.dump(resulting_alignment, fp)
