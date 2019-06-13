from tokenizer_class import JackTokenizer
from symobl_table_class import SymbolTable
from vm_writer_class import VMWriter


class CompileEngine:
    """
    Generates .xml file of a given .jack file's tokens
    """

    def __init__(self, inpt, outpt):
        """
        creates a new compilation engine with the given input and output
        :param inpt: .jack file
        :param outpt: .vm file
        """
        self.tokenizer = JackTokenizer(inpt)
        self.symbol_table = SymbolTable()
        self.code_writer = VMWriter(outpt)
        self.class_name = None
        self.label_index = 0
        self.compile_class()

    def compile_class(self):
        """
        compiles a complete class
        :return: None
        """
        self.tokenizer.advance()  # ignore 'class' keyword
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        self.tokenizer.advance()  # ignore '{' symbol
        while self.tokenizer.curtok < len(self.tokenizer.tokens) - 1:
            dec = self.tokenizer.key_word()
            if dec == "field" or dec == "static":
                self.compile_var_dec()
            else:
                self.compile_subroutine()
            self.tokenizer.advance()

    def compile_subroutine(self):
        """
        compiles a complete method, function or constructor
        :return: None
        """
        self.symbol_table.start_subroutine()
        func_type = self.tokenizer.key_word()
        self.tokenizer.advance()
        self.tokenizer.advance()  # ignore the return type of the function
        func_name = self.class_name + "." + self.tokenizer.identifier()
        self.tokenizer.advance()
        if func_type == "method":
            self.symbol_table.define("this", self.class_name, SymbolTable.ARG)
        self.compile_parameter_list()
        self.tokenizer.advance()  # ignore ')' symbol
        self.tokenizer.advance()  # ignore '{' symbol
        key = self.tokenizer.key_word()
        while key == "var":
            self.compile_var_dec()
            self.tokenizer.advance()
            key = self.tokenizer.key_word()
        n_locals = self.symbol_table.var_count(SymbolTable.VAR)
        self.code_writer.write_function(func_name, n_locals)
        if func_type == "constructor":  # allocate memory for the constructed object
            n_fields = self.symbol_table.var_count(SymbolTable.FIELD)
            self.code_writer.write_push("constant", n_fields)
            self.code_writer.write_call("Memory.alloc", 1)
            self.code_writer.write_pop("pointer", 0)
        elif func_type == "method":
            self.code_writer.write_push("argument", 0)
            self.code_writer.write_pop("pointer", 0)
        self.compile_statements()

    def compile_var_dec(self):
        """
        compiles a static declaration or a field declaration
        :param is_class: true iff it's a class var declaration
        :return: None
        """
        var_kind = SymbolTable.KEY2ENUM[self.tokenizer.key_word()]
        self.tokenizer.advance()
        tok_type = self.tokenizer.token_type()
        if tok_type == JackTokenizer.KEYWORD_T:
            var_type = self.tokenizer.key_word()
        else:
            var_type = self.tokenizer.identifier()
        while True:
            self.tokenizer.advance()
            tok_type = self.tokenizer.token_type()
            if tok_type == JackTokenizer.IDENTIFIER_T:
                var_name = self.tokenizer.identifier()
                self.symbol_table.define(var_name, var_type, var_kind)
            else:
                sym = self.tokenizer.symbol()
                if sym == ";":
                    break

    def compile_parameter_list(self):
        """
        compiles a (possibly empty) parameter list not including parentheses
        :return: None
        """
        var_type = None
        while True:
            self.tokenizer.advance()
            tok_type = self.tokenizer.token_type()
            if tok_type == JackTokenizer.KEYWORD_T:
                var_type = self.tokenizer.key_word()
            elif tok_type == JackTokenizer.IDENTIFIER_T:
                if not var_type:
                    var_type = self.tokenizer.identifier()
                else:
                    var_name = self.tokenizer.identifier()
                    self.symbol_table.define(var_name, var_type, SymbolTable.ARG)
                    var_type = None
            else:
                sym = self.tokenizer.symbol()
                if sym == ")":
                    break

    def compile_statements(self):
        """
        compiles a sequence of statements, not including the enclosing "{}"
        :return: None
        """
        tok_type = self.tokenizer.token_type()
        while tok_type == JackTokenizer.KEYWORD_T:
            key = self.tokenizer.key_word()
            if key == "let":
                self.compile_let()
            elif key == "do":
                self.compile_do()
            elif key == "while":
                self.compile_while()
            elif key == "return":
                self.compile_return()
            else:
                self.compile_if()
                tok_type = self.tokenizer.token_type()
                continue
            self.tokenizer.advance()  # ignore ';' symbol
            tok_type = self.tokenizer.token_type()

    def compile_do(self):
        """
        compile a do statement
        :return: None
        """
        self.tokenizer.advance()  # ignore 'do' keyword
        func_name = self.tokenizer.identifier()
        var_type = self.symbol_table.type_of(func_name)
        n_args = 0
        if var_type:
            self.code_writer.write_push(self.symbol_table.kind_of(func_name),
                                        self.symbol_table.index_of(func_name))
            func_name = var_type
            n_args += 1
        self.tokenizer.advance()
        sym = self.tokenizer.symbol()
        if sym == ".":
            func_name += sym
            self.tokenizer.advance()
            func_name += self.tokenizer.identifier()
            self.tokenizer.advance()
        else:
            func_name = self.class_name + "." + func_name
            n_args += 1
            self.code_writer.write_push("pointer", 0)
        self.tokenizer.advance()  # ignore '(' symbol
        n_args += self.compile_expression_list()
        self.code_writer.write_call(func_name, n_args)
        self.code_writer.write_pop("temp", 0)
        self.tokenizer.advance()  # ignore ')' symbol

    def compile_let(self):
        """
        compiles a let statement
        :return: the xml tags that correspond with let statement
        """
        self.tokenizer.advance()  # ignore 'let' keyword
        var_name = self.tokenizer.identifier()
        kind = self.symbol_table.kind_of(var_name)
        ind = self.symbol_table.index_of(var_name)
        self.tokenizer.advance()
        sym = self.tokenizer.symbol()
        is_array = False
        if sym == "[":
            is_array = True
            self.code_writer.write_push(kind, ind)
            self.tokenizer.advance()
            self.compile_expression()
            self.code_writer.write_arithmetic("add")
            self.tokenizer.advance()  # ignore ']' symbol
        self.tokenizer.advance()  # ignore '=' symbol
        self.compile_expression()
        if is_array:
            self.code_writer.write_pop("temp", 0)
            self.code_writer.write_pop("pointer", 1)
            self.code_writer.write_push("temp", 0)
            self.code_writer.write_pop("that", 0)
        else:
            self.code_writer.write_pop(kind, ind)

    def compile_while(self):
        """
        compiles a while statement
        :return: the xml tags corresponding with while statement
        """
        lab1 = self.class_name + ".L" + str(self.label_index)
        self.label_index += 1
        lab2 = self.class_name + ".L" + str(self.label_index)
        self.label_index += 1
        self.tokenizer.advance()  # ignore 'while' keyword
        self.tokenizer.advance()  # ignore '(' symbol
        self.code_writer.write_label(lab1)
        self.compile_expression()
        self.code_writer.write_arithmetic("not")
        self.code_writer.write_if(lab2)
        self.tokenizer.advance()  # ignore ')' symbol
        self.tokenizer.advance()  # ignore '{'
        self.compile_statements()
        self.code_writer.write_goto(lab1)
        self.code_writer.write_label(lab2)

    def compile_return(self):
        """
        compiles a return statement
        :return: None
        """
        self.tokenizer.advance()
        if self.tokenizer.token_type() == JackTokenizer.SYMBOL_T and self.tokenizer.symbol() == ";":
            self.code_writer.write_push("constant", 0)
        else:
            self.compile_expression()
        self.code_writer.write_return()

    def compile_if(self):
        """
        compiles an if\else statement
        :return: the xml tags corresponding with if\else statement
        """
        lab1 = self.class_name + ".L" + str(self.label_index)
        self.label_index += 1
        lab2 = self.class_name + ".L" + str(self.label_index)
        self.label_index += 1
        self.tokenizer.advance()  # ignore 'if' keyword
        self.tokenizer.advance()  # ignore '(' symbol
        self.compile_expression()
        self.code_writer.write_arithmetic("not")
        self.tokenizer.advance()  # ignore ')' symbol
        self.tokenizer.advance()  # ignore '{'
        self.code_writer.write_if(lab1)
        self.compile_statements()
        self.code_writer.write_goto(lab2)
        self.tokenizer.advance()  # ignore '}' symbol
        self.code_writer.write_label(lab1)
        if (self.tokenizer.token_type() == JackTokenizer.KEYWORD_T and
                self.tokenizer.key_word() == "else"):
            self.tokenizer.advance()
            self.tokenizer.advance()  # ignore '{' symbol
            self.compile_statements()
            self.tokenizer.advance()  # ignore '}' symbol
        self.code_writer.write_label(lab2)

    def compile_expression(self):
        """
        compiles an expression
        :return: None
        """
        self.compile_term()
        while True:
            sym = self.tokenizer.symbol()
            if sym == ")" or sym == "]" or sym == ";" or sym == "," or sym == "{":  # todo remove {
                break
            elif sym == "<":
                command = "lt"
            elif sym == ">":
                command = "gt"
            elif sym == "&":
                command = "and"
            elif sym == "=":
                command = "eq"
            elif sym == "+":
                command = "add"
            elif sym == "-":
                command = "sub"
            elif sym == "|":
                command = "or"
            elif sym == "*":
                command = "mult"
            else:
                command = "div"
            self.tokenizer.advance()
            self.compile_term()
            if command == "mult":
                self.code_writer.write_call("Math.multiply", 2)
            elif command == "div":
                self.code_writer.write_call("Math.divide", 2)
            else:
                self.code_writer.write_arithmetic(command)

    def compile_term(self):
        """
        compiles a term
        :return: None
        """
        possible_call = False
        tilda_id_or_minus_used = False
        tok_type = self.tokenizer.token_type()
        n_args = 0
        if tok_type == JackTokenizer.INT_CONST_T:
            num = self.tokenizer.int_val()
            self.code_writer.write_push("constant", int(num))
        elif tok_type == JackTokenizer.STRING_CONST_T:
            strng = self.tokenizer.string_val()
            str_len = len(strng)
            self.code_writer.write_push("constant", str_len)
            self.code_writer.write_call("String.new", 1)
            for c in strng:
                val = ord(c)
                self.code_writer.write_push("constant", val)
                self.code_writer.write_call("String.appendChar", 2)
        elif tok_type == JackTokenizer.KEYWORD_T:
            key = self.tokenizer.key_word()
            ind = 0
            if key == "this":
                self.code_writer.write_push("pointer", ind)
            else:
                self.code_writer.write_push("constant", ind)
                if key == "true":
                    self.code_writer.write_arithmetic("not")
        elif tok_type == JackTokenizer.IDENTIFIER_T:
            name = self.tokenizer.identifier()
            possible_call = True
            self.tokenizer.advance()
            sym = self.tokenizer.symbol()
            if sym == "(":
                name = self.class_name + "." + name
                self.code_writer.write_push("pointer", 0)
                self.tokenizer.advance()
                n_args += self.compile_expression_list() + 1
                self.code_writer.write_call(name, n_args)
                self.tokenizer.advance()  # ignore ')' symbol
            elif sym == ".":
                var_type = self.symbol_table.type_of(name)
                if var_type:
                    self.code_writer.write_push(self.symbol_table.kind_of(name),
                                                self.symbol_table.index_of(name))
                    name = var_type
                    n_args = 1
                name += sym
                self.tokenizer.advance()
                name += self.tokenizer.identifier()
                self.tokenizer.advance()
                self.tokenizer.advance()  # ignore '(' symbol
                n_args += self.compile_expression_list()
                self.code_writer.write_call(name, n_args)
                self.tokenizer.advance()  # ignore ')' symbol
            elif sym == "[":
                var_type = self.symbol_table.kind_of(name)
                ind = self.symbol_table.index_of(name)
                self.code_writer.write_push(var_type, ind)
                self.tokenizer.advance()
                self.compile_expression()
                self.code_writer.write_arithmetic("add")
                self.code_writer.write_pop("pointer", 1)
                self.code_writer.write_push("that", 0)
                self.tokenizer.advance()  # ignore ']' symbol
            else:
                var_type = self.symbol_table.kind_of(name)
                ind = self.symbol_table.index_of(name)
                self.code_writer.write_push(var_type, ind)
        else:
            sym = self.tokenizer.symbol()
            if sym == "~" or sym == "-":
                self.tokenizer.advance()
                self.compile_term()
                if sym == "-":
                    self.code_writer.write_arithmetic("neg")
                else:
                    self.code_writer.write_arithmetic("not")
                tilda_id_or_minus_used = True
            elif sym == "(" or sym == "[":
                self.tokenizer.advance()
                self.compile_expression()
        if not possible_call and not tilda_id_or_minus_used:
            self.tokenizer.advance()

    def compile_expression_list(self):
        """
        compiles a (possibly empty) comma - separated expression list
        :return: number of the expressions in the expression list
        """
        n_expressions = 0
        while True:
            tok_type = self.tokenizer.token_type()
            if tok_type == JackTokenizer.SYMBOL_T:
                sym = self.tokenizer.symbol()
                if sym == ")":
                    break
                elif sym == ",":
                    self.tokenizer.advance()
                else:
                    n_expressions += 1
                    self.compile_expression()
            else:
                n_expressions += 1
                self.compile_expression()
        return n_expressions
