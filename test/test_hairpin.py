import random
import unittest

import regex
import rstr
import pprint
import dafna


class TestHairpin(unittest.TestCase):
    def test_01(self):
        generator = range(2, 21)

        def hairpin_random_string(strength):
            n = random.randint(1, strength-1)
            m = strength - n

            assert m+n == strength

            def replace_complimentary_symbol(string):
                repl = {'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
                replacement = dict((regex.escape(k), v) for k, v in repl.items())
                pattern = regex.compile("|".join(replacement.keys()))
                return "".join(list(pattern.sub(lambda m: replacement[regex.escape(m.group(0))], string)))

            hairpin_head_pattern = f'((a|t){{{n}}})(a|t|g|c){{0,3}}((g|c){{{m}}})'
            hairpin_loop_pattern = '(a|t){3,7}'
            hairpin_tail_pattern = '({gc_group}(a|c|g|t){{0,3}}{at_group})'

            hairpin_head = rstr.xeger(hairpin_head_pattern)
            hairpin_loop = rstr.xeger(hairpin_loop_pattern)
            sub_groups = regex.findall(hairpin_head_pattern, hairpin_head)[0]
            hairpin_tail = rstr.xeger(hairpin_tail_pattern.format(
                gc_group=replace_complimentary_symbol(sub_groups[3][::-1]),
                at_group=replace_complimentary_symbol(sub_groups[0][::-1])
            )
            )

            return f'{hairpin_head}{hairpin_loop}{hairpin_tail}'

        def hairpin_max_strength(string):
            def replace_complimentary_symbol(string):
                repl = {'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
                replacement = dict((regex.escape(k), v) for k, v in repl.items())
                pattern = regex.compile("|".join(replacement.keys()))
                return "".join(list(pattern.sub(lambda m: replacement[regex.escape(m.group(0))], string)))
            strength = 0
            n_count = '1,'
            m_count = '1,'
            pattern = \
                '({at_group})[a|t|g|c]{{0,3}}?({gc_group})[a|t|g|c]{{3,7}}({gc_complimentary_group})[a|t|g|c]{{0,3}}({at_complimentary_group})'
            start_pattern = '([a|t]{{{n_count}}})[a|t|g|c]{{{bubble_count}}}([g|c]{{{m_count}}})'
            match = []
            for i in range(0,4):
                match += regex.findall(start_pattern.format(n_count=n_count, m_count=m_count, bubble_count=i), string)
            if any(match):
                for hairpin_head_part in match:
                    n = len(hairpin_head_part[0])
                    for i in range(n, 0, -1):
                        for bubble_count in range(0,4):
                            sub_match = regex.findall(start_pattern.format(n_count=i, m_count=m_count, bubble_count=bubble_count), string)
                            if any(sub_match):
                                at_group, at_complimentary_group = sub_match[0][0], replace_complimentary_symbol(sub_match[0][0][::-1])
                                gc_group, gc_complimentary_group = sub_match[0][1], replace_complimentary_symbol(sub_match[0][1][::-1])
                                a = pattern.format(
                                        gc_group=gc_group,
                                        gc_complimentary_group=gc_complimentary_group,
                                        at_group=at_group,
                                        at_complimentary_group=at_complimentary_group
                                    )
                                full_match = regex.findall(pattern.format(
                                        gc_group=gc_group,
                                        gc_complimentary_group=gc_complimentary_group,
                                        at_group=at_group,
                                        at_complimentary_group=at_complimentary_group
                                    ),
                                    string
                                )

                                if any(full_match):
                                    for match_case in full_match:
                                        temp_strength = len(match_case[0]) + len(match_case[2])
                                        strength = strength if strength > temp_strength else temp_strength
            return strength
        a = hairpin_random_string(6)
        print(a)
        # print(hairpin_max_strength(a))
        print(hairpin_max_strength('ttttgggaaattatccgaaaaa'))
