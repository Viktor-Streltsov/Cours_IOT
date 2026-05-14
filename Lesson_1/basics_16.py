# ================================
# ООП В PYTHON
# Наследование, Полиморфизм, Инкапсуляция
# ================================


# =========================================
# БАЗОВЫЙ КЛАСС
# =========================================

class Building:
    # Конструктор класса
    def __init__(self, year, city):
        self.year = year
        self.city = city

    # Метод вывода информации
    def get_info(self):
        print(f'Building in {self.city}, built in {self.year}')


# =========================================
# НАСЛЕДОВАНИЕ
# =========================================
# School наследуется от Building
# Это значит:
# School получает все свойства и методы Building

class School(Building):

    def __init__(self, pupils, year, city, school_name):
        # Вызываем конструктор родителя
        super().__init__(year, city)

        # Добавляем новые свойства
        self.pupils = pupils
        self.school_name = school_name


# House тоже наследуется от Building
class House(Building):

    def __init__(self, floors, year, city):
        super().__init__(year, city)
        self.floors = floors


# =========================================
# ПОЛИМОРФИЗМ
# =========================================
# Один и тот же метод работает по-разному
# в разных классах

class Shop(Building):

    def __init__(self, products, year, city):
        super().__init__(year, city)
        self.products = products

    # Переопределяем метод get_info()
    def get_info(self):
        print(
            f'Shop in {self.city}, '
            f'year: {self.year}, '
            f'products: {self.products}'
        )


# School тоже переопределяет метод
class ModernSchool(School):

    def get_info(self):
        print(
            f'School: {self.school_name}, '
            f'city: {self.city}, '
            f'pupils: {self.pupils}'
        )


# =========================================
# ИНКАПСУЛЯЦИЯ
# =========================================
# Скрываем данные внутри класса

class Bank:

    def __init__(self, money):
        # Приватное свойство
        self.__money = money

    # Метод для получения денег
    def get_money(self):
        return self.__money

    # Метод для изменения денег
    def set_money(self, value):

        # Проверяем данные
        if value < 0:
            print("Balance cannot be negative!")
        else:
            self.__money = value


# =========================================
# СОЗДАНИЕ ОБЪЕКТОВ
# =========================================

school = ModernSchool(500, 2005, 'Moscow', 'IT School')
house = House(12, 2015, 'Bishkek')
shop = Shop(3000, 2010, 'Almaty')

# Полиморфизм
# Один метод get_info()
# но разное поведение

school.get_info()
shop.get_info()
house.get_info()

print('----------------')

# Инкапсуляция

bank = Bank(1000)

# Получаем значение через метод
print("Money:", bank.get_money())

# Меняем значение
bank.set_money(5000)

print("New balance:", bank.get_money())

# Ошибка проверки
bank.set_money(-100)
