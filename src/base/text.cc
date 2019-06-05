/*
 * Copyright (c) 2004-2005 The Regents of The University of Michigan
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Nathan Binkert
 */

#if defined(__APPLE__)
#define _GLIBCPP_USE_C99 1
#endif

#if defined(__sun)
#include <math.h>
#endif

#include <cassert>
#ifdef __SUNPRO_CC
#include <math.h>
#endif
#include <cmath>

#include "base/stats/info.hh"
#include "base/stats/text.hh"
#include "base/cast.hh"
#include "base/misc.hh"
#include "base/str.hh"
#include <complex>
#include <string>
#include <stdlib.h>
#include <fstream>
#include <vector>
#include <cmath>

using namespace std;

bool Incounter = 0;
bool Outstats = 0;
int Countcnt = 0;
int jj = 0;
int count = 0;
vector<string> Countname(64); // all the input counter name

// value(s) corresponding with the specific counter name
// some counter has 3 values, so the counter name can be 
// represented by name_0, name_1, name_2
map<string, double> CounterValue;
map<string, double>::iterator iter;
map<string, bool> mapflag; // if or not insert the CounterValue map

vector<double> Param;

vector<string> line; // every line in the counter_atomic.txt
vector<string> formula; 
vector<double> results; // the results for the formula

complex <double>   r[20];
complex <double>  p[20];
complex <double>  xx0[20];
complex <double>  xx1[20];
long frequency;
double timeinterval;
// cycle
long numCycle;
// present tick
long nowTick;
long ticks;

/**
 * input the counter name required for power estimation
 * store the counter name in the vector Countname
 */

class Configoperation
{
public:
	void openfile(char const* filename);
	string powerin;
	string powerout;
	float powerfreq;
	float powervol;
	string noisein;
	string noiseout;
	float noisetime;
}config;

template <class Type>
Type stringToNum(const string& str) {
	istringstream iss(str);
	Type num;
	iss >> num;
	return num;
}


void Configoperation::openfile(char const* filename)
{
	int i = 0;
	string ss, name, val;
	ifstream infile(filename);
	if (!infile) {
		cout << "Can't open Configoperation file." << endl;
	}
		while (getline(infile, ss))
		{
			istringstream word(ss);
			word >> name;
			word >> val;
			if (i>0)
			{
				if (i == 1) config.powerin = val;
				if (i == 2) config.powerout = val;
				if (i == 3) config.powerfreq = stringToNum<float>(val);
				if (i == 4) config.powervol = stringToNum<float>(val);
				if (i == 5) config.noisein = val;
				if (i == 6) config.noiseout = val;
				if (i == 7) config.noisetime = stringToNum<float>(val);
				i++;
			}
			if (name == "#") i = 1;
		}
		

	
}
void PRIn()
{
	int i = 0, ii = 0;

	double ss[50];
	
	ifstream fin(config.noisein,ios::in);
	if (!fin) {
		cerr << "Can't open PRIn file." << endl;
		getchar();
	}
	
	while (!fin.eof())
	{
			fin >> ss[i];
			i++;
	}
 
	jj =i / 4;
	for (i =0; i<jj; i++)
	{

		ii = 2 * i;
		p[i] = complex <double>(ss[ii], ss[ii + 1]);

	}
	for (i =0; i<jj; i++)
	{

		ii = 2 * i+2*jj;
		r[i] = complex <double>(ss[ii], ss[ii + 1]);

	}
	
	fin.close();
	
	
}
void CountIn()
{
    ifstream fin("/home/pan/DVFS/gem5-dvfs/parameter/counter_input_o3.txt");

    if (!fin) {
        cerr << "Can't open CountIn file." << endl;
        getchar();
    }

    while (!fin.eof()) {
        fin >> Countname[Countcnt];
        Countcnt++;
    }
    
    fin.close();
}

/**
 * input the parameters required for power estimation
 * store the parameters in the vector param
 */
void ParamIn()
{
    ifstream fin(config.powerin);

    if (!fin) {
        cerr << "Can't open ParamIn the file." << endl;
        getchar();
    }

    while (!fin.eof()) {
        string str;
        fin >> str;
        double param;
        stringstream sstr;
        sstr.str(str);
        sstr >> param;
        Param.push_back(param);
    }
}

/**
 * input the formulas required for power estimatipn
 * store every line in the vector line
 */
void FormulaIn()
{
    ifstream fin("/home/pan/DVFS/gem5-dvfs/parameter/label_o3.txt");
    string s;
    while (!fin.eof()) {
        getline(fin, s);
        if (s != "\0") {
            line.push_back(s);
        }
    }

    fin.close();
}


void xxprosess(double u, int m)
{
	int i;
	complex <double> j,jjj;
	complex <double> t, s;
	t = complex <double>(u, 0);
	s = complex <double>(timeinterval, 0);
	if (m == 1)
	{
		for (i = 0; i<jj; i++)
			xx0[i] =-t / (p[i]);
	}
	else
	{
		for (i = 0; i<jj; i++)
			xx0[i] = xx1[i];
	}

	for (i = 0; i<jj; i++)
	{
		jjj = p[i] * s;
	//	cout << "jjj=" << jjj << endl;
		j = exp(jjj);
		xx1[i] = xx0[i] * j + (j - complex <double>(1, 0)) / p[i] * t;
		
     
	}
//	cout << "xx1=" << xx1[0] << endl;

}


double NoiseEstimation(double u, int m)
{
	complex <double>  w = 0;
	xxprosess(u, m);
	int a;
	for (a = 0; a<jj; a++)
		w += r[a] * xx1[a];
   return w.real();
}

/**
 * some sub function for the formula calculation
 */
double math(double op1, string opc, double op2)
{
    if (opc == "+")          return op1+op2;
    else if (opc == "-")     return op1-op2;
    else if (opc == "*")     return op1*op2;
    else {
        if ((op1==0) | (op2==0)) return 0;
        else                 return op1/op2;
    }
}

double processFormula(vector<string> ff)
{
    int len = ff.size();
    string index = "";
    bool mul = 0;

    double res;

    if ((ff[len-1] == "1") | (ff[len-1] == "2") | (ff[len-1] == "3"))
    {
        index = ff[len-1];
        mul = 1;
        ff.pop_back();
        len = ff.size();
    }

    if (len == 1) {
        if (mul) {
            string key = formula[0] + index;
            res = CounterValue[key];
        }
        else {
            string key = formula[0];
            res = CounterValue[key];
        }
    }

    else { // len is 3, 5...
        vector<double> opx; //operand
        vector<string> opc; //opcode
        opx.clear();
        opc.clear();
        int times = len/2;
        double temp = 0;

        for (int i = 0; i <= times; i++) 
        {
            string key1 = formula[2*i];
            key1 = mul ? (key1 + index) : key1;
            double value = CounterValue[key1];
            opx.push_back(value);
        }
        for (int i = 0; i < times; i++)
        {
            string key2 = formula[2*i+1];
            opc.push_back(key2);
        }

        // calculate the formula
        for (int i = 0; i < times; i++) 
        {
            double op1 = (i==0) ? opx[0] : temp;
            temp = math(op1, opc[i], opx[i+1]);
        }

        res = temp;
    }

    return res;

}

double PowerEstimation()
{
    double Energy = 0;

    for (int i = 0; i < line.size(); i++)
    {
        string str = line[i] + " ";
        int size = str.size();
        formula.clear();

        for (int j = 0; j < size; j++)
        {
            string::size_type pos = str.find(' ', j);
            if (pos < size) 
            {
                string s = str.substr(j, pos-j);
                formula.push_back(s);
                j = pos;
            }
        }

        double Formulavalue = processFormula(formula);
        Energy += Formulavalue * Param[i];
    }

    double power = Energy / numCycle;
    power += Param[Param.size()-1];

    return power;

}
/**********************************************************************************/

#ifndef NAN
float __nan();
/** Define Not a number. */
#define NAN (__nan())
/** Need to define __nan() */
#define __M5_NAN
#endif

#ifdef __M5_NAN
float
__nan()
{
    union {
        uint32_t ui;
        float f;
    } nan;

    nan.ui = 0x7fc00000;
    return nan.f;
}
#endif

namespace Stats {

std::list<Info *> &statsList();

Text::Text()
    : mystream(false), stream(NULL), descriptions(false)
{
}

Text::Text(std::ostream &stream)
    : mystream(false), stream(NULL), descriptions(false)
{
    open(stream);
}

Text::Text(const std::string &file)
    : mystream(false), stream(NULL), descriptions(false)
{
    open(file);
}


Text::~Text()
{
    if (mystream) {
        assert(stream);
        delete stream;
    }
}

void
Text::open(std::ostream &_stream)
{
    if (stream)
        panic("stream already set!");

    mystream = false;
    stream = &_stream;
    if (!valid())
        fatal("Unable to open output stream for writing\n");
}

void
Text::open(const std::string &file)
{
    if (stream)
        panic("stream already set!");

    mystream = true;
    stream = new ofstream(file.c_str(), ios::trunc);
    if (!valid())
        fatal("Unable to open statistics file for writing\n");
}

bool
Text::valid() const
{
    return stream != NULL && stream->good();
}

void
Text::begin()
{
    if (Incounter == 0) {
        config.openfile("/home/pan/DVFS/gem5-dvfs/parameter/parameter.config");
	CountIn();  // input the counter
        ParamIn();  // input the parameters
        FormulaIn(); // input the formula
	PRIn();
        Incounter = 1;
    }
    CounterValue.clear();
    mapflag.clear();
    ccprintf(*stream, "\n---------- Begin Simulation Statistics ----------\n");
}

void
Text::end()
{
    int i,j;
    if (Outstats == 0) {
        ofstream f(config.powerout, ios::trunc);
        f.close();
        ofstream ff(config.noiseout, ios::trunc);
         ff.close();
    	ofstream fff("/home/pan/DVFS/gem5-dvfs/m5out/powerlist.txt", ios::trunc);
         fff.close();
        Outstats = 1;
    }

    ofstream fout(config.powerout, ios::app);
    
    // dump the stats corresponding with required counters
    fout << "************ dump required stats ************" << endl;
    for (iter = CounterValue.begin(); iter != CounterValue.end(); ++iter) {
        fout << iter->first << "    " << iter->second << endl;
    }
    
    double power = PowerEstimation();
    fout << "--------------- power = " << power << " ---------------" << endl;
    fout << "--------------- cycle = " << numCycle << " ---------------" << endl;
    fout << "--------------- tick = " << nowTick << " -----------------" << endl;
    fout << endl;
    fout.close();
    ofstream ffout(config.noiseout, ios::app);
    timeinterval=config.noisetime;
	
    j=((double)ticks)/1000000000000/config.noisetime;
    double noise,u;
     u=power/config.powervol;
     ffout << "--------------- power = " << power << " ---------------" << endl;
     ffout << "--------------- ticks = " << ticks << " -----------------" << endl;
    
    for(i=0;i<j;i++)
    {
      count=count+1;
      noise=NoiseEstimation(u,count);
      ffout << "--------------- noise = " << noise << " -----------------" << endl;
    }
    ffout << "--------------- tick = " << nowTick << " -----------------" << endl;
    ffout << endl; 
    ffout.close();
    ofstream fffout("/home/pan/DVFS/gem5-dvfs/m5out/powerlist.txt", ios::app);
    fffout << power<< endl;
    fffout.close();
    ccprintf(*stream, "\n---------- End Simulation Statistics   ----------\n");
    stream->flush();
}

bool
Text::noOutput(const Info &info)
{
    if (!info.flags.isSet(display))
        return true;

    if (info.prereq && info.prereq->zero())
        return true;

    return false;
}

string
ValueToString(Result value, int precision)
{
    stringstream val;

    if (!std::isnan(value)) {
        if (precision != -1)
            val.precision(precision);
        else if (value == rint(value))
            val.precision(0);

        val.unsetf(ios::showpoint);
        val.setf(ios::fixed);
        val << value;
    } else {
        val << "nan";
    }

    return val.str();
}

struct ScalarPrint
{
    Result value;
    string name;
    string desc;
    Flags flags;
    bool descriptions;
    int precision;
    Result pdf;
    Result cdf;

    void update(Result val, Result total);
    void operator()(ostream &stream, bool oneLine = false) const;
};

void
ScalarPrint::update(Result val, Result total)
{
    value = val;
    if (total) {
        for (int i = 0; i < Countname.size(); i++) {
            if (name == Countname[i]) {
                /*cout << "value = " << value << endl;
                cout << "name = " << name << endl;
                cout << "pdf = " << (val/total) << endl;
                cout << "cdf = " << cdf << endl;
                cout << "\n" << endl;*/
                CounterValue.insert(pair<string, double>((name+"1"), value));
                CounterValue.insert(pair<string, double>((name+"2"), (val/total)));
                CounterValue.insert(pair<string, double>((name+"3"), (val/total + cdf)));
                mapflag.insert(pair<string, bool>(name, 1)); 
                
            }
        }
        pdf = val / total;
        cdf += pdf;
    }
}

void
ScalarPrint::operator()(ostream &stream, bool oneLine) const
{
    if ((flags.isSet(nozero) && (!oneLine) && value == 0.0) ||
        (flags.isSet(nonan) && std::isnan(value)))
        return;

    stringstream pdfstr, cdfstr;

    if (!std::isnan(pdf))
        ccprintf(pdfstr, "%.2f%%", pdf * 100.0);

    if (!std::isnan(cdf))
        ccprintf(cdfstr, "%.2f%%", cdf * 100.0);

    if (oneLine) {
        ccprintf(stream, " |%12s %10s %10s",
                 ValueToString(value, precision), pdfstr.str(), cdfstr.str());
    } else {
        ccprintf(stream, "%-40s %12s %10s %10s", name,
                 ValueToString(value, precision), pdfstr.str(), cdfstr.str());

        for (int i = 0; i < Countname.size(); i++) {
            if ((name == Countname[i]) && (mapflag[name] == 0)) {
                /*cout << "name = " << name << endl;
                cout << "value = " << value << endl;
                cout << "\n" << endl;*/
                CounterValue.insert(pair<string, double>(name, value));
                mapflag.insert(pair<string, bool>(name, 1));
            }
        }
        
        // number of cycles every phase
        if (name == "system.cpu.numCycles") {
            numCycle = value;
        }

        // present tick when dump
        if (name == "final_tick") {
            nowTick = value;
        }
        if (name == "sim_ticks") {
            ticks = value;
        }
        if (name == "sim_freq") {
            frequency = value;
        }
        if (descriptions) {
            if (!desc.empty())
                ccprintf(stream, " # %s", desc);
        }
        stream << endl;
    }
}

struct VectorPrint
{
    string name;
    string separatorString;
    string desc;
    vector<string> subnames;
    vector<string> subdescs;
    Flags flags;
    bool descriptions;
    int precision;
    VResult vec;
    Result total;
    bool forceSubnames;

    void operator()(ostream &stream) const;
};

void
VectorPrint::operator()(std::ostream &stream) const
{
    size_type _size = vec.size();
    Result _total = 0.0;

    if (flags.isSet(pdf | cdf)) {
        for (off_type i = 0; i < _size; ++i) {
            _total += vec[i];
        }
    }

    string base = name + separatorString;

    ScalarPrint print;
    print.name = name;
    print.desc = desc;
    print.precision = precision;
    print.descriptions = descriptions;
    print.flags = flags;
    print.pdf = _total ? 0.0 : NAN;
    print.cdf = _total ? 0.0 : NAN;

    bool havesub = !subnames.empty();

    if (_size == 1) {
        // If forceSubnames is set, get the first subname (or index in
        // the case where there are no subnames) and append it to the
        // base name.
        if (forceSubnames)
            print.name = base + (havesub ? subnames[0] : std::to_string(0));
        print.value = vec[0];
        print(stream);
        return;
    }

    if ((!flags.isSet(nozero)) || (total != 0)) {
        if (flags.isSet(oneline)) {
            ccprintf(stream, "%-40s", name);
            print.flags = print.flags & (~nozero);
        }

        for (off_type i = 0; i < _size; ++i) {
            if (havesub && (i >= subnames.size() || subnames[i].empty()))
                continue;

            print.name = base + (havesub ? subnames[i] : std::to_string(i));
            print.desc = subdescs.empty() ? desc : subdescs[i];

            print.update(vec[i], _total);
            print(stream, flags.isSet(oneline));
        }

        if (flags.isSet(oneline)) {
            if (descriptions) {
                if (!desc.empty())
                    ccprintf(stream, " # %s", desc);
            }
            stream << endl;
        }
    }

    if (flags.isSet(::Stats::total)) {
        print.pdf = NAN;
        print.cdf = NAN;
        print.name = base + "total";
        print.desc = desc;
        print.value = total;
        print(stream);
    }
}

struct DistPrint
{
    string name;
    string separatorString;
    string desc;
    Flags flags;
    bool descriptions;
    int precision;

    const DistData &data;

    DistPrint(const Text *text, const DistInfo &info);
    DistPrint(const Text *text, const VectorDistInfo &info, int i);
    void init(const Text *text, const Info &info);
    void operator()(ostream &stream) const;
};

DistPrint::DistPrint(const Text *text, const DistInfo &info)
    : data(info.data)
{
    init(text, info);
}

DistPrint::DistPrint(const Text *text, const VectorDistInfo &info, int i)
    : data(info.data[i])
{
    init(text, info);

    name = info.name + "_" +
        (info.subnames[i].empty() ? (std::to_string(i)) : info.subnames[i]);

    if (!info.subdescs[i].empty())
        desc = info.subdescs[i];
}

void
DistPrint::init(const Text *text, const Info &info)
{
    name = info.name;
    separatorString = info.separatorString;
    desc = info.desc;
    flags = info.flags;
    precision = info.precision;
    descriptions = text->descriptions;
}

void
DistPrint::operator()(ostream &stream) const
{
    if (flags.isSet(nozero) && data.samples == 0) return;
    string base = name + separatorString;

    ScalarPrint print;
    print.precision = precision;
    print.flags = flags;
    print.descriptions = descriptions;
    print.desc = desc;
    print.pdf = NAN;
    print.cdf = NAN;

    if (flags.isSet(oneline)) {
        print.name = base + "bucket_size";
        print.value = data.bucket_size;
        print(stream);

        print.name = base + "min_bucket";
        print.value = data.min;
        print(stream);

        print.name = base + "max_bucket";
        print.value = data.max;
        print(stream);
    }

    print.name = base + "samples";
    print.value = data.samples;
    print(stream);

    print.name = base + "mean";
    print.value = data.samples ? data.sum / data.samples : NAN;
    print(stream);

    if (data.type == Hist) {
        print.name = base + "gmean";
        print.value = data.samples ? exp(data.logs / data.samples) : NAN;
        print(stream);
    }

    Result stdev = NAN;
    if (data.samples)
        stdev = sqrt((data.samples * data.squares - data.sum * data.sum) /
                     (data.samples * (data.samples - 1.0)));
    print.name = base + "stdev";
    print.value = stdev;
    print(stream);

    if (data.type == Deviation)
        return;

    size_t size = data.cvec.size();

    Result total = 0.0;
    if (data.type == Dist && data.underflow != NAN)
        total += data.underflow;
    for (off_type i = 0; i < size; ++i)
        total += data.cvec[i];
    if (data.type == Dist && data.overflow != NAN)
        total += data.overflow;

    if (total) {
        print.pdf = 0.0;
        print.cdf = 0.0;
    }

    if (data.type == Dist && data.underflow != NAN) {
        print.name = base + "underflows";
        print.update(data.underflow, total);
        print(stream);
    }

    if (flags.isSet(oneline)) {
        ccprintf(stream, "%-40s", name);
    }

    for (off_type i = 0; i < size; ++i) {
        stringstream namestr;
        namestr << base;

        Counter low = i * data.bucket_size + data.min;
        Counter high = ::min(low + data.bucket_size - 1.0, data.max);
        namestr << low;
        if (low < high)
            namestr << "-" << high;

        print.name = namestr.str();
        print.update(data.cvec[i], total);
        print(stream, flags.isSet(oneline));
    }

    if (flags.isSet(oneline)) {
        if (descriptions) {
            if (!desc.empty())
                ccprintf(stream, " # %s", desc);
        }
        stream << endl;
    }

    if (data.type == Dist && data.overflow != NAN) {
        print.name = base + "overflows";
        print.update(data.overflow, total);
        print(stream);
    }

    print.pdf = NAN;
    print.cdf = NAN;

    if (data.type == Dist && data.min_val != NAN) {
        print.name = base + "min_value";
        print.value = data.min_val;
        print(stream);
    }

    if (data.type == Dist && data.max_val != NAN) {
        print.name = base + "max_value";
        print.value = data.max_val;
        print(stream);
    }

    print.name = base + "total";
    print.value = total;
    print(stream);
}

void
Text::visit(const ScalarInfo &info)
{
    if (noOutput(info))
        return;

    ScalarPrint print;
    print.value = info.result();
    print.name = info.name;
    print.desc = info.desc;
    print.flags = info.flags;
    print.descriptions = descriptions;
    print.precision = info.precision;
    print.pdf = NAN;
    print.cdf = NAN;

    print(*stream);
}

void
Text::visit(const VectorInfo &info)
{
    if (noOutput(info))
        return;

    size_type size = info.size();
    VectorPrint print;

    print.name = info.name;
    print.separatorString = info.separatorString;
    print.desc = info.desc;
    print.flags = info.flags;
    print.descriptions = descriptions;
    print.precision = info.precision;
    print.vec = info.result();
    print.total = info.total();
    print.forceSubnames = false;

    if (!info.subnames.empty()) {
        for (off_type i = 0; i < size; ++i) {
            if (!info.subnames[i].empty()) {
                print.subnames = info.subnames;
                print.subnames.resize(size);
                for (off_type i = 0; i < size; ++i) {
                    if (!info.subnames[i].empty() &&
                        !info.subdescs[i].empty()) {
                        print.subdescs = info.subdescs;
                        print.subdescs.resize(size);
                        break;
                    }
                }
                break;
            }
        }
    }

    print(*stream);
}

void
Text::visit(const Vector2dInfo &info)
{
    if (noOutput(info))
        return;

    bool havesub = false;
    VectorPrint print;

    if (!info.y_subnames.empty()) {
        for (off_type i = 0; i < info.y; ++i) {
            if (!info.y_subnames[i].empty()) {
                print.subnames = info.y_subnames;
                break;
            }
        }
    }
    print.flags = info.flags;
    print.separatorString = info.separatorString;
    print.descriptions = descriptions;
    print.precision = info.precision;
    print.forceSubnames = true;

    if (!info.subnames.empty()) {
        for (off_type i = 0; i < info.x; ++i)
            if (!info.subnames[i].empty())
                havesub = true;
    }

    VResult tot_vec(info.y);
    VResult super_total(1, 0.0);
    for (off_type i = 0; i < info.x; ++i) {
        if (havesub && (i >= info.subnames.size() || info.subnames[i].empty()))
            continue;

        off_type iy = i * info.y;
        VResult yvec(info.y);

        Result total = 0.0;
        for (off_type j = 0; j < info.y; ++j) {
            yvec[j] = info.cvec[iy + j];
            tot_vec[j] += yvec[j];
            total += yvec[j];
            super_total[0] += yvec[j];
        }

        print.name = info.name + "_" +
            (havesub ? info.subnames[i] : std::to_string(i));
        print.desc = info.desc;
        print.vec = yvec;
        print.total = total;
        print(*stream);
    }

    // Create a subname for printing the total
    vector<string> total_subname;
    total_subname.push_back("total");

    if (info.flags.isSet(::Stats::total) && (info.x > 1)) {
        print.name = info.name;
        print.subnames = total_subname;
        print.desc = info.desc;
        print.vec = super_total;
        print.flags = print.flags & ~total;
        print(*stream);
    }
}

void
Text::visit(const DistInfo &info)
{
    if (noOutput(info))
        return;

    DistPrint print(this, info);
    print(*stream);
}

void
Text::visit(const VectorDistInfo &info)
{
    if (noOutput(info))
        return;

    for (off_type i = 0; i < info.size(); ++i) {
        DistPrint print(this, info, i);
        print(*stream);
    }
}

void
Text::visit(const FormulaInfo &info)
{
    visit((const VectorInfo &)info);
}

/*
  This struct implements the output methods for the sparse
  histogram stat
*/
struct SparseHistPrint
{
    string name;
    string separatorString;
    string desc;
    Flags flags;
    bool descriptions;
    int precision;

    const SparseHistData &data;

    SparseHistPrint(const Text *text, const SparseHistInfo &info);
    void init(const Text *text, const Info &info);
    void operator()(ostream &stream) const;
};

/* Call initialization function */
SparseHistPrint::SparseHistPrint(const Text *text, const SparseHistInfo &info)
    : data(info.data)
{
    init(text, info);
}

/* Initialization function */
void
SparseHistPrint::init(const Text *text, const Info &info)
{
    name = info.name;
    separatorString = info.separatorString;
    desc = info.desc;
    flags = info.flags;
    precision = info.precision;
    descriptions = text->descriptions;
}

/* Grab data from map and write to output stream */
void
SparseHistPrint::operator()(ostream &stream) const
{
    string base = name + separatorString;

    ScalarPrint print;
    print.precision = precision;
    print.flags = flags;
    print.descriptions = descriptions;
    print.desc = desc;
    print.pdf = NAN;
    print.cdf = NAN;

    print.name = base + "samples";
    print.value = data.samples;
    print(stream);

    MCounter::const_iterator it;
    for (it = data.cmap.begin(); it != data.cmap.end(); it++) {
        stringstream namestr;
        namestr << base;

        namestr <<(*it).first;
        print.name = namestr.str();
        print.value = (*it).second;
        print(stream);
    }
}

void
Text::visit(const SparseHistInfo &info)
{
    if (noOutput(info))
        return;

    SparseHistPrint print(this, info);
    print(*stream);
}

Output *
initText(const string &filename, bool desc)
{
    static Text text;
    static bool connected = false;

    if (!connected) {
        ostream *os = simout.find(filename);
        if (!os)
            os = simout.create(filename);

        text.open(*os);
        text.descriptions = desc;
        connected = true;
    }

    return &text;
}

} // namespace Stats
