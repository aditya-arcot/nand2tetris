class SymbolTable:
    '''maintains class and subroutine variable info'''

    def __init__(self):
        self.next_field_ind = 0
        self.next_static_ind = 0
        self.next_argument_ind = 0
        self.next_local_ind = 0

        self.class_vars = {} # field, static
        self.subroutine_vars = {} # argument, local

    def print_variables(self):
        '''prints class and subroutine variable info'''
        print('\n----- class vars -----')
        for var, properties in self.class_vars.items():
            print(var, properties)
        print('----- subroutine vars -----')
        for var, properties in self.subroutine_vars.items():
            print(var, properties)
        print('---------------------------\n')

    def start_subroutine(self):
        '''resets subroutine dict, indices'''
        self.subroutine_vars = {}
        self.next_argument_ind = 0
        self.next_local_ind = 0

    def define(self, name, _type, kind):
        '''adds new variable to corresponding dict'''
        # type - int, char, boolean, class name
        # kind - field, static, argument, local

        if kind == 'field':
            self.class_vars[name] = [_type, kind, self.next_field_ind]
            self.next_field_ind += 1
        elif kind == 'static':
            self.class_vars[name] = [_type, kind, self.next_static_ind]
            self.next_static_ind += 1
        elif kind == 'argument':
            self.subroutine_vars[name] = [_type, kind, self.next_argument_ind]
            self.next_argument_ind += 1
        elif kind == 'local':
            self.subroutine_vars[name] = [_type, kind, self.next_local_ind]
            self.next_local_ind += 1
        else:
            print(f'unknown kind - {kind}')

    def type_of(self, name):
        '''returns variable type'''
        return self.var_property(name, 0)

    def kind_of(self, name):
        '''returns variable kind'''
        kind = self.var_property(name, 1)
        if kind == 'field':
            return 'this'
        return kind

    def index_of(self, name):
        '''returns variable index'''
        return self.var_property(name, 2)

    def var_property(self, name, ind):
        '''returns variable property'''
        if name in self.subroutine_vars:
            return self.subroutine_vars[name][ind]
        if name in self.class_vars:
            return self.class_vars[name][ind]
        return -1
