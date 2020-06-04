import subprocess
import argparse


def make_mfcc(data_dir):
    subprocess.run(f'cd $KALDI_ROOT/egs/wsj/s5; . ./path.sh; . ./cmd.sh; '
                   f'steps/make_mfcc.sh {data_dir}',
                   shell=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir_path', help='Path to the kaldi data dir')

    args = parser.parse_args()

    make_mfcc(args.data_dir_path)