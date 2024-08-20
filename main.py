import client

try:
    with open('nickname.txt', 'r') as f:
        nick = f.readline()

except FileNotFoundError:
    nick = input('Введите ник: ')
    with open('nickname.txt', 'w') as f:
        f.write(nick)

me = client.Client(20122, nick)
try:
    me.Host(1)
except OSError:
    me.Connect()
