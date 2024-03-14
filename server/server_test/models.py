from django.db import models

class testTable(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()
#СЮДА ВПИСАТЬ КЛАССЫ ТАБЛИЦ, КОГДА ПРИДУМАЕШЬ КАК ЭТО СДЕЛАТЬ НЕ ПОЗОРНО :)
    
class Teacher(models.Model):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=30)
    qualification = models.CharField(max_length=30)

class Event(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    date = models.DateField()
    name = models.TextField()
    table = models.PositiveSmallIntegerField()

class StudentWork(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    result = models.CharField(max_length=30)
    theme = models.CharField(max_length=30)
    student = models.CharField(max_length=50)
    studClass = models.CharField(max_length=3)
    level = models.CharField(max_length=20)
    document = models.CharField(max_length=20)

class OpenClass(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    studClass = models.CharField(max_length=3)
    theme = models.TextField()
    target = models.TextField()
    result = models.CharField(max_length=15)

class Course(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    theme = models.TextField()
    form = models.CharField(max_length=20)
    document = models.CharField(max_length=20)
    place = models.CharField(max_length=50)
    organizer = models.CharField(max_length=50)
    length = models.IntegerField()

class Experience(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    #308 72
    theme = models.TextField()
    result = models.CharField(max_length=15)
    form = models.CharField(max_length=20)
    document = models.CharField(max_length=20)
    place = models.CharField(max_length=50)
    action = models.CharField(max_length=30)
    level = models.CharField(max_length=20)
    link = models.URLField()

class Expertise(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    result = models.CharField(max_length=15)
    action = models.CharField(max_length=30)
    level = models.CharField(max_length=20)

class Organization(models.Model):
    event = models.ForeignKey(Event, on_delete = models.CASCADE)
    form = models.CharField(max_length=20)
    document = models.CharField(max_length=20)
    place = models.CharField(max_length=50)

class SelfEd(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    begin = models.DateField()
    end = models.DateField()
    theme = models.TextField() 
    method = models.TextField()

class auth(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    password = models.CharField(max_length=30)