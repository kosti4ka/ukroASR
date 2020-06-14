#!/usr/bin/env bash

export PYTHONPATH="${PYTHONPATH}:/data/exp/kostya/ukr_g2p"
export PYTHONPATH="${PYTHONPATH}:/data/exp/kostya/ukroASR"
UKROASR_ROOT=/data/exp/kostya/ukroASR

cd $KALDI_ROOT/egs/wsj/s5
. ./path.sh
. ./cmd.sh
. utils/parse_options.sh

data_dir=$1
dict_dir=$2

# generating vocabluary
python3.6 $UKROASR_ROOT/tools/gen_vocab.py -t $data_dir/text -v $dict_dir/vocab

# generating lexicon file
python3.6 $UKROASR_ROOT/tools/gen_lexicon.py -v $dict_dir/vocab -o $dict_dir/lexicon.txt

# extend lexicon with silence phones
echo '!SIL SIL' >> $dict_dir/lexicon.txt
echo '<SPOKEN_NOISE> SPN' >> $dict_dir/lexicon.txt
echo '<UNK> SPN' >> $dict_dir/lexicon.txt
echo '<NOISE> NSN' >> $dict_dir/lexicon.txt