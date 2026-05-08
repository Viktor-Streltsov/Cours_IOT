# Функции

def test_func(word):  # Создание функции с параметрами
    print(word)


test_func('Hello World')  # Вызов функции
test_func(45)


def summa(a, b):
    print(a * b)
    return a + b


res = summa(5, 9)

print(summa(4, 2))
print(res)

# 1 вариан

nums1 = [5, 7, 2, 9, 4]

min = nums1[0]
for el in nums1:
    if el < min:
        min = el

print(min)


# 2 вариан через функцию

def minimal(l):
    min_num = l[0]
    for el in l:
        if el < min_num:
            min_num = el

    return min_num


nums1 = [5, 7, 2, 9, 4]
min1 = minimal(nums1)

nums2 = [5.4, 7.2, 2.3, 9.5, 4.7, 2.1]
min2 = minimal(nums2)

if min < min2:
    print(min1)
else:
    print(min2)

# Лямда функции (ананимные)

func = lambda x, y: x * y
print(func(5, 2))
