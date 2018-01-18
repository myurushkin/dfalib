//#include <iostream>
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

#include "json.hpp"

#include "regex/regex.h"
#include "DNALangParser.h"
#include "./dfalib/dfa.h"
#include "parserequest.h"

using std::string;
using std::map;
using json = nlohmann::json;

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

void find_all_min_strings(std::shared_ptr<Automata>& big, std::vector<int>& min_paths, int currentNode, list<string>& result);
void find_all_min_strings(std::shared_ptr<Automata>& big, std::list<string>& min_strings);


int main(int argc, char* argv[])
{
    if (argc != 2) {
        return 1;
    }

    std::ifstream inf(argv[1]);
    std::string config((std::istreambuf_iterator<char>(inf)),
        std::istreambuf_iterator<char>());
    json obj = json::parse(config);

    string grammarpath = obj["grammar-filepath"].get<std::string>();

    string tmpdir = obj["tmp-dirpath"].get<std::string>();
    string regpath = tmpdir + "/parsed_grammar.txt";
    string resultgraphpath = tmpdir + "/result_graph.txt";
    string minstringpath = obj["output-filepath"].get<std::string>();

    std::map<std::string, std::shared_ptr<Automata>> processed_items;
    DNALangParser grammarParser;
    std::map<string, set<string> > grammar = grammarParser.parseFile(grammarpath);
    assert(grammar.count("result") != 0);
    for (auto it = grammar.begin(); it != grammar.end(); ++it) {
        if (it->first == "result") {
            continue;
        }
        //cout << "reading rule " << it->first << std::endl;

        std::shared_ptr<Automata> result;
        int ind = 0;
        for (auto jt = it->second.begin(); jt != it->second.end(); ++jt) {
            //cout << "\treading subrule " << ind++ << std::endl;

            string temppath = tmpdir + "/temp.txt";
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

			// generate_automata_visualization_script(temp, "E:/projects/projects-git/dfalib/img/fsm-my.gv");

            if (jt == it->second.begin()) {
                result = temp;
            } else {
                result = find_min_automata(sum_automata(result, temp));
            }
            //cout << "\tCount of states in subrule: " << result->state_count() << std::endl;
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


    //cout << "Answer calculation..." << std::endl;
    std::shared_ptr<Automata> big = generate_big_automata(calculations_graph, processed_items);
    //cout << "\tCount of states in result: " << big->state_count() << std::endl;

    ofstream fres(resultgraphpath);
    big->dump_to_stream(fres);

    {
        //std::vector<string> min_strings(big->state_count());
        //std::queue<int> states;
        //std::set<int> viewed_states;
        //states.push(0);
        //viewed_states.insert(0);
        //while (states.empty() == false) {
        //    auto from = states.front();
        //    states.pop();
        //    for (int i = 0; i < 4; ++i) {
        //        int to = big->get_to_state(from, i);
        //        if (viewed_states.count(to) > 0)
        //            continue;
        //        min_strings[to] = min_strings[from] + char('a' + i);
        //        states.push(to);
        //        viewed_states.insert(to);
        //    }
        //}

        std::list<string> min_strings;
        find_all_min_strings(big, min_strings);

        ofstream f(minstringpath);
        //cout << "answers:" << std::endl;
        if (min_strings.empty()) {
            //cout << "NO ANSWER" << std::endl;
            // f << "NO ANSWER";
        } else {
            for (auto& nextstring : min_strings)
            {
                //cout << nextstring << std::endl;
                f << nextstring << std::endl;
            }
        }
    }

    return 0;
}

std::map<char, char> nsymb2symb = { { 'a', 'a' },{ 'c', 'c' },{ 'b', 'g' },{ 'd', 't' } };
void find_all_min_strings(std::shared_ptr<Automata>& big, std::vector<int>& min_paths, int currentNode, list<string>& result) {
    result.clear();
    if (min_paths[currentNode] == 0) {
        result.push_back("");
        return;
    }
    for (int prevNode = 0; prevNode < big->state_count(); ++prevNode) {
        if (min_paths[prevNode] != min_paths[currentNode] - 1) {
            continue;
        }

        std::list<int> symbols;
        for (int i = 0; i < 4; ++i) {
            if (big->get_to_state(prevNode, i) == currentNode) {
                symbols.push_back(i);
            }
        }

        list<string> subresult;
        if (symbols.empty() == true) {
            continue;
        }

        find_all_min_strings(big, min_paths, prevNode, subresult);
        for (auto symb : symbols) {
            for (auto res : subresult) {
                result.push_back(res.append(1, nsymb2symb['a' + symb]));
            }
        }
    }
}

void find_all_min_strings(std::shared_ptr<Automata>& big, std::list<string>& min_strings) {
    min_strings.clear();
    std::vector<int> min_paths(big->state_count(), std::numeric_limits<int>::max());
    min_paths[0] = 0;

    std::queue<int> states;
    std::set<int> viewed_states;
    states.push(0);
    viewed_states.insert(0);
    min_paths[0] = 0;
    while (states.empty() == false) {
        auto from = states.front();
        states.pop();
        for (int i = 0; i < 4; ++i) {
            int to = big->get_to_state(from, i);
            if (viewed_states.count(to) > 0)
                continue;
            min_paths[to] = min_paths[from] + 1;
            states.push(to);
            viewed_states.insert(to);
        }
    }

    // assert(big->terminal_states.size() == 1);
    for (int i = 0; i < big->state_count(); ++i) {
        if (big->is_terminal(i) == false)
            continue;

        list<string> subresult;
        find_all_min_strings(big, min_paths, i, subresult);
        min_strings.insert(min_strings.end(), subresult.begin(), subresult.end());
    }
}
