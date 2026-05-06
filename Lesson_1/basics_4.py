# Цикл for
# Использовать для перебора данных

# range диапозон
# от 0 до 5 (renge(6)),
# от 1 до 5 (renge(1, 6)) если добавить 3 параметр это на сколько будет увеличиваться переменная при каждо итерации
# Если надо от 1 до 6 включительно то можно в цикле сделать print(i + 1)

for i in range(1, 6):
    print(i)

word = 'Hello World'
count = 0

for i in word:
    print(i)

for i in word:
    if i == 'l':
        print("Yes")
        count += 1

print('Count: ', count)

# Цикл while

i = 5

isHasCar = True  # Бесконечный цикл

while i < 15:
    print(i)
    i += 2

# Правельное использование бесконечного цикла

# Использовать для условий и дальнейшей работы цикла
while isHasCar:
    if input('Enter data: ') == 'Stop':
        isHasCar = False

# Выход из цикла и пропуск итерации
for i in range(1, 6):
    if i == 5:
        break  # выход
    if i % 2 == 0:
        continue  # пропуск

    print(i)
