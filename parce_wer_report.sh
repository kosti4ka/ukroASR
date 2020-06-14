#!/usr/bin/env bash

cd $KALDI_ROOT/egs/wsj/s5
. ./path.sh
. ./cmd.sh
. utils/parse_options.sh

wer_report=$1
metric=$2

echo {\'WER\': $(cat $wer_report | awk '{print $2}')} > $metric
