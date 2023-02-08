// computes RAM[1] = 1+2+...+n
// usage: put n in RAM[0]

	@R0
	D=M
	@n
	M=D	// n = RAM[0]

	@i
	M=1	// i = 0

	@sum
	M=0	// sum = 0

(LOOP)
	// go to STOP if i > n
	@n
	D=M
	@i
	D=D-M
	@STOP
	D;JLT

	// sum += i
	@i
	D=M
	@sum
	M=D+M
	
	// i += 1
	@i
	M=M+1

	// go to LOOP
	@LOOP
	0;JMP


(STOP)
	@sum
	D=M
	@R1
	M=D	// RAM[1] = sum

(END)
	@END
	0;JMP
