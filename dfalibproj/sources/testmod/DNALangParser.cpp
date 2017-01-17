#include "DNALangParser.h"
#include <fstream>
#include <list>
#include <sstream>
#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
#include <regex>
#include <set>
#include <stack>

#include "StringUtils.h"

using namespace std;

 map<string, set<string>> DNALangParser::parseFile(const std::string& file_path)
{
    ifstream infile(file_path);
	string line;
	ifstream file(file_path);
	list<string> chains;

	if (file.is_open())
	{
		string newline;
		while (getline(file, line))
		{
            if (line.size() == 0)
                continue;
			line = trim(line);
			newline.append(line);
			if (newline.back() != '\\')
			{
				chains.push_back(newline);
				newline.clear();
			}
			else
			{
				newline.pop_back();
			}
		}
		file.close();
	}
    map<string, string> expressionMap;
    map<string, set<string>> resultMap;

    map<string, map<string, int[2]>> diapasonMap;
    vector<string> orderedList;
    for (string chain: chains) {
        vector<string>splitVector = split(chain, '=', true);
        if (splitVector.size() < 2)
            continue;
        string expression = splitVector[1];
        vector<string>expressions = split(expression, ',');
        if (expressions.size() == 0)
            continue;
        expressionMap[splitVector[0]] = expressions[0];
        orderedList.push_back(splitVector[0]);
        map<string, int[2]> diapasonsForExpression;
        for (size_t i = 1; i < expressions.size(); ++i)
        {
            vector<string> diapasonVector = split(expressions[i], '=', true);
            if (diapasonVector.size() < 2)
                continue;
            vector<string> oneDiapason = split(diapasonVector[1], ':', true);
            if (oneDiapason.size() < 2)
                continue;
            oneDiapason[0].erase(0, 1);
            oneDiapason[1].erase(oneDiapason[1].length() - 1, oneDiapason[1].length());
            diapasonsForExpression[diapasonVector[0]][0] = stoi(oneDiapason[0]);
            diapasonsForExpression[diapasonVector[0]][1] = stoi(oneDiapason[1]);

        }
        diapasonMap[splitVector[0]] = diapasonsForExpression;
    }
    std::reverse(orderedList.begin(), orderedList.end());
    for (size_t i = 0; i < orderedList.size(); ++i)
        for (size_t j = i + 1; j < orderedList.size(); j++)
        {
            expressionMap[orderedList[j]] = std::regex_replace(expressionMap[orderedList[j]],  std::regex(orderedList[i]), "(" + expressionMap[orderedList[i]] + ")");
        }
    for (string expression: orderedList)
    {
         map <string, int[2]> diapasons = diapasonMap[expression];
         std::smatch m;
         std::regex e ("\\{[A-Za-z]+\\}");
         std::set<string> expressions;
         expressions.insert(expressionMap[expression]);
         bool findRegexIterator = false;
         do
         {
             std::set<string> modifiedExpressions = expressions;
             findRegexIterator = false;
             for (std::set<string>::iterator iter = expressions.begin(); iter != expressions.end(); ++iter)
             {
                 string expressionValue = *iter;
                 while (std::regex_search (expressionValue,m,e)) {
                       findRegexIterator = true;
                       string iterationValue = m.str();
                       iterationValue.erase(iterationValue.length() - 1, iterationValue.length());
                       iterationValue.erase(0, 1);
                       std::string tmpValue = expressionValue;
                       for (int i = diapasons[iterationValue][0]; i < diapasons[iterationValue][1] + 1; i++)
                       {
                           std::string modifiedValue = std::regex_replace(tmpValue, std::regex("\\{"+iterationValue+"\\}"), "{" + std::to_string(i) + "}");
                           modifiedExpressions.insert("(" + modifiedValue + ")");
                       }
                       modifiedExpressions.erase(expressionValue);
                       break;
                 }

             }
             expressions = modifiedExpressions;
         }
         while (findRegexIterator == true);
         resultMap[expression] = expressions;
    }
    for (string expression: orderedList)
    {
        std::set<string> modifiedSet;
        for (string expressionValue: resultMap[expression])
        {
            std::smatch m;
            std::regex e ("\\{[0-9]+\\}");
            while (std::regex_search (expressionValue,m,e)) {
                string iterationValue = m.str();
                iterationValue.erase(iterationValue.length() - 1, iterationValue.length());
                iterationValue.erase(0, 1);
                int count = stoi(iterationValue);
                std::stack<char> bracketStack;
                int m_lastExprPosition = m.position();
                int m_firstExprPosition = m_lastExprPosition - 1;
                do
                {
                    if (expressionValue[m_firstExprPosition] ==')')
                        bracketStack.push(')');
                    if (expressionValue[m_firstExprPosition] == '(')
                        bracketStack.pop();
                    m_firstExprPosition--;
                }
                while (!bracketStack.empty());
                string iteratedExpression = expressionValue.substr(m_firstExprPosition + 1, m_lastExprPosition - m_firstExprPosition - 1);
                string newExpression;
                for (int i = 0; i < count; i++)
                    newExpression.append(iteratedExpression);
                expressionValue.replace(m_firstExprPosition + 1, iteratedExpression.length() + m.str().length(), newExpression);
            }
            modifiedSet.insert(expressionValue);
        }
        resultMap[expression] = modifiedSet;
    }
    return resultMap;
}
