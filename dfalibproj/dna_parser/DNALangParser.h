#ifndef DNA_LANG_PARSER_H
#define DNA_LANG_PARSER_H

#include <string>
#include <map>

using namespace std;

class DNALangParser
{
public:
    map<string, string> parseFile(const std::string& file_path);
};

#endif
