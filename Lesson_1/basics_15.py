# Класс Cat
class Cat:
    # Конструктор класса
    # __init__ автоматически вызывается при создании объекта
    def __init__(self, name, age, isHappy=None):
        self.name = name  # Имя кота
        self.age = age  # Возраст кота
        self.isHappy = isHappy  # Настроение кота

        print("Object created")

    # Метод для изменения данных объекта
    # Можно передавать новые значения после создания объекта
    def set_data(self, name=None, age=None, isHappy=None):

        # Проверяем переданы ли новые значения
        # Если да — обновляем поля объекта

        if name is not None:
            self.name = name

        if age is not None:
            self.age = age

        if isHappy is not None:
            self.isHappy = isHappy

    # Метод для вывода информации
    def get_data(self):
        print(
            'Name:', self.name,
            '| Age:', self.age,
            '| Happy:', self.isHappy
        )

    # Дополнительный метод
    def say_meow(self):
        print(self.name, "says: Meow 😺")


# Создание объекта
# Здесь вызывается конструктор __init__
cat1 = Cat('Barsik', 3, True)

# Вывод данных
cat1.get_data()

# Изменение данных объекта
cat1.set_data('John', 2)

print("After changes:")
cat1.get_data()

cat1.say_meow()

print('----------------')

# Второй объект
cat2 = Cat('Hander', 2, False)

cat2.get_data()
cat2.say_meow()
