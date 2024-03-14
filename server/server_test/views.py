from django.http import HttpResponse, JsonResponse
from .models import testTable

def testServer(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    return HttpResponse("OK")

def testArgs(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    val = request.GET['param']
    return HttpResponse(f"Got argument: {val}")

def testJson(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    return JsonResponse({"data": [1, 2, 3, 4, 5], "data2": [2, 3, 4, 5, 6]})

def testDB(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    # получаем все объекты
    items = testTable.objects.all()
    #print(items.query)
    
    # здесь происходит выполнения запроса в БД
    response = []
    for item in items:
        #print(f"{item.id}.{item.name} - {item.age}")
        response.append((item.id, item.name, item.age))

    return JsonResponse({"data": response})

def fillDB(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    val1, val2 = (request.GET['param']).split(" ")[:2]
    entry = testTable.objects.create(name=val1, age=val2)
    print(entry.id)
    return HttpResponse("GOOD")



def auth(request):  #При входе в клиент будет проверять права
    print(f"RECIEVED {request.get_host()}: {request.GET}")

    return 

def getData(request): #В зависимости от пользователя будет выдавать его данные
    print(f"RECIEVED {request.get_host()}: {request.GET}")

    return 

def upData(request): #Обновляет  содержимое базы данных - удаляет, добавляет или изменяет записи.
    print(f"RECIEVED {request.get_host()}: {request.GET}")

    return 

def docData(request):#Собирает все данные для генерации документа 
    print(f"RECIEVED {request.get_host()}: {request.GET}")                 #(Отличается от getData отсутствием необходимости разделять по учителям, взамен разделяя по кафедрам, например.)

    return