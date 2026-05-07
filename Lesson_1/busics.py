nums = [5, 67, 'text', False]  # Создание списка
print(nums)

nums[0] = 467  # Изменение элемента

print(nums)
print(nums[3])

nums_2 = [5, 68, [5, 8]]

print(nums_2[-1][0])  # Вывод вложенного списка

numbers = [5, 2, 7]

numbers.append(100)  # Добавление элемента в конец списка
numbers.insert(1, True)  # Добавление элемента по индексу
numbers.extend([3, 6, 7])  # Добавление списка элементов
numbers.sort()  # Сортировка
numbers.reverse()  # Переворот местами реверсивный список
numbers.pop(1)  # Удаление последнего элемента так же удаление по индексу
numbers.remove(6)  # Удаление определенного элемента
# numbers.clear() # Полное удаление
numbers.count(5)  # Количество похожих элементов
len(numbers)  # Длина списка

print(numbers)

# Перебор списка

nums_elem = [5, 2, 7, '50', True]

for el in nums_elem:
    el *= 2
    print(el)
