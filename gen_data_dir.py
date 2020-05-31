import json
from pathlib import Path
import os
from normilize import normilize_line
from collections import defaultdict
import argparse
import pandas as pd

MIN_UTT_DURATION = 0.4


def gen_data_dir(csv_path, out_data_path, normilize=True):
    """
    Generates a kaldi data dir out of csv with data.
    :param csv_path: path to the csv file with data
    :param out_data_path: path to the output kaldi data dir
    :param normilize: normilize text
    :return:
    """

    # setting paths
    csv_path = Path(csv_path)
    out_data_path = Path(out_data_path)
    utt2spk_path = out_data_path / 'utt2spk'
    spk2utt_path = out_data_path / 'spk2utt'
    segments_path = out_data_path / 'segments'
    text_path = out_data_path / 'text'
    wav_scp_path = out_data_path / 'wav.scp'
    parent_wav_path = csv_path.parent

    # make data dir
    out_data_path.mkdir(parents=True, exist_ok=True)

    # reading data
    df = pd.read_csv(csv_path)

    # init wav scp and spk2utt
    wav_scp = []
    spk2utt = defaultdict(list)

    with open(utt2spk_path, 'w', encoding='utf-8') as utt2spk_f, \
            open(segments_path, 'w', encoding='utf-8') as segments_f, \
            open(text_path, 'w', encoding='utf-8') as text_f:
        for index, row in df.iterrows():
            text = normilize_line(row["text"]) if normilize else row["text"]
            utt_start = row["utt_start"]
            utt_end = row["utt_end"]
            utt_id = row["utt_id"]
            spk_id = row["spk_id"]
            audio_id = row["audio_id"]
            if utt_end - utt_start > MIN_UTT_DURATION:
                utt2spk_f.write(f'{utt_id} {spk_id}\n')
                segments_f.write(f'{utt_id} {audio_id} {utt_start} {utt_end}\n')
                text_f.write(f'{utt_id} {text}\n')
                wav_scp.append((audio_id, parent_wav_path / row["audio_path"]))
                spk2utt[utt_id].append(utt_id)

    # save utt2spk
    with open(spk2utt_path, 'w', encoding='utf-8') as spk2utt_f:
        for spk_id in spk2utt:
            spk2utt_f.write(f'{spk_id} {" ".join(spk2utt[spk_id])}\n')

    # save wav scp
    wav_scp = list(set(wav_scp))
    with open(wav_scp_path, 'w', encoding='utf-8') as wav_scp_f:
        for audio in wav_scp:
            wav_scp_f.write(f'{audio[0]} {audio[1]}\n')


def aeneas_json2kaldi_data(aeneas_json_paths, audio_paths, out_data_dir, normilize=True, rewrite=False):
    """
    Generates a kaldi data dir from the aeneas json.
    :param aeneas_json_paths: list of paths to a aeneas jsons
    :param audio_paths: list of paths to the corresponding wav files
    :param out_data_dir: the output data dir
    :return:
    """

    # setting paths
    aeneas_json_paths = [Path(path) for path in aeneas_json_paths]
    audio_paths = [Path(path) for path in audio_paths]
    out_data_dir = Path(out_data_dir)

    if not rewrite:
        assert not out_data_dir.exists(), f'data dir in {out_data_dir} already exists!'

    utts = {}
    audios = {}
    for json_path, audio_path in zip(aeneas_json_paths,audio_paths):
        # parse json
        j = json.load(open(json_path, 'r', encoding='utf8'))

        # generate audi_id
        audio_id = audio_path.stem
        audios[audio_id] = audio_path

        # generate a dictionary of utterances by utt_id
        for f in j['fragments']:
            # generate utterance
            utt_start = float(f['begin'])
            utt_end = float(f['end'])
            utt_spk = audio_id
            utt_id = f'{audio_id}-{str(int(utt_start * 100)).zfill(7)}-{str(int(utt_end * 100)).zfill(7)}'
            line = [l for l in f['lines'] if l not in ['<<<<<<<<<','>>>>>>>>>']][0]
            if normilize:
                utt_text = normilize_line(line)
            else:
                utt_text = f['lines'][0]

            utts[utt_id] = {'id': utt_id,
                            'audio_id': audio_id,
                            'start': round(utt_start, 2),
                            'end': round(utt_end, 2),
                            'speaker': utt_spk,
                            'text': utt_text}

    # set filenames
    wav_scp = out_data_dir / 'wav.scp'
    utt2spk = out_data_dir / 'utt2spk'
    segments = out_data_dir / 'segments'
    text = out_data_dir / 'text'

    # make dir
    if not out_data_dir.exists():
        os.makedirs(str(out_data_dir))

    with open(wav_scp, 'w', encoding='utf-8') as wav_f:
        for audio_id in audios:
            wav_f.write(f'{audio_id} {audios[audio_id]}\n')

    with open(utt2spk, 'w', encoding='utf-8') as utt2spk_f, \
            open(segments, 'w', encoding='utf-8') as segments_f, \
            open(text, 'w', encoding='utf-8') as text_f:
        for utt_id in utts:
            utt2spk_f.write(f'{utt_id} {utts[utt_id]["audio_id"]}\n')
            segments_f.write(f'{utt_id} {utts[utt_id]["audio_id"]} {utts[utt_id]["start"]} {utts[utt_id]["end"]}\n')
            text_f.write(f'{utt_id} {utts[utt_id]["text"]}\n')


def text_with_unk(text_path, lexicon_path, out_text_path):

    # setting paths
    text_path = Path(text_path)
    lexicon_path = Path(lexicon_path)
    out_text_path = Path(out_text_path)

    # read text
    text = [x.split() for x in open(text_path, 'r', encoding='utf-8').read().split('\n') if x]

    # read lexicon
    lexicon = defaultdict(list)
    [lexicon[x.split()[0]].append(x.split()[1:]) for x in open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if x]

    with open(out_text_path, 'w', encoding='utf-8') as f:
        for line in text:
            f.write(f'{line[0]}')
            for word in line[1:]:
                f.write(f' {word}') if word in lexicon else f.write(f' <UNK>')
            f.write(f'\n')


def text2plane(texts_list, out_text_file):

    out_text_file = Path(out_text_file)

    with open(out_text_file, 'w', encoding='utf-8') as out_text:

        for text_file in texts_list:
            f = open(text_file, "r")
            lines = list(f)
            f.close()

            for line in lines:
                utt_text = normilize_line(line)
                out_text.write(f'{utt_text}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_path', help='Path to the csv file with data')
    parser.add_argument('out_data_path', help='Path to the output data dir')

    args = parser.parse_args()

    gen_data_dir(args.csv_path, args.out_data_path)