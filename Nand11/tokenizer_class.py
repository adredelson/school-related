import re

class JackTokenizer:
    """
    Removes all comments and whitespaces from the input stream and breaks it into Jack language
    tokens, as specified by the jack grammar
    """

    COMMENT = re.compile("\\s*//.*$")
    MULTI_COMMENT_ST = re.compile("^\\s*/\*")
    MULTI_COMMENT_END = re.compile("\*/\\s*$")
    WHITESPACE = re.compile("^\\s+$")
    KEYWORD = re.compile("class|constructor|function|method|field|static|var|int|char|boolean|void"
                         "|true|false|null|this|let|do|if|else|while|return")
    SYMBOL = re.compile("[{|}()\[\].,;+\-*/&<>=~]")
    INT_CONST = re.compile("\\d+")
    STRING_CONST = re.compile("\"([^\"\n]*)\"")
    IDENTIFIER = re.compile("[a-zA-Z_]\\w*")

    KEYWORD_T = 0
    SYMBOL_T = 1
    INT_CONST_T = 2
    STRING_CONST_T = 3
    IDENTIFIER_T = 4

    def __init__(self, jack_file):
        """
        Opens the input stream and gets ready to tokenize it
        :param jack_file: the file to tokenize
        """
        self.tokens = []
        self.curtok = 0
        in_comment = False
        tok_str = ""
        string_consts = []
        with open(jack_file, 'r') as jack:
            line = jack.readline()
            while line:
                m = JackTokenizer.STRING_CONST.search(line)
                if m and not (re.search("^\\s*//", line) or
                              JackTokenizer.MULTI_COMMENT_ST.search(line)):
                    string_consts.append(m.group())
                    line = re.sub(JackTokenizer.STRING_CONST, " 65540 ", line)
                if JackTokenizer.MULTI_COMMENT_ST.match(line) and not \
                        JackTokenizer.MULTI_COMMENT_END.search(line):
                    in_comment = True
                    line = jack.readline()
                    continue
                if JackTokenizer.MULTI_COMMENT_END.search(line):
                    in_comment = False
                    line = jack.readline()
                    continue
                if JackTokenizer.COMMENT.search(line):
                    line = re.sub(JackTokenizer.COMMENT, "", line)
                if not (JackTokenizer.WHITESPACE.match(line) or in_comment):
                    tok_str += line + " "
                line = jack.readline()
        temp_tokens = tok_str.split()
        for strng in temp_tokens:
            if strng != "":
                if strng == "65540":
                    self.tokens.append(string_consts.pop(0))
                    continue
                m = JackTokenizer.SYMBOL.search(strng)
                if m:
                    while m:
                        sym = m.group()
                        if strng[0] == sym:
                            self.tokens.append(sym)
                            strng = strng[1:]
                        elif strng.index(sym) == len(strng) - 1:
                            strng = strng[:-1]
                            self.tokens.append(strng)
                            self.tokens.append(sym)
                            break
                        else:
                            ind = strng.find(sym)
                            self.tokens.append(strng[:ind])
                            self.tokens.append(sym)
                            strng = strng[ind + 1:]
                        if not JackTokenizer.SYMBOL.search(strng) and len(strng) > 0:
                            self.tokens.append(strng)
                            break
                        m = JackTokenizer.SYMBOL.search(strng)
                else:
                    self.tokens.append(strng)

    def advance(self):
        """
        make the next token the current token
        :return: None
        """
        self.curtok += 1

    def token_type(self):
        """
        :return: the type of the current token
        """
        curtok = self.tokens[self.curtok]
        m = JackTokenizer.KEYWORD.match(curtok)
        if m:
            return JackTokenizer.KEYWORD_T
        m = JackTokenizer.SYMBOL.match(curtok)
        if m:
            return JackTokenizer.SYMBOL_T
        m = JackTokenizer.IDENTIFIER.match(curtok)
        if m:
            return JackTokenizer.IDENTIFIER_T
        m = JackTokenizer.INT_CONST.match(curtok)
        if m:
            return JackTokenizer.INT_CONST_T
        else:
            return JackTokenizer.STRING_CONST_T

    def key_word(self):
        """
        :return: the keyword which is the current token
        """
        m = JackTokenizer.KEYWORD.match(self.tokens[self.curtok])
        return m.group()

    def symbol(self):
        """
        :return: the symbol that is the current token
        """
        m = JackTokenizer.SYMBOL.match(self.tokens[self.curtok])
        return m.group()

    def identifier(self):
        """
        :return: the identifier that is the current token
        """
        m = JackTokenizer.IDENTIFIER.match(self.tokens[self.curtok])
        return m.group()

    def int_val(self):
        """
        :return: the integer value that is the current token
        """
        m = JackTokenizer.INT_CONST.match(self.tokens[self.curtok])
        return int(m.group())

    def string_val(self):
        """
        :return: the string that is the current token
        """
        m = JackTokenizer.STRING_CONST.match(self.tokens[self.curtok])
        return m.group(1)
