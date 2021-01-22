/*
Iibriariy is a library with functions that I commonly use.
Created by isaac879 (02/08/2017)
*/

#ifndef Iibrary_h
#define Iibrary_h

#if ARDUINO > 22
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

struct RGB {
	unsigned char r = 0; //between 0 and 255
	unsigned char g = 0; //between 0 and 255
	unsigned char b = 0; //between 0 and 255
};

struct HSV {
	float h = 0; //angle in degrees
	float s = 1; //between 0 and 1
	float v = 1; //between 0 and 1
};

struct Coordinate {
	int x;
	int y;
	int z;
};

int getRandomNumber();
double mapNumber(double x, double in_min, double in_max, double out_min, double out_max);
int roundMapNumber(double x, double in_min, double in_max, double out_min, double out_max);
void printi(String text);
void printi(String text, char c, String endText = "\n");
void printi(short num, String endText = "\n");
void printi(unsigned short num, String endText = "\n");
void printi(int num, String endText = "\n");
void printi(unsigned int num, String endText = "\n");
void printi(long num, String endText = "\n");
void printi(unsigned long num, String endText = "\n");
void printi(float num, int dp = 3, String endText = "\n");
void printi(double num, int dp = 3, String endText = "\n");
void printi(String text, short num, String endText = "\n");
void printi(String text, unsigned short num, String endText = "\n");
void printi(String text, int num, String endText = "\n");
void printi(String text, unsigned int num, String endText = "\n");
void printi(String text, long num, String endText = "\n");
void printi(String text, unsigned long num, String endText = "\n");
void printi(String text, float num, int dp = 3, String endText = "\n");
void printi(String text, double num, int dp = 3, String endText = "\n");
double degToRads(double deg);
double radsToDeg(double rads);
void hsv2rgb(float h, float s, float v, RGB *rgb);

class Iibrary {
public:
	Iibrary();//constructor
			  //Iibrary(int i = 0);//constructor
	long serialReadInt();
private:
	int _privateVar;
};
#endif