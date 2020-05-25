#!/usr/bin/env bash

cd $KALDI_ROOT/egs/wsj/s5; . ./path.sh; . ./cmd.sh

python3.6 $work_dir/tools/gen_vocab.py -t $data/train/text -v $data/local/dict/vocab

# generating lexicon file
python3.6 $work_dir/tools/gen_lexicon.py -v $data/local/dict/vocab -o $data/local/dict/lexicon.txt

# silence_phones.txt
echo 'SIL' > $data/local/dict/silence_phones.txt
echo 'SPN' >> $data/local/dict/silence_phones.txt
echo 'NSN' >> $data/local/dict/silence_phones.txt

# optional_silence.txt
echo 'SIL' > $data/local/dict/optional_silence.txt

# extend lexicon with silence phones
echo '!SIL SIL' >> $data/local/dict/lexicon.txt
echo '<SPOKEN_NOISE> SPN' >> $data/local/dict/lexicon.txt
echo '<UNK> SPN' >> $data/local/dict/lexicon.txt
echo '<NOISE> NSN' >> $data/local/dict/lexicon.txt