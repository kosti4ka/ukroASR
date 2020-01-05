def get_list(file_path, encoding='utf-8'):
    """
    Reads list from the file
    :param file_path: path to the file
    :param encoding: encoding
    :return: list from the file
    """

    return [x.split() for x in open(file_path, 'r', encoding=encoding).read().split('\n') if x]
