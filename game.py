from Client.client import Client

if __name__ == '__main__':
    user = input('Insira seu usuário: ')

    client = Client(user)
    client.start()
