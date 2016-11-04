#ifndef TRIM_H
#define TRIM_H

#include <algorithm> 
#include <functional> 
#include <cctype>
#include <locale>

// trim from start
static inline std::string &ltrim(std::string &s) {
	s.erase(s.begin(), std::find_if(s.begin(), s.end(),
		std::not1(std::ptr_fun<int, int>(std::isspace))));
	return s;
}

// trim from end
static inline std::string &rtrim(std::string &s) {
	s.erase(std::find_if(s.rbegin(), s.rend(),
		std::not1(std::ptr_fun<int, int>(std::isspace))).base(), s.end());
	return s;
}

// trim from both ends
static inline std::string &trim(std::string &s) {
	return ltrim(rtrim(s));
}

static inline void split(const std::string &s, char delim, std::vector<std::string> &elems, bool split_first = false) {
    std::stringstream ss;
    ss.str(s);
    std::string item;
    if (split_first == false)
    {
        while (std::getline(ss, item, delim)) {
            elems.push_back(trim(item));
        }
    }
    else
    {
        size_t pos = 0;
        std::string token;
        if ((pos = s.find(delim)) != std::string::npos) {
            token = s.substr(0, pos);
            elems.push_back(trim(token));
            std::string second = s.substr(pos + 1);
            elems.push_back(trim(second));
        }
    }
}


static inline std::vector<std::string> split(const std::string &s, char delim,  bool split_first = false) {
    std::vector<std::string> elems;
    split(s, delim, elems, split_first);
    return elems;
}


#endif
