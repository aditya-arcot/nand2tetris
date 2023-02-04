// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


// infinite loop
(LISTEN)
  // reset RAM[addr] to SCREEN
  @SCREEN
  D=A
  @addr
  M=D

  // reset color to -1
  @color
  M=-1

  // read RAM[KBD]
  @KBD
  D=M

  // if greater than 0, jump to BLACK
  @BLACK
  D;JGT

(WHITE)
  @color
  M=0

  @FILL
  0;JMP

(BLACK)
  // no extra code needed
  // continues to FILL

(FILL)
  // check diff between RAM[addr] and KBD
  // if 0, jump to LISTEN
  @addr
  D=M
  @KBD
  D=A-D
  @LISTEN
  D;JEQ

  // get color
  @color
  D=M

  // set row color
  @addr
  A=M
  M=D

  // addr += 1
  @addr
  M=M+1

  // restart FILL
  @FILL
  0;JMP
