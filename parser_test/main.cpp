#include <iostream>
#include <map>
#include "DNALangParser/DNALangParser.h"

using namespace std;

int main(int argc, char *argv[])
{
   DNALangParser parser;
   map<string, string> result = parser.parseFile("/home/lev/Документы/C++ projects/parser_test/test.txt");
   for (auto pair: result)
   {
       cout << pair.first << endl;
       cout << pair.second << endl << endl;
   }
}
