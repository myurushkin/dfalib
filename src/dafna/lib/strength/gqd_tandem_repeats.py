import re
import itertools


# Убираем повторы и строки, где 2 икса подряд
def filterUnique(arraySeq: [str]):
    resArray = []
    for seq in arraySeq:
        if ('x' * 2) in seq:
            continue
        else:
            resArray.extend([seq])
    return resArray


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


# PSA - pattern sections amount - функция, подсчитывающая сколько раз подряд встречается паттерн
def psa(pattern: str, nuclString: str):
    i = 0
    flag = False
    while not flag:
        i += 1
        rl = re.compile(pattern.replace('x', '\w') * i)
        if rl.findall(nuclString):
            i += 1
        else:
            i -= 1
            flag = True
    return i


def analgc(input_string: str, templateArray: [str]):
    # делаем из элемента последовательности регулярку
    lowQ = len(input_string) // 4
    highQ = (len(input_string) * 3) // 4
    maxForce = 0
    maxTemplate = ''

    if not re.search('[act]{2,}', input_string[lowQ:highQ]):
        for l in templateArray:
            rl = re.compile(l.replace('x', '\w') * 4)
            nsForce = l.count('g')
            if nsForce > maxForce and rl.findall(input_string):
                maxForce = nsForce
                maxTemplate = l
    gStrength = maxTemplate.count('g')
    if gStrength == 1:
        gStrength = 0
    # return gStrength, maxTemplate, input_string
    return gStrength


def max_strength(input_string):
    # добавил по символу слева и справа чтобы нормально обсчитывались обрезанные ТП типа ggaggaggagg
    input_string = 'x' + input_string + 'x'
    templateArray = comb(len(input_string))
    return analgc(input_string, templateArray)
