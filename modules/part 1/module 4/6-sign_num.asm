// Computes: if R0>0
//		R1=1
//	     else
//		R1=0

	@R0
	D=M 		//D = RAM[R0]

	@POSITIVE
	D;JGT 		//jump if RAM[R0] > 0

	@R1
	M=0 		//RAM[R1] = 0
	@END
	0;JMP 		//jump to END

(POSITIVE)
	@R1
	M=1 		//RAM[R1] = 1

(END)			// infinite loop
	@END
	0;JMP

