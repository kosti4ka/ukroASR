from collections import defaultdict
from pathlib import Path


def get_list(file_path, encoding='utf-8'):
    """
    Reads list from the file
    :param file_path: path to the file
    :param encoding: encoding
    :return: list from the file
    """

    file_path = Path(file_path)

    return [x for x in open(file_path, 'r', encoding=encoding).read().split('\n') if x]


def get_lexicon(file_path, encoding='utf-8'):
    """
    Reads lexicon from the file
    :param file_path: path to the lexicon
    :param encoding: encoding
    :return: lexicon
    """

    lexicon = defaultdict(list)
    [lexicon[x.split()[0]].append(x.split()[1:]) for x in get_list(file_path, encoding=encoding)]

    return lexicon
