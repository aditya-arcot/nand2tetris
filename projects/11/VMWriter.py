class VMWriter:
    '''appends VM code for various commands to supplied list'''

    def __init__(self, output_list:list):
        self.output_list = output_list

    def write_push(self, segment, index):
        '''adds VM code for push command'''
        self.output_list.append(f'push {segment} {index}')

    def write_pop(self, segment, index):
        '''adds VM code for pop command'''
        self.output_list.append(f'pop {segment} {index}')

    def write_arithmetic(self, command):
        '''adds VM code for arithmetic command'''
        self.output_list.append(command)

    def write_label(self, label):
        '''adds VM code for labal declaration'''
        self.output_list.append(f'label {label}')

    def write_goto(self, label):
        '''adds VM code for goto command'''
        self.output_list.append(f'goto {label}')

    def write_if(self, label):
        '''adds VM code for if-goto command'''
        self.output_list.append(f'if-goto {label}')

    def write_call(self, name, n_args):
        '''adds VM code for call command'''
        self.output_list.append(f'call {name} {n_args}')

    def write_function(self, name, n_local):
        '''adds VM code for function declaration'''
        self.output_list.append(f'function {name} {n_local}')

    def write_return(self):
        '''adds VM code for return command'''
        self.output_list.append('return')
        