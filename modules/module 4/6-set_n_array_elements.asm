// set first n elements of array to -1
// given
//	arr = 100 (start of array)
//	n = 10

// for (i=0; i<n; i++){
//	arr[i] = -1
// }

	// arr = 100
	@100
	D=A
	@arr
	M=D

	// n = 10
	@10
	D=A
	@n
	M=D

	// i = 0
	@i
	M=0

(LOOP)
	// if (i==n) go to END
	@i
	D=M
	@n
	D=M-D
	@END
	D;JEQ

	// RAM[arr+i] = -1
	@arr
	D=M
	@i
	A=D+M
	M=-1

	// i++
	@i
	M=M+1

	// restart LOOP
	@LOOP
	0;JMP

(END)
	@END
	0;JMP
