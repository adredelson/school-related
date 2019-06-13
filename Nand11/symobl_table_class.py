

class SymbolTable:
    """
    a table containing all the information about variables in a jack class or method
    """

    STATIC = 0
    FIELD = 1
    ARG = 2
    VAR = 3
    KEY2ENUM = {'static': 0, 'field': 1, 'var': 3}

    def __init__(self):
        self.class_table = {}
        self.scope_table = {}
        self.field_index = 0
        self.static_index = 0
        self.arg_index = 0
        self.loc_index = 0

    def start_subroutine(self):
        """
        starts a new subroutine scope
        :return: None
        """
        self.scope_table = {}
        self.arg_index = 0
        self.loc_index = 0

    def define(self, name, var_type, kind):
        """
        defines a new identifier of the given name, type and kind, and assigns it a running index
        :param name: the variable's name
        :param var_type: the variable's type
        :param kind: either static, field, arg or var
        :return: None
        """
        if kind == SymbolTable.FIELD:
            self.class_table[name] = (var_type, 'this', self.field_index)
            self.field_index += 1
        elif kind == SymbolTable.STATIC:
            self.class_table[name] = (var_type, 'static', self.static_index)
            self.static_index += 1
        elif kind == SymbolTable.ARG:
            self.scope_table[name] = (var_type, 'argument', self.arg_index)
            self.arg_index += 1
        else:
            self.scope_table[name] = (var_type, 'local', self.loc_index)
            self.loc_index += 1

    def var_count(self, kind):
        """
        returns the number of variables of the given kind
        :param kind: either static, field, arg or var
        :return: the number of variables of the given kind
        """
        if kind == SymbolTable.FIELD:
            return self.field_index
        elif kind == SymbolTable.STATIC:
            return self.static_index
        elif kind == SymbolTable.ARG:
            return self.arg_index
        else:
            return self.loc_index

    def kind_of(self, name):
        """
        returns the kind of the current identifier in the current scope
        :param name: the identifier
        :return: the kind of the variable, None if it does'nt exist in the current scope
        """
        if name in self.scope_table:
            return self.scope_table[name][1]
        elif name in self.class_table:
            return self.class_table[name][1]
        return None

    def type_of(self, name):
        """
        returns the type of the current identifier in the current scope
        :param name: the identifier
        :return: the type of the variable, None if it does'nt exist in the current scope
        """
        if name in self.scope_table:
            return self.scope_table[name][0]
        elif name in self.class_table:
            return self.class_table[name][0]
        return None

    def index_of(self, name):
        """
        returns the index of the current identifier in the current scope
        :param name: the identifier
        :return: the index of the variable, None if it does'nt exist in the current scope
        """
        if name in self.scope_table:
            return self.scope_table[name][2]
        elif name in self.class_table:
            return self.class_table[name][2]
        return None
