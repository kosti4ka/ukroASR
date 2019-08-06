from nltk.tokenize import RegexpTokenizer

word_tokinize_regexp = r'\w+\'*-*\w*'

# TODO rewrite it as a class
def normilize_line(line):

    tokenizer = RegexpTokenizer(word_tokinize_regexp)
    return ' '.join(tokenizer.tokenize(line)).lower()