#!/usr/bin/env bash

#TODO remove this part
export PYTHONPATH="${PYTHONPATH}:/data/exp/kostya/ukr_g2p"
export PYTHONPATH="${PYTHONPATH}:/data/exp/kostya/ukroASR"
UKROASR_ROOT=/data/exp/kostya/ukroASR

num_jobs=8

echo "$0 $@"  # Print the command line for logging

. utils/parse_options.sh

if [ $# -ne 3 ]; then
  echo "Usage: prepare_lang.sh <src-dict-dir> <lm-path> <out-dict-dir>"
  echo "<src-dict-dir> should contain the following files:"
  echo " extra_questions.txt  nonsilence_phones.txt  optional_silence.txt  silence_phones.txt"
  echo "options: "
  echo "     --num-jobs <number of jobs>                     # default: 1."
  exit 1;
fi

src_dict_dir=$1
lm_path=$2
out_dict_dir=$3

# check src-dict-dir
if [ ! -f "$src_dict_dir/silence_phones.txt" ] || [ ! -f "$src_dict_dir/nonsilence_phones.txt" ] || \
   [ ! -f "$src_dict_dir/optional_silence.txt" ] || [ ! -f "$src_dict_dir/extra_questions.txt" ]; then
  echo "$0: <src-dict-dir>  $src_dict_dir does not contain all required files"
  exit 1
fi

# check lm exists
if [ ! -f "$lm_path" ]; then
  echo "$0: <lm-path>  $lm_path expected to exist"
  exit 1
fi

# create out dir
mkdir -p $out_dict_dir

# copy all needed files
for file in $src_dict_dir/silence_phones.txt \
            $src_dict_dir/nonsilence_phones.txt \
            $src_dict_dir/optional_silence.txt \
            $src_dict_dir/extra_questions.txt; do
  cp $file $out_dict_dir
done

# generating vocabulary out of lm
ngram -lm $lm_path -write_vocab $out_dict_dir/vocab

# generating lexicon file
python3.6 $UKROASR_ROOT/tools/gen_lexicon.py -v $dict_dir/vocab -o $dict_dir/lexicon.txt -nj $nj

# extend lexicon with silence phones
echo '!SIL SIL' >> $dict_dir/lexicon.txt
echo '<SPOKEN_NOISE> SPN' >> $dict_dir/lexicon.txt
echo '<UNK> SPN' >> $dict_dir/lexicon.txt
echo '<NOISE> NSN' >> $dict_dir/lexicon.txt
