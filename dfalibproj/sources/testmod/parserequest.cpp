#include <algorithm>
#include <cctype>
#include <cassert>
#include <memory>
#include <stdexcept>
#include "parserequest.h"

void private_create_automata(std::list<Token>& input, std::list<Token>::iterator& it,
	std::stack<std::shared_ptr<GrammarExprTree>>& tokens, std::stack<char>& control) {

	while (it != input.end()) {
		Token symb = *it++;

		if (symb.type == Token::Item) {
			tokens.push(GrammarExprTree::createItemNode(symb.item));
			continue;
		}

		if (symb.type == Token::OpenScope) {
			control.push('(');
			private_create_automata(input, it, tokens, control);
		}
		if (symb.type == Token::CloseScope) {
			while (control.top() != '(') {
				char op = control.top();
				control.pop();
				if (op != '|') {
					throw std::runtime_error("smth is wrong");
				}

				std::shared_ptr<GrammarExprTree> second_token = tokens.top();
				tokens.pop();
				std::shared_ptr<GrammarExprTree> first_token = tokens.top();
				tokens.pop();
				tokens.push(GrammarExprTree::createOpNode('|', first_token, second_token));
			}

			assert(control.top() == '(');
			control.pop();
			return;
		}

		if (symb.type == Token::Operation && symb.op == '|') {
			control.push(symb.op);
			continue;
		}

		if (symb.type == Token::Operation && symb.op == '*') {
			if (it->type == Token::OpenScope) {
				control.push('(');
				private_create_automata(input, ++it, tokens, control);
			}
			else {
				Token symb = *it++;
				tokens.push(GrammarExprTree::createItemNode(symb.item));
			}

			std::shared_ptr<GrammarExprTree> second_token = tokens.top();
			tokens.pop();
			std::shared_ptr<GrammarExprTree> first_token = tokens.top();
			tokens.pop();
			tokens.push(GrammarExprTree::createOpNode('*', first_token, second_token));
			continue;
		}
	}
}

std::shared_ptr<GrammarExprTree> parse_request(std::string rexpr) {
	std::stack<std::shared_ptr<GrammarExprTree>> tokens;
	std::stack<char> control;

	std::list<Token> input;
	char control_symbols[] = "|()";
	int control_symbols_count = sizeof(control_symbols) / sizeof(char);

	bool prev_symb_ischar = false;
	for (int i = 0; i < rexpr.size(); ++i) {
		if (rexpr[i] == ' ') {
			continue;
		}

		bool current_symb_isletter = std::find(control_symbols,
			control_symbols + control_symbols_count, rexpr[i]) == control_symbols + control_symbols_count;
		if (prev_symb_ischar == true && (current_symb_isletter == true || rexpr[i] == '(')) {
			input.push_back('*');
		}

		prev_symb_ischar = current_symb_isletter || rexpr[i] == ')';

		if (rexpr[i] == '(') {
			input.push_back(Token(Token::OpenScope));
			continue;
		}
		if (rexpr[i] == ')') {
			input.push_back(Token(Token::CloseScope));
			continue;
		}
		if (rexpr[i] == '|') {
			input.push_back(Token('|'));
			continue;
		}

		int j = i + 1;
		while (j < rexpr.size() && (isalpha(rexpr[j]) || isalnum(rexpr[j]) || rexpr[j] == '_')) {
			++j;
		}

		input.push_back(rexpr.substr(i, j - i));
		i = j - 1;
	}

	auto it = input.begin();
	private_create_automata(input, it, tokens, control);
	assert(control.size() == 0 && tokens.size() == 1);
	return tokens.top();
}
