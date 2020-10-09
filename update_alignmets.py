import subprocess
from pathlib import Path
from tools.utils import get_list
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.textfile import TextFile, TextFragment
from aeneas.language import Language
import json
import uuid

REALIGN_THRESHOLD = 40

# anchor_dict = {
#     32:273,
#     109:939,
#     127:1174,
#     275:2473,
#     362:3594,
#     485:5503,
#     566:6665,
#     804:10132,
#     1017:13561,
#     1079:14444
# } # python numbers
# total_lines = 1171
# total_len = 15558
in_audio = "/Users/mac/Datasets/ukrodataset/audiobooks/prokopchuk_ozernii_viter/prokopchuk_ozernii_viter.wav"
# in_text = '/Users/mac/Datasets/ukrainian/nestaiko/nestaiko_2.txt'
original_json = "/Users/mac/Datasets/ukrodataset/audiobooks/prokopchuk_ozernii_viter/prokopchuk_ozernii_viter.json"
current_json = '/Users/mac/Downloads/tuned (6).json'
out_json = "/Users/mac/Datasets/ukrodataset/audiobooks/prokopchuk_ozernii_viter/prokopchuk_ozernii_viter.json"

# init work dir
tmp_dir = Path('/tmp/work_dir')
tmp_dir.mkdir(parents=True, exist_ok=True)

# parts = []
# current_line = 0
# current_time = 0
# for k in anchor_dict:
#     parts.append((current_line, k + 1, current_time, anchor_dict[k]))
#     current_line = k + 1
#     current_time = anchor_dict[k]
# parts.append((current_line, total_lines, current_time, total_len))


original_j = json.load(open(original_json, 'r', encoding='utf8'))
current_j = json.load(open(current_json, 'r', encoding='utf8'))


# generate a dictionary of utterances by utt_id
out_j = {'fragments':[]}
begin_fixed = False
end_fixed = False
segments_to_align = []
current_text_to_align = []
curent_start_to_align = None
curent_end_to_align = None

for f_original, f_current in zip(original_j['fragments'], current_j['fragments']):
    assert f_original['id'] == f_current['id']
    utt_id = f_current['id']
    lines = f_current['lines']
    if round(float(f_original['begin']), 3) != round(float(f_current['begin']), 3) or '<<<<<<<<<' in lines:
        begin_fixed = True
        if '<<<<<<<<<' not in lines:
            lines = ['<<<<<<<<<'] + lines
    if round(float(f_original['end']), 3) != round(float(f_current['end']), 3) or '>>>>>>>>>' in lines:
        end_fixed = True
        if '>>>>>>>>>' not in lines:
            lines = lines + ['>>>>>>>>>']

    out_j['fragments'].append({'id':utt_id,
                               'begin':float(f_current['begin']),
                               'end':float(f_current['end']),
                               'lines':lines
           })

    if begin_fixed and not end_fixed:
        curent_start_to_align = round(float(f_current['begin']),3)
        current_text_to_align.append((utt_id, lines[1]))

    if not begin_fixed and not end_fixed:
        current_text_to_align.append((utt_id, lines[0]))

    if not begin_fixed and end_fixed:
        curent_end_to_align = round(float(f_current['end']), 3)
        current_text_to_align.append((utt_id, lines[0]))
        if len(current_text_to_align) > REALIGN_THRESHOLD:
            segments_to_align.append({'start': curent_start_to_align,
                                      'end': curent_end_to_align,
                                      'lines': current_text_to_align
            })
        current_text_to_align = []
        curent_start_to_align = None
        curent_end_to_align = None

    begin_fixed = False
    end_fixed = False


# split audio and text into chunks
for segment in segments_to_align:
    # split audio
    audio_segment = tmp_dir / f'audio_segment.wav'
    start_time = segment['start']
    duration = segment['end'] - start_time
    ffmpeg_cmd = f'ffmpeg -y -ss {start_time} -i {in_audio} -t {duration} {audio_segment}'
    subprocess.call(ffmpeg_cmd, shell=True)

    textfile = TextFile()
    for utt_id, text in segment['lines']:
        textfile.add_fragment(TextFragment(utt_id, Language.UKR, [text], [text]))

    align_segment = tmp_dir / f'align_segment.json'
    config_string = 'task_language=ukr'
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_segment
    task.text_file = textfile
    task.sync_map_file_path_absolute = align_segment
    ExecuteTask(task).execute()
    sync_map = task.sync_map_leaves(fragment_type=0)
    # task.output_sync_map_file()
    # j = json.load(open(align_segment, 'r', encoding='utf8'))

    # updating out json with new times
    for fragment in sync_map:
        utt_id = fragment.identifier
        utt_start = float(fragment.begin) + start_time
        utt_end = float(fragment.end) + start_time

        for fragment in out_j['fragments']:
            if fragment['id'] == utt_id:
                # updating timing
                fragment['begin'] = utt_start
                fragment['end'] = utt_end


with open(out_json, 'w') as fp:
    json.dump(out_j, fp)
