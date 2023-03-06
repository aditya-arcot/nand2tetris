class VMWriter:
    def __init__(self, output_list:list):
        self.output_list = output_list

    def write_push(self, segment, index):
        self.output_list.append(f'push {segment} {index}')

    def write_pop(self, segment, index):
        self.output_list.append(f'pop {segment} {index}')
    
    def write_arithmetic(self, command):
        self.output_list.append(command)
    
    def write_label(self, label):
        self.output_list.append(f'label {label}')

    def write_goto(self, label):
        self.output_list.append(f'goto {label}')

    def write_if(self, label):
        self.output_list.append(f'if-goto {label}')

    def write_call(self, name, n_args):
        self.output_list.append(f'call {name} {n_args}')

    def write_function(self, name, n_local):
        self.output_list.append(f'function {name} {n_local}')
    
    def write_return(self):
        self.output_list.append('return')
        