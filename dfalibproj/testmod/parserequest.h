#ifndef PARSE_REQUEST_H
#define PARSE_REQUEST_H

#include <list>
#include <stack>
#include <vector>

struct Token {
	enum Type {
		None,
		Item,
		Operation,
		OpenScope,
		CloseScope
	};

	Token()
		: op(0), type(None) {
	}

	Token(Type type)
		: op(0), type(type) {
	}
	Token(char op)
		: op(op), type(Operation) {
	}
	Token(std::string item)
		: op(0), item(item), type(Item) {
	}

	char op;
	std::string item;
	Type type;
};

struct GrammarExprTree {
	char op;
	std::string name;
	std::vector<GrammarExprTree*> childs;

	static GrammarExprTree* createItemNode(std::string name) {
		GrammarExprTree* result = new GrammarExprTree();
		result->name = name;
		return result;
	}
	static GrammarExprTree* createOpNode(char op, GrammarExprTree* left, GrammarExprTree* right) {
		GrammarExprTree* result = new GrammarExprTree();
		result->op = op;
		result->childs.resize(2);
		result->childs[0] = left;
		result->childs[1] = right;
		return result;
	}
};

void parse_request(std::string rexpr, GrammarExprTree*& result);

#endif
