from nltk.tokenize import RegexpTokenizer

word_tokinize_regexp = r'\w+\'*-*\w+'

# TODO rewrite it as a class
def normilize_line(line):

    tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
    return tokenizer.tokenize(line)