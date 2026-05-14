# Создаем класс Cat
class Cat:
    # Атрибуты класса (по умолчанию пустые)
    name = None
    age = None
    isHappy = None

    # Метод для установки данных кота
    def set_data(self, name, age, isHappy):
        self.name = name  # Имя кота
        self.age = age  # Возраст кота
        self.isHappy = isHappy  # Счастлив ли кот

    # Метод для вывода информации о коте
    def get_data(self):
        print(
            'Name:', self.name,
            '| Age:', self.age,
            '| Happy:', self.isHappy
        )

    # Дополнительный метод
    # Показывает человеческое описание настроения
    def say_mood(self):
        if self.isHappy:
            print(self.name, 'is happy 😸')
        else:
            print(self.name, 'is sad 😿')


# Создаем первый объект
cat1 = Cat()
cat1.set_data('Batsil', 3, True)

# Создаем второй объект
cat2 = Cat()
cat2.set_data('Grou', 5, False)

# Вывод информации
cat1.get_data()
cat1.say_mood()

print('----------------')

cat2.get_data()
cat2.say_mood()
