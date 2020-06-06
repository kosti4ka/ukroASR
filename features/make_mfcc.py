import subprocess
import argparse


def make_mfcc(data_dir, mfcc_dir, log_dir):
    subprocess.run(f'cd $KALDI_ROOT/egs/wsj/s5; . ./path.sh; . ./cmd.sh; '
                   f'steps/make_mfcc.sh {data_dir} {log_dir} {mfcc_dir}',
                   shell=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir_path', help='Path to the kaldi data dir')
    parser.add_argument('log_dir_path', help='Path to the log dir')
    parser.add_argument('mfcc_dir_path', help='Path to the mfcc dir')

    args = parser.parse_args()

    make_mfcc(args.data_dir_path, args.log_dir_path, args.mfcc_dir_path)