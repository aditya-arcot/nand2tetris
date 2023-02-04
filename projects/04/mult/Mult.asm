// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.

// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

  // a = R0
  @R0
  D=M
  @a
  M=D

  // b = R1
  @R1
  D=M
  @b
  M=D

  // R2 = 0
  @R2
  M=0


(LOOP)
  // if b == 0 jump to END
  @b
  D=M
  @END
  D;JEQ

  // b -= 1
  @b
  M=M-1

  // R2 += a
  @a
  D=M
  @R2
  M=M+D

  // restart LOOP
  @LOOP
  0;JMP


(END)
  @END
  0;JMP
