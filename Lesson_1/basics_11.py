# Исключения - error

x = int(input("Enter a number: "))
x += 5
print(x)  # Если пользователь введет символ букву то будет ошибка

# Отслеживание ошибок
try:
    x = int(input("Enter a number: "))
    x += 5
    print(x)
except ValueError:
    print("Please enter a number")

# Циклическая программа пока пользователь не напишет число она не остановиться
num = 0
while num == 0:
    try:
        x = int(input("Enter a number: "))
        x += 5
        print(x)
    except ValueError:
        print("Please enter a number")
    else:
        print('else')
    finally:
        print('Finished')
