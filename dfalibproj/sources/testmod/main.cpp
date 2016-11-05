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

    if (is_file_exist(regpath) == false)
    {
        DNALangParser grammarParser;
        std::map<string, string> grammar = grammarParser.parseFile(grammarpath);

        std::ofstream f(regpath);
        f << grammar.size() << std::endl;
        for (auto it = grammar.begin(); it != grammar.end(); ++ it)
            f << it->first << std::endl << it->second << std::endl;
    }

    std::ifstream file(regpath);
    int count;
    file >> count;
    std::map<std::string, string> grammar;
    string temp;
    getline(file, temp);
    for (int i = 0; i < count-1; ++i) {
        string left, expr;
        getline(file, left);
        getline(file, expr);
        grammar[left] = expr;
    }

    string result, resultexpr;
    getline(file, temp);
    getline(file, resultexpr);

    for (auto it = grammar.begin(); it != grammar.end(); ++it) {
        cout << "reading automata " << it->first << std::endl;
        string automata_path = datapath + "/temp_automata_" + it->first + ".txt";
        string minimized_automata_path = datapath + "/temp_min_automata_" + it->first + ".txt";
        if (is_file_exist(automata_path) == false)
        {
            string expr = it->second;
            std::string::iterator end_pos = std::remove(expr.begin(), expr.end(), ' ');
            expr.erase(end_pos, expr.end());
            RegEx re;
            re.Compile(expr);
            std::ofstream f(automata_path);
            re.Dump2Stream(f);
        }

        if (is_file_exist(minimized_automata_path) == false)
        {
            std::ifstream in(automata_path);
            auto automata = Automata::read_from_stream(in);
            in.close();

            cout << "before : " << automata->n_value;
            automata = find_min_automata(automata);
            cout << " after: " << automata->n_value << std::endl;

            std::ofstream out(minimized_automata_path);
            automata->dump_to_stream(out);
        }

    }


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


    std::map<std::string, std::shared_ptr<Automata>> processed_items;
    for (auto item : items) {
        string path = datapath + "/temp_min_automata_" + item + ".txt";
        ifstream f(path);
        assert(f.is_open() == true);
        processed_items[item] = Automata::read_from_stream(f);
    }
    std::shared_ptr<Automata> big = generate_big_automata(calculations_graph, processed_items);

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
\
        ofstream f(minstringpath);
        if (big->terminal_states.empty()) {
            f << "NO ANSWER";
        } else {
            for (auto state : big->terminal_states)
            {
                f << min_strings[state] << std::endl;
            }
        }
    }

    return 0;
}
