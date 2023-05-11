from functools import *

''' Новая версия определения силы шпильки'''
def complement(nucl1:chr,nucl2:chr):
    state = False
    match (nucl1,nucl2):
        case ('a','t'):
            state = True
        case ('t','a'):
            state = True
        case ('g','c'):
            state = True
        case ('c','g'):
            state = True
    return state


def chkLegs(leg1:[str],leg2:[str]):
    a = leg1
    b = leg2[::-1]
    counter = 0
    maxStrength = 0
    if len(a) != len(b):
        print('Плечи не равны! Проверить вручную {leg1} и {leg2}'.format(leg1=leg1,leg2=leg2))
    for i in range(0,len(a)):
        if complement(a[i], b[i]):
            counter += 1
        else:
            if counter > 1:
                maxStrength += counter
                counter = 0
            else:
                counter = 0
    if counter > 1:
        maxStrength += counter
    return maxStrength


def dissect(nuclString:str):
    if len(nuclString) % 2 == 0:
        stemLength = len(nuclString) // 2 - 2
        lleg, head, rleg = nuclString[0: stemLength], nuclString[stemLength:stemLength+4], nuclString[stemLength+4:]
    else:
        stemLength = len(nuclString) // 2 - 1
        lleg, head, rleg = nuclString[0: stemLength], nuclString[stemLength:stemLength+3], nuclString[stemLength+3:]
    return lleg,head,rleg


@cache


def max_hairpin_strength_3(items):
    n = len(items)
    if n < 5:
        return 0, tuple([])

    value_first = -1
    picture_first = []
    for ind in range(n-1, 0, -1):
        if complement(items[0][1], items[ind][1]) and ind >= 4:
            val1, pic1 = max_hairpin_strength_3(items[1:ind])
            val2, pic2 = max_hairpin_strength_3(items[ind + 1:])
            val = 1 + val1 + val2
            if val > value_first:
                value_first = val
                picture_first = [(items[0][0], items[ind][0])]
                picture_first.extend(pic1)
                picture_first.extend(pic2)

    value_second = -1
    picture_second = []
    for ind in range(n):
        if complement(items[ind][1], items[-1][1]) and len(items) - ind >= 5:
            val1, pic1 = max_hairpin_strength_3(items[:ind])
            val2, pic2 = max_hairpin_strength_3(items[ind + 1: -1])
            val = 1 + val1 + val2
            if val > value_second:
                value_second = val
                picture_second = [(items[ind][0], items[-1][0])]
                picture_second.extend(pic1)
                picture_second.extend(pic2)
            #value_second = max(value_second, 1 + max_hairpin_strength_2(s[ind+1:-1]) + max_hairpin_strength_2(s[:ind]))

    value_third, picture_third = max_hairpin_strength_3(items[1:-1])
    #picture_third = list(filter(lambda x: x is not None, picture_third))

    return max([(value_first, picture_first),
                (value_second, picture_second),
                (value_third, picture_third)], key = lambda x: x[0])

def max_hairpin_strength_2(s:str):
    ss = tuple(enumerate(s))
    return max_hairpin_strength_3(ss)

def max_hairpin_strength(nuclString:str):
    return max_hairpin_strength_2(nuclString)[0]
    '''Строка делится пополам, одна половина записывается в первый массив, вторая во второй. Если деление
    неравномерно, то дописывается вначале ноль. Построить в форме рекурсии. Сделать отдельно функцию, которая проверяет
    подряд идущие связи и рекурсивно пихать в неё разные пары массивов. Продумать, что если находить максимальную
    последовательность и дальше уже нет в принципе более длинных хвостов, то обрывается. Может тоже функцией оформить?
    В функцию подсчёта вставить параметр theoretical_strength и при варьировании шпильки обращаться к нему. Если мы попали
    в theoretical_strength, то всё, обрыв.'''
    #tForce -Теоретически возможная сила для анализируемой шпильки
    #mForce - Пока что максимальная сила
    #cForce - Текущая сила
    i = 1
    flag = False
    #Проверяем нулевой случай, исходную строку
    lleg, head, rleg = dissect(nuclString)
    mForce = chkLegs(lleg,rleg)
    tForce = len(lleg)

    if mForce != tForce:
        while not flag:
            lleg,head,rleg = dissect(nuclString[i:])
            cForce = chkLegs(lleg,rleg)
            tForce = len(lleg)
            if cForce > mForce:
                mForce = cForce
            if mForce >= tForce:
                flag = True
            lleg,head,rleg = dissect(nuclString[:-i])
            cForce = chkLegs(lleg,rleg)
            tForce = len(lleg)
            if cForce > mForce:
                mForce = cForce
            if mForce >= tForce:
                flag = True
            i += 1
    return mForce


# if __name__ == '__main__':
#     with open("C:\\Users\\Docent\\Desktop\\Projects\\Python\\work\\test.txt") as file:
#         with open("C:\\Users\\Docent\\Desktop\\Projects\\Python\\work\\results.txt",'w') as results:
#             for string in file:
#                 results.write(string.strip('\n')+'----' + str(max_hairpin_strength(string))+'\n')