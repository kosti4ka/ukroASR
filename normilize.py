from nltk.tokenize import RegexpTokenizer

word_tokinize_regexp = r'\w+\'*-*\w*'
latin2cyrillic = (u"aeikmopuc",
                  u"аеікморис")


# TODO rewrite it as a class
def normilize_line(line, convert_to_cyrillic=True):

    tokenizer = RegexpTokenizer(word_tokinize_regexp)
    line_toknized = ' '.join(tokenizer.tokenize(line)).lower()
    tr = {ord(a): ord(b) for a, b in zip(*latin2cyrillic)}
    return line_toknized.translate(tr) if convert_to_cyrillic else line_toknized
