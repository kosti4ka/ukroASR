from pathlib import Path
import os


def words(text_path, out_dir, utt_id=True):

    text_path = Path(text_path)
    out_dir = Path(out_dir)
    words_path = out_dir / 'words.txt'

    text = [x.split() for x in open(text_path, 'r').read().split('\n')[:-1]]

    words = []
    for t in text:
        if utt_id:
            words.extend(t[1:])
        else:
            words.extend(t)

    words = sorted(list(set(words)))

    # make dir
    if not out_dir.exists():
        os.makedirs(str(out_dir))

    with open(words_path, 'w', encoding='utf-8') as words_f:
        for word in words:
            words_f.write(f'{word}\n')

if __name__ == '__main__':
    words('/Users/mac/Datasets/ukrainian/prychynna/data/text',
          '/Users/mac/Datasets/ukrainian/prychynna/lang')