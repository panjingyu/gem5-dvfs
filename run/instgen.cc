#include <iostream>
#include <fstream>
#include <cassert>
#include <string>
#include <sstream>
#include <stdlib.h>
#include <time.h>
#include <vector>
using namespace std;

vector<int> shu;

class Configoperation
{
public:
	// 1-13: input vector
	int numbase;	 //1
	int bigbase;	 //2
	float branpre; 	 //3
	int ALUwgt;		 //4
	int mulwgt;		 //5
	int divwgt;		 //6
	int faddwgt;	 //7
	int fsubwgt;	 //8
	int fmulwgt;	 //9
	int fdivwgt;	 //10
	int fmovwgt;	 //11
	int ldwgt;		 //12
	int stwgt;		 //13
	int numALU;
	int nummul;
	int numdiv;
	int numfadd;
	int numfsub;
	int numfmul;
	int numfdiv;
	int numfmov;
	int numld;
	int numst;

} config;

template <class Type>
Type stringToNum(const string &str)
{
	istringstream iss(str);
	Type num;
	iss >> num;
	return num;
}

void openfile(char const *filename)
{
	string s;

	int i = 0;
	ifstream infile(filename);
	if (!infile)
	{
		cout << "Can't open file." << endl;
		assert(infile.is_open());
	}
	while (getline(infile, s)) // get 13d vector
	{
		shu.push_back(stringToNum<int>(s));
	}

	infile.close();
}

void writefile(char const *filename)
{
	int branch;
	string s;
	int j = 0, numL = 3, numLL = 300, kong, m, n;
	int i, suminstruction, sumwgt, every;

	suminstruction = shu.size();

	branch = config.branpre * 4 + 128;
	cout << "#branch = " << branch << endl;
	srand((unsigned int)time(NULL));

	ofstream outfile(filename);
	if (!outfile)
	{
		cout << "Can't open file." << endl;
	}
	/***********************************************************/
	outfile << "	.arch armv7-a" << endl;
	outfile << "	.eabi_attribute 27, 3" << endl;
	outfile << "	.fpu vfp" << endl;
	outfile << "	.eabi_attribute 20, 1" << endl;
	outfile << "	.eabi_attribute 21, 1" << endl;
	outfile << "	.eabi_attribute 23, 3" << endl;
	outfile << "	.eabi_attribute 24, 1" << endl;
	outfile << "	.eabi_attribute 25, 1" << endl;
	outfile << "	.eabi_attribute 26, 2" << endl;
	outfile << "	.eabi_attribute 30, 6" << endl;
	outfile << "	.eabi_attribute 18, 4" << endl;
	outfile << "	.file	\"i.c\"" << endl;
	outfile << "	.text" << endl;
	outfile << "	.align	2" << endl;
	outfile << "	.global	main" << endl;
	outfile << "	.type	main, %function" << endl;
	outfile << "main : " << endl;
	outfile << "	@ args = 0, pretend = 0, frame = 16" << endl;
	outfile << "	@ frame_needed = 1, uses_anonymous_args = 0" << endl;
	outfile << "	@ link register save eliminated." << endl;
	outfile << "	str	fp, [sp, #-4]!" << endl;
	/*************************************************************************/
	outfile << "	add	fp, sp, #0" << endl;			 //  int x;
	outfile << "	sub	sp, sp, #12" << endl;			 //float y;
	outfile << "	mov	r3, #0" << endl;					 //                  x = 0;
	outfile << "	str	r3, [fp, # - 8]" << endl;	//
	outfile << "	ldr	r3, [fp, #  - 8]" << endl; //   x = x + 2;
	outfile << "start_mark:" << endl;

	for (i = 0, m = 0, j = 0, n = 0; i < suminstruction; i++, j++, m++, n++)
	{

		switch (shu[m])
		{
		case 0:
			outfile << "	ldr	r3, [fp, #-8]" << endl;
			outfile << "	add	r3, r3, #1" << endl;
			outfile << "	str	r3, [fp, #-8]" << endl;
			break;
		case 1:
			outfile << "	ldr	r3, [fp, #-8]" << endl;
			outfile << "	mov	r3, r3, asl #1" << endl;
			outfile << "	str	r3, [fp, #-8]" << endl;
			break;
		case 2:
			outfile << "	mov	r2, r3, lsr #31" << endl;
			outfile << "	add	r3, r2, r3" << endl;
			outfile << "	mov	r3, r3, asr #1" << endl;
			break;
		case 3:
			outfile << "	flds	s15, [fp, #-12]" << endl;
			outfile << "	fcvtds	d6, s15" << endl;
			outfile << "	fldd	d7, .L" << numLL << endl;
			outfile << "	faddd	d7, d6, d7" << endl;
			outfile << "	fcvtsd	s15, d7" << endl;
			outfile << "	fsts	s15, [fp, #-12]" << endl;
			break;
		case 4:
			outfile << "	flds	s15, [fp, #-12]" << endl;
			outfile << "	fcvtds	d6, s15" << endl;
			outfile << "	fldd	d7, .L" << numLL << endl;
			outfile << "	fsubd	d7, d6, d7" << endl;
			outfile << "	fcvtsd	s15, d7" << endl;
			outfile << "	fsts	s15, [fp, #-12]" << endl;
			break;
		case 5:
			outfile << "	flds	s15, [fp, #-12]" << endl;
			outfile << "	fcvtds	d6, s15" << endl;
			outfile << "	fldd	d7, .L" << numLL << endl;
			outfile << "	fmuld	d7, d6, d7" << endl;
			outfile << "	fcvtsd	s15, d7" << endl;
			outfile << "	fsts	s15, [fp, #-12]" << endl;
			break;
		case 6:
			outfile << "	flds	s15, [fp, #-12]" << endl;
			outfile << "	fcvtds	d6, s15" << endl;
			outfile << "	fldd	d7, .L" << numLL << endl;
			outfile << "	fdivd	d7, d6, d7" << endl;
			outfile << "	fcvtsd	s15, d7" << endl;
			outfile << "	fsts	s15, [fp, #-12]" << endl;
			break;
		case 7:
			outfile << "	mov	r3, #12" << endl;
			break;
		case 8:
			outfile << "	ldr	r3, [fp, #-12]	@ float   " << endl;
			break;
		case 9:
			outfile << "	str	r3, [fp, #-12]	@ float   " << endl;
			break;
		}

		if (n == 10)
		{
			outfile << "	ble	.L" << numL << endl;

			outfile << ".L" << numLL << ":" << endl;
			outfile << "	.word   -1717986918" << endl;
			outfile << "	.word	1070176665" << endl;
			outfile << "	.word	1045220557" << endl;
			numLL++;
			n = 0;
			outfile << ".L" << numL << ":" << endl;
			numL++;
		}

		/*if(j==config.bigbase)
	{
		outfile << "	bl	rand" << endl;
		outfile << "	mov	r2, r0" << endl;
		outfile << "	mov	r3, r2, asr #31" << endl;
		outfile << "	mov	r3, r3, lsr #24" << endl;
		outfile << "	add	r2, r2, r3" << endl;
		outfile << "	and	r2, r2, #255" << endl;
		outfile << "	rsb	r3, r3, r2" << endl;
		outfile << "	str	r3, [fp, # - 8]" << endl;
		outfile << "	ldr	r3, [fp, # - 8]" << endl;
		outfile << "	cmp	r3, #" << branch<<endl;
		outfile << "	ble	.L" << numL << endl;
		outfile << ".L" << numL << ":" << endl;
		numL++;
		j=0;
	}*/
	}
	outfile << "exit_mark:" << endl;
	outfile << "	mov	r3, #0" << endl;
	outfile << "	mov	r0, r3" << endl;
	outfile << "	add	sp, fp, #0" << endl;
	outfile << "	ldmfd	sp!, {fp}" << endl;
	outfile << "	bx	lr" << endl;
	outfile << ".L256:" << endl;
	outfile << "	.align	2" << endl;
	outfile << ".L" << numLL << ":" << endl;
	outfile << "	.word   -1717986918" << endl;
	outfile << "	.word	1070176665" << endl;
	outfile << "	.word	1045220557" << endl;

	outfile << "	.size	main, .-main" << endl;
	outfile << "	.ident	\"GCC: (ctng-1.8.1-FA) 4.5.1\"" << endl;
	outfile << "	.section	.note.GNU-stack,\"\",%progbits" << endl;
}

int main()
{
	openfile("./13-vec.txt");
	writefile("./testout.s");
	cout << "instgen done..." << endl;
	return 0;
}
