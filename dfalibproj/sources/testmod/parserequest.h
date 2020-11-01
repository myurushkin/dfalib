#ifndef PARSE_REQUEST_H
#define PARSE_REQUEST_H

#include <list>
#include <stack>
#include <memory>
#include <vector>
#include <string>

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
	std::vector<std::shared_ptr<GrammarExprTree>> childs;

	static std::shared_ptr<GrammarExprTree> createItemNode(std::string name) {
		std::shared_ptr<GrammarExprTree> result(new GrammarExprTree());
		result->name = name;
		return result;
	}
	static std::shared_ptr<GrammarExprTree> createOpNode(char op, std::shared_ptr<GrammarExprTree> left, std::shared_ptr<GrammarExprTree> right) {
		std::shared_ptr<GrammarExprTree> result(new GrammarExprTree());
		result->op = op;
		result->childs.resize(2);
		result->childs[0] = left;
		result->childs[1] = right;
		return result;
	}
};

std::shared_ptr<GrammarExprTree> parse_request(std::string rexpr);

#endif
