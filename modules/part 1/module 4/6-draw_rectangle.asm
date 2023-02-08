// draw rectangle with dimensions 16 x n
// n is read from RAM[0]

	// addr = SCREEN
	// 16384
	@SCREEN
	D=A
	@addr
	M=D

	// n = RAM[0]
	@R0
	D=M
	@n
	M=D

	// i = 0
	@i
	M=0

(LOOP)
	// if i > n go to END
	@i
	D=M
	@n
	D=D-M
	@END
	D;JGT
	
	// RAM[addr] = -1 (all 1s in binary)
	@addr
	A=M
	M=-1

	// move to next row
	// addr += 32
	@32
	D=A
	@addr
	M=M+D

	// i += 1
	@i
	M=M+1

	// restart LOOP
	@LOOP
	0;JMP

(END)
	@END
	0;JMP
