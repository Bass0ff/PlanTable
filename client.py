import requests

print("Выберите команду:\n-пустая строка - Проверка соединения\n-check - Проверка аргумента\n-checkjson - проверка принятия json-ответа\n-checkdb - проверка работы с БД\n-filldb - новая запись в БД\n-quit - закрыть клиент")
url = input("Введите команду: ")  

if url == "quit":
    exit()

while True:
    prompt = input("TESTER > ")
    if prompt == "/quit":
        print("Выберите команду:\n-пустая строка - Проверка соединения\n-check - Проверка аргумента\n-checkjson - проверка принятия json-ответа\n-checkdb - проверка работы с БД\n-filldb - новая запись в БД\n-quit - закрыть клиент")
        url = input("Введите команду: ")
        if url == "quit":
            exit()
        continue
    try:
        response = requests.get(f"http://127.0.0.1:8000/{url}", params={"param": prompt})
        if url == "checkjson" or url == "checkdb":
            print("SERVER >", response.json())
            print(response.json()['data'][0])
        else:
            print("SERVER >", response.text)
    except requests.exceptions.ConnectionError:
        print("Сервер не включен.")
    
