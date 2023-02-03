// flip values of RAM[0] and RAM[1]

	@R1
	D=M
	@temp
	M=D	//temp = RAM[1]

	@R0
	D=M
	@R1
	M=D 	// RAM[1] = RAM[0]

	@temp
	D=M
	@R0
	M=D	// RAM[0] = temp

(END)
	@END
	0;JMP

