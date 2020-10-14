from pathlib import Path
from collections import defaultdict
import operator
import argparse


def convert_ctm_to_whole(in_ctm_path, segments_path, out_ctm_path):
    """
    Converts ctm file with segmets relative times to the ctm with absolute times
    :param in_ctm_path: a path to the initial ctm file
    :param segments_path: a path to the segments file
    :param out_ctm_path: the output ctm file
    :return:
    """

    # setting paths
    in_ctm_path = Path(in_ctm_path)
    segments_path = Path(segments_path)
    out_ctm_path = Path(out_ctm_path)

    # read segments file
    segments = [x.split() for x in open(segments_path, 'r', encoding='utf-8').read().split('\n') if x]
    segments = {s[0]: {'audio_id':s[1], 'start':float(s[2]), 'end':float(s[3])} for s in segments}

    # read ctm file
    in_ctm = [x.split() for x in open(in_ctm_path, 'r', encoding='utf-8').read().split('\n') if x]
    in_ctm = [{'segment_id':s[0], 'channel':s[1], 'start': float(s[2]), 'duration':float(s[3]), 'phone':s[4]} for s in in_ctm]

    out_ctm = []
    for c in in_ctm:
        out_ctm.append({'audio_id': segments[c['segment_id']]['audio_id'], 'channel': c['channel'],
                        'start': round(c['start'] + segments[c['segment_id']]['start'], 2),
                        'duration': c['duration'], 'phone': c['phone']})

    with open(out_ctm_path, 'w', encoding='utf-8') as f:
        for c in out_ctm:
            f.write(f'{c["audio_id"]} {c["channel"]} {c["start"]} {c["duration"]} {c["phone"]}\n')


def ctm_to_word_stat(in_ctm_path):
    """
    Generate words statistic out of ctm file
    :param in_ctm_path: a path to the initial ctm file
    :return:
    """

    # setting paths
    in_ctm_path = Path(in_ctm_path)

    # read ctm file
    in_ctm = [x.split() for x in open(in_ctm_path, 'r', encoding='utf-8').read().split('\n') if x]
    in_ctm = [{'segment_id': s[0], 'channel': s[1], 'start': float(s[2]), 'duration': float(s[3]), 'word': s[4]} for s
              in in_ctm]

    words = defaultdict(int)

    for c in in_ctm:
        words[c["word"]] += 1

    sorted_words = sorted(words.items(), key=operator.itemgetter(1), reverse=True)

    print('ok')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_ctm', help='path to the input ctm file', required=True)
    parser.add_argument('-s', '--segments', help='path to the segments file', required=True)
    parser.add_argument('-o', '--out_ctm', help='path to the output ctm file', required=True)

    args = parser.parse_args()

    convert_ctm_to_whole(args.input_ctm, args.segments, args.out_ctm)
