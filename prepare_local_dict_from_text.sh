#!/usr/bin/env bash

export PYTHONPATH="${PYTHONPATH}:/data/exp/kostya/ukr_g2p"
export PYTHONPATH="${PYTHONPATH}:/data/exp/kostya/ukroASR"
UKROASR_ROOT=/data/exp/kostya/ukroASR

nj=1

echo "$0 $@"  # Print the command line for logging

. utils/parse_options.sh

if [ $# -ne 3 ]; then
  echo "Usage: prepare_local_dict_from_text.sh <src-dict-dir> <out-dict-dir> <text-path-1> <text-path-1> ..."
  echo "<src-dict-dir> should contain the following files:"
  echo " extra_questions.txt  nonsilence_phones.txt  optional_silence.txt  silence_phones.txt"
  echo "options: "
  echo "     -nj <number of jobs>                     # default: 1."
  exit 1;
fi

src_dict_dir=$1
out_dict_dir=$2
shift;
shift;

# check src-dict-dir
if [ ! -f "$src_dict_dir/silence_phones.txt" ] || [ ! -f "$src_dict_dir/nonsilence_phones.txt" ] || \
   [ ! -f "$src_dict_dir/optional_silence.txt" ] || [ ! -f "$src_dict_dir/extra_questions.txt" ]; then
  echo "$0: <src-dict-dir>  $src_dict_dir does not contain all required files"
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

# generating vocabluary
python3.6 $UKROASR_ROOT/tools/gen_vocab.py -t $* -v $out_dict_dir/vocab

# generating lexicon file
python3.6 $UKROASR_ROOT/tools/gen_lexicon.py -v $out_dict_dir/vocab -o $out_dict_dir/lexicon.txt -nj $nj

# extend lexicon with silence phones
echo '!SIL SIL' >> $out_dict_dir/lexicon.txt
echo '<SPOKEN_NOISE> SPN' >> $out_dict_dir/lexicon.txt
echo '<UNK> SPN' >> $out_dict_dir/lexicon.txt
echo '<NOISE> NSN' >> $out_dict_dir/lexicon.txt
