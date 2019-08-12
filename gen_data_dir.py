import json
from pathlib import Path
import os
from normilize import normilize_line

def aeneas_json2kaldi_data(aeneas_json_path, audio_path, out_data_dir, normilize=True, rewrite=False):
    """
    Generates a kaldi data dir from the aeneas json.
    :param aeneas_json_path: a path to a aeneas json
    :param out_data_dir: the output data dir
    :return:
    """

    # setting paths
    aeneas_json_path = Path(aeneas_json_path)
    audio_path = Path(audio_path)
    out_data_dir = Path(out_data_dir)

    if not rewrite:
        assert not out_data_dir.exists(), f'data dir in {out_data_dir} already exists!'

    # parse json
    j = json.load(open(aeneas_json_path, 'r', encoding='utf8'))

    # generate audi_id
    audio_id = audio_path.stem

    # generate a dictionary of utterances by utt_id
    utts = {}
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
        wav_f.write(f'{audio_id} {audio_path}')

    with open(utt2spk, 'w', encoding='utf-8') as utt2spk_f, \
            open(segments, 'w', encoding='utf-8') as segments_f, \
            open(text, 'w', encoding='utf-8') as text_f:
        for utt_id in utts:
            utt2spk_f.write(f'{utt_id} {utts[utt_id]["speaker"]}\n')
            segments_f.write(f'{utt_id} {audio_id} {utts[utt_id]["start"]} {utts[utt_id]["end"]}\n')
            text_f.write(f'{utt_id} {utts[utt_id]["text"]}\n')


if __name__ == '__main__':
    aeneas_json2kaldi_data('/Users/mac/Datasets/ukrainian/prychynna/prychynna_tuned.json',
                           '/Users/mac/Datasets/ukrainian/prychynna/prychynna.wav',
                           '/Users/mac/Datasets/ukrainian/prychynna/data',
                           rewrite=True)