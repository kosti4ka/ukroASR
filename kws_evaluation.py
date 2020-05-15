from pathlib import Path
import argparse

def evaluate_ctm(ref_ctm, hyp_ctm, word):

    print(word)

    # setting paths
    ref_ctm_path = Path(ref_ctm)
    hyp_ctm_path = Path(hyp_ctm)

    # read ctm files
    ref_ctm = [x.split() for x in open(ref_ctm_path, 'r', encoding='utf-8').read().split('\n') if x]
    ref_ctm = [{'segment_id': s[0], 'channel': s[1], 'start': float(s[2]), 'duration': float(s[3]), 'word': s[4].lower()}
                    for s in ref_ctm if s[4].lower() == word.lower()]

    hyp_ctm = [x.split() for x in open(hyp_ctm_path, 'r', encoding='utf-8').read().split('\n') if x]
    hyp_ctm = [{'segment_id': s[0], 'channel': s[1], 'start': float(s[2]), 'duration': float(s[3]), 'word': s[4].lower()}
                    for s in hyp_ctm if s[4].lower() == word.lower()]

    tp = 0
    fp = 0
    fn = 0

    for ref_w in ref_ctm:
        w_found = False
        for hyp_w in hyp_ctm:
            if ref_w['segment_id'] == hyp_w['segment_id']:
                if abs(hyp_w['start'] - ref_w['start']) < hyp_w['duration']:
                    tp += 1
                    w_found = True
        if not w_found:
            fn += 1

    for hyp_w in hyp_ctm:
        w_found = False
        for ref_w in ref_ctm:
            if ref_w['segment_id'] == hyp_w['segment_id']:
                if abs(hyp_w['start'] - ref_w['start']) < hyp_w['duration']:
                    w_found = True
        if not w_found:
            fp += 1


    print(f'TP {tp}\n')
    print(f'FP {fp}\n')
    print(f'FN {fn}\n')


if __name__ == '__main__':
    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-ref', '--ref_ctm_path', required=True, type=Path,
                        help='Path to ref ctm file')
    parser.add_argument('-hyp', '--hyp_ctm_path', required=True, type=Path,
                        help='Path to hyp ctm file')
    parser.add_argument('-hw', '--hot_word', required=True, type=str,
                        help='Hot word to be detected')

    # parse
    script_args = parser.parse_args()

    evaluate_ctm(script_args.ref_ctm_path, script_args.hyp_ctm_path, script_args.hot_word)
