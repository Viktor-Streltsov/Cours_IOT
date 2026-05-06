fount = None
word = input('Напишите слово: ')
symbol = input('Напишите символ: ')

for i in word:
    if i == symbol:
        found = True
        break
    else:
        found = False

print(found)
