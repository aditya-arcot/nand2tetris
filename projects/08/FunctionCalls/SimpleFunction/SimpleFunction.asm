// function SimpleFunction.test 2
(SimpleFunction.test)
@0
D=A
@SP
M=M+1
A=M-1
M=D
@0
D=A
@SP
M=M+1
A=M-1
M=D


// push local 0
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1


// push local 1
@LCL
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1


// add
@SP
AM=M-1
D=M
A=A-1
M=D+M


// not
@SP
A=M-1
M=!M


// push argument 0
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1


// add
@SP
AM=M-1
D=M
A=A-1
M=D+M


// push argument 1
@ARG
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1


// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D


// return
@LCL
D=M
@end_frame
M=D
@5
D=D-A
A=D
D=M
@ret_addr
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@end_frame
D=M
@1
D=D-A
@R13
M=D
A=D
D=M
@THAT
M=D
@R13
MD=M-1
A=D
D=M
@THIS
M=D
@R13
MD=M-1
A=D
D=M
@ARG
M=D
@R13
MD=M-1
A=D
D=M
@LCL
M=D
@ret_addr
A=M
0;JMP


