#include <iostream>
#include <set>
#include <fstream>
#include <queue>
#include <map>
#include <cassert>
#include <list>
#include <stack>
#include <algorithm>
#include <vector>
#include <cctype>
#include <memory>
#include <string>

#include "regex/regex.h"
#include "DNALangParser.h"
#include "./dfalib/dfa.h"
#include "parserequest.h"

using std::string;
using std::map;

std::shared_ptr<Automata> generate_big_automata(std::shared_ptr<GrammarExprTree> root, std::map<std::string, std::shared_ptr<Automata>>& processed_items) {
	if (root->childs.empty()) {
		return processed_items.at(root->name);
	}
	
	std::shared_ptr<Automata> result = find_min_automata(generate_big_automata(root->childs[0], processed_items));
    for (int i = 1; i < root->childs.size(); ++i) {
		auto next = find_min_automata(generate_big_automata(root->childs[i], processed_items));
		if (root->op == '*') {
			result = find_min_automata(intesect_automata(result, next));
			continue;
		}
		if (root->op == '|') {
			result = find_min_automata(sum_automata(result, next));
			continue;
		}
	}
	return result;
}

bool is_file_exist(string fileName)
{
    std::ifstream infile(fileName);
    return infile.good();
}

int main(int argc, char* argv[])
{
    string datapath = argv[1];
    string grammarpath = datapath + "/input_grammar.txt";
    string regpath = datapath + "/parsed_grammar.txt";
    string resultgraphpath = datapath + "/result_graph.txt";
    string minstringpath = datapath + "/minimum_string.txt";


    std::map<std::string, std::shared_ptr<Automata>> processed_items;
    DNALangParser grammarParser;
    std::map<string, set<string> > grammar = grammarParser.parseFile(grammarpath);
    assert(grammar.count("result") != 0);
    for (auto it = grammar.begin(); it != grammar.end(); ++it) {
        if (it->first == "result") {
            continue;
        }
        cout << "reading rule " << it->first << std::endl;

        std::shared_ptr<Automata> result;
        int ind = 0;
        for (auto jt = it->second.begin(); jt != it->second.end(); ++jt) {
            cout << "\treading subrule " << ind++ << std::endl;

            string temppath = datapath + "/temp.txt";
            string expr = *jt;
            std::string::iterator end_pos = std::remove(expr.begin(), expr.end(), ' ');
            expr.erase(end_pos, expr.end());
            RegEx re;
            re.Compile(expr);
            std::ofstream f1(temppath);
            re.Dump2Stream(f1);

            ifstream f2(temppath);
            assert(f2.is_open() == true);


            auto temp = find_min_automata(Automata::read_from_stream(f2));
            if (jt == it->second.begin()) {
                result = temp;
            } else {
                result = find_min_automata(sum_automata(result, temp));
            }
            cout << "\tCount of states in subrule: " << result->state_count() << std::endl;
        }
        processed_items[it->first] = result;

    }


    std::string resultexpr = *grammar["result"].begin();
    std::shared_ptr<GrammarExprTree> calculations_graph = parse_request(resultexpr);


    std::set<std::string> items;
    std::queue<std::shared_ptr<GrammarExprTree>> nodes;
    nodes.push(calculations_graph);
    while (nodes.empty() == false) {
        auto next = nodes.front();
        nodes.pop();
        for (int i = 0; i < next->childs.size(); ++i) {
            nodes.push(next->childs[i]);
        }
        if (next->childs.empty()) {
            items.insert(next->name);
        }
    }


    cout << "Answer calculation..." << std::endl;
    std::shared_ptr<Automata> big = generate_big_automata(calculations_graph, processed_items);
    cout << "\tCount of states in result: " << big->state_count() << std::endl;

    ofstream fres(resultgraphpath);
    big->dump_to_stream(fres);

    {
        std::vector<string> min_strings(big->state_count());
        std::queue<int> states;
        std::set<int> viewed_states;
        states.push(0);
        viewed_states.insert(0);
        while (states.empty() == false) {
            auto from = states.front();
            states.pop();
            for (int i = 0; i < 4; ++i) {
                int to = big->get_to_state(from, i);
                if (viewed_states.count(to) > 0)
                    continue;
                min_strings[to] = min_strings[from] + char('a' + i);
                states.push(to);
                viewed_states.insert(to);
            }
        }

        ofstream f(minstringpath);
        cout << "answers:" << std::endl;
        if (big->terminal_states.empty()) {
            cout << "NO ANSWER" << std::endl;
            f << "NO ANSWER";
        } else {
            for (auto state : big->terminal_states)
            {
                cout << min_strings[state] << std::endl;
                f << min_strings[state] << std::endl;
            }
        }
    }

    return 0;
}
