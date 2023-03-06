class SymbolTable:
    def __init__(self):
        self.next_field_ind = 0
        self.next_static_ind = 0
        self.next_argument_ind = 0
        self.next_local_ind = 0

        self.class_vars = {} # field, static
        self.subroutine_vars = {} # argument, local

    def print_tables(self):
        print('\n----- class vars -----')
        for i in self.class_vars.keys():
            print(i, self.class_vars[i])
        print('----- subroutine vars -----')
        for i in self.subroutine_vars.keys():
            print(i, self.subroutine_vars[i])
        print('---------------------------\n')

    def start_subroutine(self):
        self.subroutine_vars = {}
        self.next_argument_ind = 0
        self.next_local_ind = 0

    def define(self, name, type, kind):
        # type - int, char, boolean, class name
        # kind - field, static, argument, local

        if kind == 'field':
            self.class_vars[name] = [type, kind, self.next_field_ind]
            self.next_field_ind += 1
        elif kind == 'static':
            self.class_vars[name] = [type, kind, self.next_static_ind]
            self.next_static_ind += 1
        elif kind == 'argument':
            self.subroutine_vars[name] = [type, kind, self.next_argument_ind]
            self.next_argument_ind += 1
        elif kind == 'local':
            self.subroutine_vars[name] = [type, kind, self.next_local_ind]
            self.next_local_ind += 1
        else:
            print(f'unknown kind - {kind}')

    def type_of(self, name):
        return self.var_property(name, 0)

    def kind_of(self, name):
        return self.var_property(name, 1)
    
    def index_of(self, name):
        return self.var_property(name, 2)
    
    def var_property(self, name, ind):
        if name in self.subroutine_vars:
            return self.subroutine_vars[name][ind]
        if name in self.class_vars:
            return self.class_vars[name][ind]
        return -1
