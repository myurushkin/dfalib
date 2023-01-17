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


def max_hairpin_strength(nuclString:str):
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