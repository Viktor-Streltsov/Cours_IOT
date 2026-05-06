if 5 == 5:  # Условие если условие true то оно выполница если нет то нет
    print('yes')

user_data = int(input('Enter a number: '))  # Ввод числа
# > < = !=

if user_data % 2 == 0:  # Если число четное то true если нет то false
    print('Number is even')

if user_data % 2 != 0:  # Если число четное то false если нет то true
    print('Number is odd')

# | Или или |

if user_data % 2 == 0:
    print('Number is even')
else:
    print('Number is odd')

# Булиан значение
isHappy = False

if isHappy:
    print('Happy')

if not isHappy:
    print('Not Happy')

# elif Второе условие
if user_data % 2 == 0:
    print('Number is even')
elif user_data == 5:
    print('Just Number')
else:
    print('Number is odd')

# and (и) или or (или)
if user_data % 2 == 0 and not isHappy:
    print('Number is even')
elif user_data == 5 or isHappy:
    print('Just Number')
else:
    print('Number is odd')

# Тернарный оператор

data = input('Enter a number: ')

number = 5 if data == 'Five' else 0

# if data == 'Five':
#     number = 5
# else:
#     number = 0

print(number)
