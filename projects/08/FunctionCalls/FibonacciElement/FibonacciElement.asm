// bootstrap
@256
D=A
@SP
M=D


// call Sys.init 0
@Sys.init$ret.0
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@5
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(Sys.init$ret.0)


// function Main.fibonacci 0
(Main.fibonacci)


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


// push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1


// lt                     // checks if n<2
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE0
D;JLT
D=0
@FALSE0
0;JMP
(TRUE0)
D=-1
(FALSE0)
@SP
A=M-1
M=D


// if-goto IF_TRUE
@SP
AM=M-1
D=M
@IF_TRUE
D;JNE


// goto IF_FALSE
@IF_FALSE
0;JMP


// label IF_TRUE          // if n<2, return n
(IF_TRUE)


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


// label IF_FALSE         // if n>=2, returns fib(n-2)+fib(n-1)
(IF_FALSE)


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


// push constant 2
@2
D=A
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


// call Main.fibonacci 1  // computes fib(n-2)
@Main.fibonacci$ret.1
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.1)


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


// push constant 1
@1
D=A
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


// call Main.fibonacci 1  // computes fib(n-1)
@Main.fibonacci$ret.2
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.2)


// add                    // returns fib(n-1) + fib(n-2)
@SP
AM=M-1
D=M
A=A-1
M=D+M


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


// function Sys.init 0
(Sys.init)


// push constant 4
@4
D=A
@SP
A=M
M=D
@SP
M=M+1


// call Main.fibonacci 1   // computes the 4'th fibonacci element
@Main.fibonacci$ret.0
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.0)


// label WHILE
(WHILE)


// goto WHILE              // loops infinitely
@WHILE
0;JMP


