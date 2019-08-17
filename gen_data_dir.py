import json
from pathlib import Path
import os
from normilize import normilize_line
from collections import defaultdict

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
            if normilize:
                utt_text = normilize_line(f['lines'][0])
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
            wav_f.write(f'{audio_id} {audios[audio_id]}')

    with open(utt2spk, 'w', encoding='utf-8') as utt2spk_f, \
            open(segments, 'w', encoding='utf-8') as segments_f, \
            open(text, 'w', encoding='utf-8') as text_f:
        for utt_id in utts:
            utt2spk_f.write(f'{utt_id} {utts[utt_id]["speaker"]}\n')
            segments_f.write(f'{utt_id} {audio_id} {utts[utt_id]["start"]} {utts[utt_id]["end"]}\n')
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


if __name__ == '__main__':
    aeneas_json2kaldi_data(['/Users/mac/Datasets/ukrainian/glibov/002_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/003_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/004_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/005_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/006_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/007_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/008_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/009_tuned.json',
                            '/Users/mac/Datasets/ukrainian/glibov/056_tuned.json'],
                           ['/Users/mac/Datasets/ukrainian/glibov/media/002.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/003.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/004.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/005.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/006.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/007.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/008.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/009.wav',
                            '/Users/mac/Datasets/ukrainian/glibov/media/056.wav'],
                           '/Users/mac/Datasets/ukrainian/glibov/data',
                           rewrite=True)
    # text_with_unk('/Users/mac/Datasets/ukrainian/glibov/data/text',
    #               '/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #               '/Users/mac/Datasets/ukrainian/glibov/data/text_unk')