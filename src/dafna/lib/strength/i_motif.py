import regex


def i_motif_max_strength(string, biological_significance: bool = False):
    x_group = '[a|c|g|t]'
    y_symbol = '[t|c]'
    n = '1,'
    m = '1,'
    strength = 0
    biological_significance_pattern = '((c{{{n}}}){X}{{1,}}?(c{{{m}}}){X}{{1,}}?()\\2{X}{{1,}}?()\\3)'
    pattern = biological_significance_pattern.format(Y=y_symbol, X=x_group, n=n, m=m)
    match = regex.findall(pattern, string)
    if any(match):
        for i_motif in match:
            sub_strength = (len(i_motif[1]) + len(i_motif[2])) / 2
            for i in range(3, len(i_motif[1]) + 1):
                sub_match = regex.findall(
                    biological_significance_pattern.format(Y=y_symbol, X=x_group, n=i, m=m), string)[0]
                if any(sub_match):
                    temp_strength = (len(sub_match[1]) + len(sub_match[2])) / 2
                    sub_strength = sub_strength if sub_strength > temp_strength else temp_strength

            strength = strength if strength > sub_strength else sub_strength

    return strength
