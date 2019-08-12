from pathlib import Path


def ctm_to_labels(in_ctm_path, a_labels_path):
    """
    Converts ctm file the audacity labels
    :param in_ctm_path: a path to the ctm file
    :param a_labels_path: out audacity labels path
    :return:
    """

    # setting paths
    in_ctm_path = Path(in_ctm_path)
    a_labels_path = Path(a_labels_path)

    # read ctm file
    in_ctm = [x.split() for x in open(in_ctm_path, 'r').read().split('\n') if x]
    in_ctm = [{'audio_id': s[0], 'channel': s[1], 'start': float(s[2]), 'duration': float(s[3]), 'phone': s[4]} for s
              in in_ctm]

    a_labels = []
    for c in in_ctm:
        a_labels.append({'start': c['start'], 'end': round(c['start'] + c['duration'], 2),
                        'label': c['phone']})

    with open(a_labels_path, 'w', encoding='utf-8') as f:
        for l in a_labels:
            f.write(f'{l["start"]} {l["end"]} {l["label"]}\n')


if __name__ == '__main__':
    ctm_to_labels('/home/ubuntu/kostya/zapovit_small/exp/mono_ali/1.whole.ctm',
                  '/home/ubuntu/kostya/zapovit_small/exp/mono_ali/labels')