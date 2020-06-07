import subprocess
import argparse


def compute_cmvn_stats(data_dir, log_dir, cmvn_dir):
    subprocess.run(f'cd $KALDI_ROOT/egs/wsj/s5; . ./path.sh; . ./cmd.sh; '
                   f'steps/compute_cmvn_stats.sh {data_dir} {log_dir} {cmvn_dir}',
                   shell=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir_path', help='Path to the kaldi data dir')
    parser.add_argument('log_dir_path', help='Path to the log dir')
    parser.add_argument('cmvn_dir_path', help='Path to the mfcc dir')

    args = parser.parse_args()

    compute_cmvn_stats(args.data_dir_path, args.log_dir_path, args.cmvn_dir_path)