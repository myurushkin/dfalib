#ifndef DNA_LANG_PARSER_H
#define DNA_LANG_PARSER_H

#include <string>
#include <map>
#include <set>

using namespace std;

class DNALangParser
{
public:
    map<string, set<string>> parseFile(const std::string& file_path);
};

#endif
