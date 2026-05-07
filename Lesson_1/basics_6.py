# Кортежи
# не изменяемые , весят меньше
# Получение и отправка данных пользователю или серверу

data = (3, 4, 5, 6, 4, 3, 4, 'Hello', True)

# data[0] = 5 -- Нельзя переприсваивать константа

print(data[1])
print(data[1:5])

print(data.count(6))  # Колчество похожих элементов
print(len(data))  # Длина кортежа

data_2 = 5, 4, 56, 7, True  # Тоже создание кортежа
data_3 = (5,)  # Тоже создание кортежа
data_4 = 5,  # Тоже создание кортежа

print(data_2)

for el in data:
    print(el)

names = [5, 6, 7]  # Список

new_data = tuple(names)  # Преобразование списка в кортеж
print(new_data)

str = 'Hell world'
word = tuple(str)  # Преобразование строки в кортеж
print(word)
