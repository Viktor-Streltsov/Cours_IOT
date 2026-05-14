class Cat:
    name = None
    age = None
    isHappy = None

    def set_data(self, age, name, isHappy):
        self.name = name
        self.age = age
        self.isHappy = isHappy

    def get_data(self):
        print(self.name, 'age:', self.age, '. Happy:', self.isHappy)


cat1 = Cat()
cat1.set_data('Batsil', 3, True)

cat2 = Cat()
cat2.set_data('Grou', 5, False)

cat1.get_data()
