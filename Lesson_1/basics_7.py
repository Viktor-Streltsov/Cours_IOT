# Словари
# key может быть num, str, boolean, кортежем

diction = {'key': 3}
print(diction['key'])

country = {'code': 'RU', 'name': 'Russian', 'population': 144}  # Создание словаря более удобо
print(country['code'])

county_2 = dict(code='RU', name='Russian', population=144)  # Создание словаря

print(county_2)

print(county_2.items())

for key, value in county_2.items():  # Перебор словаря
    print(key, ' - ', value)

print(county_2['code'])
print(county_2.get('code'))
# county_2.clear() #Очистка
# print(county_2.pop('name'))  # Удаление по ключу
# print(county_2.popitem())  # Удаление последнего элемента
print(county_2.keys())  # Ввод клчей
print(county_2.values())  # Вывод значений
print(county_2.items())  # Ввод всего

# Обновление ключей соворя
county_2['step'] = 'none'
county_2.update(code='some_value')
print(county_2)

person = {
    'user_1': {
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 25,
        'address': ['г. Москва', 'ул. Какая-то', '34'],
        'grader': {'math': 5, 'physics': 4}
    }
}

print(person['user_1']['address'][0])  # Вывод определенного элемента из словоря
