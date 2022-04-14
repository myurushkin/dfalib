import regex


def reverse_string(string, repl):
    repl = repl if repl else {'(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{'}
    replacement = dict((regex.escape(k), v) for k, v in repl.items())
    pattern = regex.compile("|".join(replacement.keys()))
    result = list(pattern.sub(lambda m: replacement[regex.escape(m.group(0))], string))
    result.reverse()
    return ''.join(result)
