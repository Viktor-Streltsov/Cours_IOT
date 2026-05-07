word = 'Football,basketball,skate'

print(word[5])
print(len(word))
print(word.count('l'))

print(word.upper())  # Верхний регистр
print(word.isupper())  # Проверка верхнего регистра
print(word.islower())  # Проверка нижнего регистра
print(word.lower())  # Нижний регистр
print(word.capitalize())  # Первый элемент в верхнем регистре
print(word.find('l'))  # Выведение индекса регистра
# print(word.split(','))  # Разбиение по элементу

hobby = word.split(',')

for i in range(len(hobby)):
    hobby[i] = hobby[i].capitalize()

print(hobby)

result = ', '.join(hobby)

print(result)

# Срезы

word_2 = 'Football'

print(word_2[0: 4])  # Срез первых 4 элементов
print(word_2[4:])  # Срез от 4 до конца
print(word_2[1:6:2])  # Срез с шагом перескакиваем через 1 элемент

list = [6, 2, 'Struks', True, 6.5]

print(list[2:])  # Вывод елементов со 2 индекса
print(list[2:-1])
# или
print(list[2:4])
print(list[2:4:2])
