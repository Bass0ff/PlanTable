from django.http import HttpResponse, JsonResponse
from .models import *

def testServer(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    return HttpResponse("OK")

def testArgs(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    print(request.GET['param'][0])
    val = request.GET['param']
    return HttpResponse(f"Got argument: {val}")

def testJson(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    return JsonResponse({"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]})

def testDB(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    # получаем все объекты
    items = testTable.objects.all().values()
    #print(items.query)
    
    # здесь происходит выполнения запроса в БД
    response = []
    for item in items:
        #print(f"{item.id}.{item.name} - {item.age}")
        response.append(item)
        print(item)

    return JsonResponse({"data": response})

def fillDB(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    val1, val2 = (request.GET['param']).split(" ")[:2]
    entry = testTable.objects.create(name=val1, age=val2)
    print(entry.id)
    return HttpResponse("GOOD")



def autho(request):  #При входе в клиент будет проверять права
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    name = request.GET['user']
    id = Teacher.objects.filter(name=name).values()[0]['id']
    acc = Teacher.objects.filter(name = name).values()[0]['access']
    password = request.GET['pass']
    is_valid = auth.objects.filter(teacher=id, password=password).exists()
    # print(is_valid)
    if is_valid:
        subj = Teacher.objects.filter(name=name).values()[0]['subject']
        # print(subj)
        print()
        return HttpResponse(f"{id}, {subj}, {acc}")    #Отправляем ID и предмет учителя на клиент
    else:
        print()
        return HttpResponse("NOPE")

def reg(request):   #При регистрации будет создавать новые записи в таблицах с паролями и преподавателями.
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    name = request.GET['name']      #ФИО преподавателя
    pwrd = request.GET['pass']      #Пароль пользователя
    subj = request.GET['subj']      #Предмет(ы)
    ctgr = request.GET['category']  #Квалификационная категория
    acss = request.GET['access']    #Уровень доступа
    is_exist = Teacher.objects.filter(name=name, subject=subj).exists()
    if is_exist:
        print()
        return HttpResponse("AE")   #Already Exists
    teach = Teacher.objects.create(name=name, subject=subj, qualification=ctgr, access=acss)
    id = teach.id
    # print(id)
    acc = auth.objects.create(password = pwrd, teacher=teach)
    print()
    return HttpResponse(id)

def getIndex(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    data = request.GET
    teacher = Teacher.objects.get(id=data['teacher'])
    rawDate = data['date'].split(".")
    date = str(rawDate[2]) + "-" + str(rawDate[1]) + "-" + str(rawDate[0])
    exists = Event.objects.filter(teacher = teacher, date = date, name = data['name']).exists()
    if exists:
        Teach = Event.objects.get(teacher = teacher, date = date, name = data['name'])
        return HttpResponse(Teach.id)
    else:
        return HttpResponse("-1")

def getData(request): #В зависимости от пользователя будет выдавать его данные
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    tab = request.GET['table']
    dataType = request.GET['type']
    Teach = Teacher.objects.get(id = request.GET['id'])
    match Teach.access:         #Проверяем уровень доступа
        case "Учитель":         #Достанет данные только по самому пользователю
            events = Event.objects.filter(teacher = Teach, table = tab)
        case "Зав. кафедрой":   #Достанет данные по кафедре
            pass
        case "Методист":        #Достанет все доступные данные
            events = Event.objects.filter(table = tab)    
    
    response = {"data": []}
    for event in events:    #Проходим по каждому отобранному событию
        t_id = event.teacher.id
        data = {"teacherName": event.teacher.name, "teacher": t_id, "type": dataType, "if": event.id, "date": event.date, "name": event.name, "table": event.table}
        match dataType:
            case "open_class":
                addData = OpenClass.objects.filter(event = event).values()[0]   #Код события - первичный ключ в остальных таблицах. Более одного варианта получить всё  равно невозможно.
            case "organization":
                addData = Organization.objects.filter(event = event).values()[0]
            case "expertise":
                addData = Expertise.objects.filter(event = event).values()[0]
            case "course":
                addData = Course.objects.filter(event = event).values()[0]
            case "experience":
                addData = Experience.objects.filter(event = event).values()[0]
            case "student_work":
                addData = StudentWork.objects.filter(event = event).values()[0]
        data.update(addData)
        response['data'].append(data)
            
    return JsonResponse(response)   #Отправлять будет словарь с данными

def unData(request):
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    index = request.GET['id']
    item = Event.objects.get(id=index)
    item.delete()
    return HttpResponse(index)   #Отправлять будет словарь с данными

def upData(request): #Обновляет содержимое базы данных - добавляет или изменяет записи.
    print(f"RECIEVED {request.get_host()}: {request.GET}")
    data = request.GET
    teacher = Teacher.objects.get(id=data['teacher'])
    rawDate = data['date'].split(".")
    date = str(rawDate[2]) + "-" + str(rawDate[1]) + "-" + str(rawDate[0])
    event, created = Event.objects.get_or_create(teacher = teacher, date = date, name=data['name'], table = data['table'])
    match data['type']:
        case "open_class":
            #values - данные, которые обновятся, если найдётся дочернее событие от event
            values = {"event": event, "studClass": data['studClass'], "theme": data['theme'], "target": data['target'], "result": data['result']}
            #Если найдёт событие, привязаное к текущему событию, обновит его. Если нет - создаст новое.
            addData, created = OpenClass.objects.update_or_create(event=event, defaults=values)
        case "organization":
            #values - данные, которые обновятся, если найдётся дочернее событие от event
            values = {"event": event, "form": data['form'], "document": data['document'], "place": data['place']}
            #Если найдёт событие, привязаное к текущему событию, обновит его. Если нет - создаст новое.
            addData, created = Organization.objects.update_or_create(event=event, defaults=values)
        case "expertise":
            #values - данные, которые обновятся, если найдётся дочернее событие от event
            values = {"event": event, "result": data['result'], "action": data['action'], "level": data['level']}
            #Если найдёт событие, привязаное к текущему событию, обновит его. Если нет - создаст новое.
            addData, created = Expertise.objects.update_or_create(event=event, defaults=values)
        case "course":
            #values - данные, которые обновятся, если найдётся дочернее событие от event
            values = {"event": event, "theme": data['theme'], "form": data['form'], "document": data['document'], "place": data['place'], "organizer": data['organizer'], "length": data['length']}
            #Если найдёт событие, привязаное к текущему событию, обновит его. Если нет - создаст новое.
            addData, created = Course.objects.update_or_create(event=event, defaults=values)
        case "experience":
            #values - данные, которые обновятся, если найдётся дочернее событие от event
            values = {"event": event, "theme": data['theme'], "result": data['result'], "form": data['form'], "document": data['document'], "place": data['place'], "action": data['action'], "level": data['level'], "link": data['link']}
            #Если найдёт событие, привязаное к текущему событию, обновит его. Если нет - создаст новое.
            addData, created = Experience.objects.update_or_create(event=event, defaults=values)
        case "student_work":
            #values - данные, которые обновятся, если найдётся дочернее событие от event
            values = {"event": event, "result": data['result'], "theme": data['theme'], "student": data['student'], "studClass": data['studClass'], "level": data['level'], "document": data['document']}
            #Если найдёт событие, привязаное к текущему событию, обновит его. Если нет - создаст новое.
            addData, created = StudentWork.objects.update_or_create(event=event, defaults=values)
    #Если находит запись с тем же названием, датой и преподавателем, автоматически обновляет её вместо добавления новой записи.

    print()
    return HttpResponse("Ok")

def docData(request):#Собирает все данные для генерации документа :
    print(f"RECIEVED {request.get_host()}: {request.GET}")                 #(Отличается от getData отсутствием необходимости разделять по учителям, взамен разделяя по кафедрам, например.)

    return