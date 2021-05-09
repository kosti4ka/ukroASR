from pathlib import Path
from tools.utils import get_list
import argparse
from tqdm import tqdm


def gen_vocab(text_paths, vocab_path, utt_id=True, lower_case=True):
    """
    Generates vocab file out of kaldi text file
    :param text_paths: list of Kaldi like text file paths
    :param vocab_path: out vocab file
    :param utt_id: each text line contains utt id
    :param lower_case: convert to lower
    :return:
    """

    # init paths
    vocab_path = Path(vocab_path)
    vocab_path.parent.mkdir(parents=True, exist_ok=True)

    vocab = set()
    for text_path in text_paths:
        print(f'Extracting words from {text_path}')
        with open(text_path, 'r', encoding='utf-8') as text_file:
            for line in tqdm(text_file):
                # line = re.sub(r'\'{2,}', ' ', line)
                line_splited = line.split()[1:] if utt_id else line.split()
                for word in line_splited:
                    # w = process_ukr_word(w)
                    if word:
                        vocab.add(word.lower() if lower_case else word)

    # sorting
    vocab = sorted(vocab)
    print(f'Total vocabulary size: {len(vocab)}')

    with open(vocab_path, 'w', encoding='utf-8') as words_f:
        for word in vocab:
            words_f.write(f'{word}\n')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text', nargs="*", help='list of paths to the text files', required=True)
    parser.add_argument('-v', '--vocab', help='path to the vocab file', required=True)

    args = parser.parse_args()

    gen_vocab(args.text, args.vocab)
