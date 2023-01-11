import re
import itertools

# Убираем повторы и строки, где 2 икса подряд
def filterUnique(arraySeq: [str]):
    maxLength = len(arraySeq[-1])
    resArray = []
    for seq in arraySeq:
        if ('x' * 2) in seq:
            continue
        else:
            resArray.extend([seq])
    resDict = {}
    for seq in resArray:
        for length in range(2, maxLength // len(seq) + 1):
            if seq * length in resArray:
                resDict[seq * length] = 1
        if seq in resDict.keys():
            resDict[seq] = 1
        else:
            resDict[seq] = 0
    resDict2 = dict((k, v) for k, v in resDict.items() if v == 0)
    return resDict2


# Генерирует все уникальные комбинации вида gx, где g - гуанин, x-любой нуклеотид
def comb(input_string_len: int):
    binArray = []
    """Размер подстроки тандемного повтора берём равным 4. Логика простая - предельный случай максимального 
    G-квадруплекса
    представляет собой 4 полиГ цепи с 1 нуклеотидом перемычкой между ними. Все случаи тандемных повторов, как бы
     они не были распределены,
    представляют собой более разреженый вариант этой последовательности, а значит искать уникальный фрагмент,
     который повторяется менее
    4 раз бессмысленно. Хотя надо подумать и доказать это как-то строже?"""
    length = input_string_len // 4
    for counter in range(2, length + 1):
        combinations = list(filter(lambda x: 'g' in x and 'x' in x,
                                   map(lambda x: "".join(x), itertools.product('gx', repeat=counter))))
        binArray.extend(combinations)
    result = list(filterUnique(sorted(set(binArray), key=len)))
    return result


def analgc(input_string: str, templateArray: [str]):
    maxTemplate = ''
    maxForce = 0
    for l in templateArray:
        # делаем из элемента последовательности регулярку
        rl = re.compile(l.replace('x', '\w'))
        nsForce = l.count('g') * len(rl.findall(input_string))
        lowQ = len(input_string) // 4
        highQ = (len(input_string) * 3) // 4
        if (nsForce > maxForce) and (not re.search('[act]{2,}', input_string[lowQ:highQ])):
            maxTemplate = l
            maxForce = nsForce
    gStrength = maxForce // 4
    return gStrength, maxTemplate, input_string


def max_strength(input_string):
    templateArray = comb(len(input_string))
    return analgc(input_string, templateArray)[0]
