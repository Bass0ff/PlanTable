import requests
import sys

from PySide2.QtCore import Qt, QSize, QDate
from PySide2.QtWidgets import *
from PySide2.QtGui import QPalette, QColor

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.shared import Pt, Mm, Cm
from datetime import datetime

tables = {  #Шаблоны для генерации страниц заполнения таблиц
    "t-01": {
        'name': "Проведение открытых уроков, классных часов, предметных недель, других мероприятий",
        'fields': [
            ["Дата", "Date"],
            ["Предмет", "EList", ("Русский Язык", "Математика", "Алгебра", "Геометрия", "Литература", "Физика")],
            ["Класс", "SText"],
            ["Тема", "Text"],
            ["Цель", "Text"],
            ["Отметка", "Check"]
        ],
        'type': 'oc'    #open_class = открытый урок
    },
    "t-02": {
        'name': "Участие в подготовке и проведении лицейских мероприятий",
        'fields': [
            ["Дата", "Date"],
            ["Название", "EList", ("Заседание Кафедры", "Педсовет", "Педагогическое чтение", "Конференция", "Олимпиада", "Конкурс", "Выставка", "Предметная неделя")],
            ["Форма участия", "EList", ("Очная", "Заочная", "Дистанционная")],
            ["Документ", "List", ("Протокол", "Выписка", "План", "Отзыв", "Приказ")]
        ],
        'type': 'se'    #self_education = самообразование
    },
    "t-03": {
        'name': "Запланированные мероприятия",
        'fields': [
            ["Мероприятие", "Text"],
            ["Результат", "Text"],
            ["Место проведения", "Text"],
            ["Дата", "Date"]
        ],
        'type': 'se'    #self_education = самообразование
    },
    "t-04": {
        'name': "Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок",
        'fields': [
            ["Название", "Text"],
            ["Личное участие", "Text"],
            ["Дата", "Date"],
            ["Результат", "Text"]
        ],
        'type': 'et'    #ExperTise = экспертная деятельность
    },
    "t-05": {
        'name': "Экспертная Деятельность",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Вид деятельности", "List", ("судья", "эксперт", "жюри")],
            ["Уровень", "List", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")]
        ],
        'type': 'et'    #ExperTise = экспертная деятельность
    },
    "t-06": {
        'name': "Обучение на курсах повышения квалификации, посещение опорных школ и др.",
        'fields': [
            ["Дата", "Date"],
            ["Тема", "Text"],
            ["Учреждение", "Text"],
            ["Часы", "Number", 0, 500],
            ["Документ", "Text"],
            ["Формат", "EList", ("очный", "дистанционный", "очный, с применением дистанционных технологий")]
        ],
        'type': 'cr'    #CouRse = прохождение курсов и пр.
    },
    "t-07": {
        'name': "Участие в сертифицированные вебинарах, семинарах и др.",
        'fields': [
            ["Дата", "Date"],
            ["Тема", "Text"],
            ["Организатор", "Text"],
            ["Формат", "Text"],
            ["Часы", "Number", 0, 500],
            ["Документ", "Text"]
        ],
        'type': 'cr'    #CouRse = прохождение курсов и пр.
    },
    "t-08": {
        'name': "Участие в конкурсах профессионального мастерства",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Уровень", "List", ("школьный", "муниципальный", "региональный", "всероссийский")],
            ["Формат", "List", ("очная", "заочная", "дистанционная")],
            ["Этап", "List", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")],
            ["Результат", "Text"],
            ["Документ", "Text"],
            ["Ссылка", "Text"]
        ],
        'type': 'ec'    #ExperienCe = предоставление опыта
    },
    "t-09": {
        'name': "Обобщение и представление опыта работы",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Форма участия", "List", ("очная", "заочная", "дистанционная")],
            ["Уровень", "List", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")],
            ["Тема", "Text"],
            ["Вид деятельности", "EList", ("выступление", "публикация", "мастер-класс")],
            ["Публикация", "EList", ("статья", "метод", "разработка")],
            ["Орган", "Text"],
            ["Ссылка", "Text"]
        ],
        'type': 'ec'    #ExperienCe = предоставление опыта
    },
    "t-10": {
        'name': "Участие в диагностике профессиональных дефицитов/предметных компетенций",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Результат", "Text"]
        ],
        'type': 'et'    #ExperTise = экспертная деятельность
    },
    "t-11": {
        'name': "Участие во внешкольных мероприятий",
        'fields': [
            ["Дата", "Date"],
            ["Тип", "EList", ("Школа Современного Педагога", "конференция", "семинар", "консультация", "стажировочная площадка", "урок коллег из другой школы")],
            ["Уровень", "List", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")],
            ["Статус", "List", ("организатор", "участник")],
            ["Место проведения", "Text"],
            ["Тема", "Text"],
            ["Организатор", "Text"]
        ],
        'type': 'cr'    #CouRse = прохождение курсов и пр.
    },
    "t-12": {
        'name': "Посещение уроков, кл.часов, мероприятий у коллег в школе",
        'fields': [
            ["Дата", "Date"],
            ["Предмет", "EList", ("Русский Язык", "Математика", "Алгебра", "Геометрия", "Литература", "Физика")],
            ["Класс", "SText"],
            ["Тема", "Text"],
            ["Цель", "Text"]
        ],
        'type': 'oc'    #open_class = открытый урок
    },
    "t-13": {
        'name': "Участие обучающихся в конкурсных мероприятиях, входящих в перечень, \n утвержденный приказом Министертсва науки и высшего образования РФ",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Обучающийся", "Text"],
            ["Класс", "SText"],
            ["Этап", "EList", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")],
            ["Результат", "Text"],
            ["Документ", "Text"]
        ],
        'type': 'sw'    #student_work = работа с учениками
    },
    "t-14": {
        'name': "Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др.",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Обучающийся", "Text"],
            ["Класс", "SText"],
            ["Уровень", "EList", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")],
            ["Результат", "Text"],
            ["Документ", "Text"]
        ],
        'type': 'sw'    #student_work = работа с учениками
    },
    "t-15": {
        'name': "Участие обучающихся в соревнованиях профессиональных компетенций",
        'fields': [
            ["Дата", "Date"],
            ["Название", "Text"],
            ["Компетенция", "Text"],
            ["Обучающийся", "Text"],
            ["Класс", "SText"],
            ["Уровень", "EList", ("отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный")],
            ["Результат", "Text"],
            ["Документ", "Text"]
        ],
        'type': 'sw'    #student_work = работа с учениками
    },
    "t-16": {
        'name': "Дополнительные общеразвивающие программы (ДОП) по подготовке обучющихся 9-11 классов к ВсОШ",
        'fields': [
            ["Название", "Text"],
            ["Дата", "Date"],
            ["Обучающийся", "Text"]
        ],
        'type': 'sw'    #student_work = работа с учениками
    },
    "t-17": {
        'name': "Участие в профильных сменах",
        'fields': [
            ["Название", "Text"],
            ["Дата", "Date"],
            ["Обучающийся", "Text"]
        ],
        'type': 'sw'    #student_work = работа с учениками
    }
}

docTables = [ #Шаблоны для заполнения документов
    [   "Учебно-методическая и организационно-методическая работа",
        ["Проведение открытых уроков, классных часов, предметных недель, других мероприятий", ["Дата", "Предмет", "Класс", "тема", "Цель, для какой цели проводится", "Отметка о выполнении"], [0, 6, 5, 4, 3, 2]],
        ["Участие в подготовке и проведении лицейских мероприятий", ["Дата", "Название мероприятия", "Форма участия", "Вид сданной документации"], [0, 3, 6, 2]],
    ],
    [   "Научно-методическая и исследовательская (экспериментальная) работа",
        ["Тема самообразования", ["Запланированные мероприятия", "Конкретный результат", "Место проведения", "Дата"], [3, 2, 4, 0]],
        ["Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок", ["Название творческой группы, инновационной/стажировочной площадки", "Личное участие в работе группы, площадки", "Дата", "Результат"], [3, 5, 0, 2]],
        ["Экспертная Деятельность", ["Дата", "Название мероприятия", "Вид экспертной детельности", "Уровень"], [0, 3, 5, 6]],
    ],
    [   "Повышение квалификации",
        ["Обучение на курсах повышения квалификации, посещение опорных школ и др.", ["Дата обучения", "Тема курсовой подготовки", "Базовое учреждение обучения (по удостоверению)", "Количество часов", "Документ об окончании обучения", "Формат обучения"], [0, 4 ,6, 9, 11]],
        ["Участие в сертифицированные вебинарах, семинарах и др.", ["Дата", "Тема мероприятия", "Организатор мероприятия", "Формат обучения", "Количество часов", "Документ"], [0, 4, 10, 5, 9, 2]],
        ["Участие в конкурсах профессионального мастерства", ["Дата", "Название", "Уровень", "Формат", "Этап", "Результат участия", "Документ", "Активная ссылка на размещение материалов в сети интернет"], [0, 3, 8, 5, 6, 2, 11, 12]],
        ["Обобщение и представление опыта работы", ["Дата", "Название мероприятия", "Форма участия", "Уровень", "Тема представления опыта", "Выступление, публикация, мастер-класс", "Вид публикации", "Название органа, издания, исходные данные", "Активная ссылка на размещение материалов в сети интернет"], [0, 3, 5, 8, 4, 7, 11, 2, 12]],
        ["Участие в диагностике профессиональных дефицитов/предметных компетенций", ["Дата", "Название диагностики", "Результат"], [0, 3, 2]],            ["Участие во внешкольных мероприятий", ["Дата", "Тип мероприятия", "Уровень", "Статус", "Место проведения", "Тема мероприятия", "Кто проводил"], [0, 3, 8, 7, 6, 4, 10]],
        ["Посещение уроков, кл.часов, мероприятий у коллег в школе", ["Дата", "Предмет", "Класс", "Тема", "Цель проведения, для какой категории проводится"], [0, 5, 6, 4, 3]],
    ],
    [   "Работа с обучающимися, в том числе и внеучебная",
        ["Участие обучающихся в конкурсных мероприятиях, входящих в перечень, утвержденный приказом Министерcтва науки и высшего образования РФ", ["Дата", "Наименование мероприятия", "ФИ обучающегося, класс", "Этап олимпиады", "Результат уастия, подтверждающий документ"], [0, 3, 8, 6, 2]],
        ["Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др.", ["Дата", "Наименование мероприятия", "ФИ обучающегося или группа учеников, класс", "Уровень", "Результат участия, подтверждающий документ"], [0, 3, 8, 6, 2]],
        ["Участие обучающихся в соревнованиях профессиональных компетенций", ["Дата", "Наименование соревнований", "Название компетенции", "ФИ обучающегося или группа учеников, класс", "Уровень", "Результат участия, подтверждающий документ"], [0, 3, 4, 8, 6, 2]],
        ["Участие обучающихся в программах образовательного фонда «Талант и успех» (образовательные центры «Сириус» и «Персей»)", ["Название программы", "Сроки прохождения", "ФИ обучающегося", "Название смены", "Сроки", "ФИ обучающегося (участника смены)"], [3, 0, 8, 12, 9, 17]]
    ]
]

def make_rows_bold(*rows):
    for row in rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class RowForm(QDialog):
    def __init__(self, root, data:list = []):    #Делаем ссылку на родителя
        self.root = root
        self.data = data
        # print(data)
        super().__init__()
        self.setWindowTitle(f'Форма "{tables[root.name]["name"]}"')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        pattern = tables[root.name]["fields"]
        self.layout = QVBoxLayout()
        for i in range(len(pattern)):
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            row.addWidget(QLabel(pattern[i][0]), stretch=1)
            field = 0
            match pattern[i][1]:
                case "Text":
                    field = QTextEdit()
                    field.setMaximumWidth(640)
                    field.setMinimumHeight(30)
                    field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    if len(data) > 0:
                        field.setText(data[i])
                    # test.append(field)
                case "SText":
                    field = QLineEdit()
                    field.setMaximumWidth(50)
                    field.setMinimumHeight(30)
                    field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    if len(data) > 0:
                        field.setText(data[i])
                    # test.append(field)
                case "Number":
                    field = QSpinBox()
                    field.setMinimum(pattern[i][2])
                    field.setMaximum(pattern[i][3])
                    field.setMaximumWidth(50)
                    field.setMinimumHeight(30)
                    field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    if len(data) > 0:
                        field.setValue(data[i])
                    # test.append(field)
                case "Date":
                    field = QDateEdit()
                    field.setDate(QDate.currentDate())
                    field.setMinimumHeight(30)
                    field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    if len(data) > 0:
                        field_data = data[i].split(".")
                        field.setDate(QDate(int(field_data[2]),int(field_data[1]),int(field_data[0])))
                    # test.append(field)
                case "List":
                    field = QComboBox()
                    field.addItems(pattern[i][2])
                    field.setMinimumHeight(30)
                    field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    if len(data) > 0:
                        index = field.findText(data[i])
                        field.setCurrentIndex(index)    
                    # test.append(field)
                case "EList":
                    field = QComboBox()
                    field.setEditable(True)
                    field.addItems(pattern[i][2])
                    if len(data) > 0:
                        index = field.findText(data[i])
                        if index == -1:
                            field.addItem(data[i])
                        index = field.findText(data[i])
                        field.setCurrentIndex(index)
                    # test.append(field)
                case "Check":
                    field = QCheckBox()
                    field.setFixedHeight(30)
                    field.setMinimumHeight(30)
                    field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    if len(data) > 0:
                        if data[i] == "True":
                            field.setChecked(True)
                    # test.append(field)
            
            row.addWidget(field, stretch=4)
            self.layout.addLayout(row)
        self.layout.addWidget(QHLine())
        menu = QHBoxLayout()
        save = QPushButton("ОК")
        save.clicked.connect(self.save)
        abort = QPushButton("Отмена")
        abort.clicked.connect(self.abort)
        delete = QPushButton("Удалить")
        delete.clicked.connect(self.delete)
        menu.addWidget(save)
        menu.addWidget(abort)
        menu.addWidget(delete)
        self.layout.addLayout(menu)
        self.setLayout(self.layout)

    def data_format(self, line):
        a = type(line)
        if a == QDateEdit:
            return str(line.date().day()) + "." + str(line.date().month()) + "." + str(line.date().year())
            # return str(line.date().year()) + "-" + str(line.date().month()) + "-" + str(line.date().day())
        elif a == QLineEdit:
            return line.text()
        elif a == QTextEdit:
            return line.toPlainText()
        elif a == QComboBox:
            return line.currentText()
        elif a == QCheckBox:
            return str(line.isChecked())

    def save(self):
        rowData = []
        for i in range(self.layout.count()-2):  #Проходимся по всем полям формы. Минус два из-за меню снизу.
            val = self.data_format(self.layout.itemAt(i).layout().itemAt(1).widget())
            name = self.layout.itemAt(i).layout().itemAt(0).widget().text()
            # print(val, name)
            if self.root.flag == "NEW":
                rowData.append(val)
            else:
                self.data[i] = val
            if (name == "Тип" or name == "Название" or name == "Мероприятие" or name == "Дата" or name == "Предмет"):
                valab = QLabel(val)
                valab.setStyleSheet('border: 1px solid black;')
                if (name == "Дата"):
                    if self.root.flag == "EDIT":
                        self.root.curRow.itemAt(0).widget().setText(val)
                    else:
                        self.root.curRow.insertWidget(0, valab, stretch=1)
                else:
                    if self.root.flag == "EDIT":
                        self.root.curRow.itemAt(1).widget().setText(val)
                    else:
                        self.root.curRow.insertWidget(1, valab, stretch=4)
        if self.root.flag == "NEW":
            self.root.data.append(rowData)
        # print()
        self.root.flag = "OK"
        print(rowData)
        self.close()

    def abort(self):
        self.root.flag = "ABORT"
        self.close()
    
    def delete(self):
        self.root.flag = "DEL"
        self.close()

class Table(QWidget):
    def __init__(self, win, table_name: str):
        self.name = table_name      #Сохраняет название для данных из словаря
        self.win = win              #Ссылка на родительское окно
        self.data = []              #Словарь со строками данных в таблице
        self.draw()                 #Отрисовка интерфейса
        

    def draw(self):
        self.widget = QWidget()          #Основной виджет страницы
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        
        Box_Left = QVBoxLayout()
        Box_Left.setAlignment(Qt.AlignTop)
        Box_Right = QVBoxLayout()
        Box_Right.setAlignment(Qt.AlignTop)

        left_widget = Color('#80B9C7')
        left_widget.setMaximumWidth(self.win.width()/7*3)
        left_widget.setMinimumHeight(self.win.height())
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_widget.setLayout(Box_Left)

        right_widget = Color('white')
        right_widget.setMinimumWidth(self.win.width()/5*3)
        right_widget.setMinimumHeight(self.win.height())
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_widget.setLayout(Box_Right)
        
        btn_menu = QPushButton('Учебно-методическая и \nорганизационно-методическая работа ')
        btn_menu.clicked.connect(lambda: self.win.goTo(self.win.page_plan_p1))
        Box_Left.addWidget(btn_menu)

        btn_menu = QPushButton('Научно-методическая \nи исследовательская работа')
        btn_menu.clicked.connect(lambda: self.win.goTo(self.win.page_plan_p2))
        Box_Left.addWidget(btn_menu)

        btn_menu = QPushButton('Повышение квалификации')
        btn_menu.clicked.connect(lambda: self.win.goTo(self.win.page_plan_p3))
        Box_Left.addWidget(btn_menu)

        btn_menu = QPushButton('Работа с обучающимися, \nв том числе и внеучебная')
        btn_menu.clicked.connect(lambda: self.win.goTo(self.win.page_plan_p4))
        Box_Left.addWidget(btn_menu)

        btn_menu = QPushButton('К созданию документа')
        btn_menu.clicked.connect(lambda: self.win.button_pushed)
        Box_Left.addWidget(btn_menu)

        if self.name == "t-03":
            texts = QFormLayout()
            self.theme = QLineEdit()
            self.dateOne = QDateEdit()
            self.dateTwo = QDateEdit()
            self.method = QLineEdit()
            texts.addRow("Тема Самообразования", self.theme)
            texts.addRow("Сроки работы над темой (год, этап)", self.dateOne)
            texts.addRow("Сроки работы над темой (год, этап)", self.dateTwo)
            texts.addRow("Образовательная технология/Метод обучения", self.method)
            texts.setAlignment(Qt.AlignBottom)
            Box_Right.addLayout(texts)

        lbl = QLabel(tables[self.name]["name"])
        font = lbl.font()
        font.setBold(True)
        font.setPointSize(14)
        lbl.setFont(font)
        lbl.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        lbl.setWordWrap(True)
        lbl.setFixedHeight(110)
        Box_Right.addWidget(lbl)

        BoxPrev = QWidget()
        prev = QHBoxLayout(BoxPrev)
        prev.setAlignment(Qt.AlignRight)
        self.btn_prev = QPushButton("<- Предыдущая Таблица")
        self.btn_prev.clicked.connect(lambda: self.win.prev_plan_table(self))
        prev.addWidget(self.btn_prev)
        Box_Right.addWidget(BoxPrev)

        BoxTable = Color('#bababa')             #Фон для серого блока, где таблица лежит.
        table_box = QVBoxLayout(BoxTable)       #Блок для хранения скроллера
        table_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        tableWidget = QWidget()
        tableWidget.setMinimumSize(self.win.width()/5 * 2, self.win.height()/ 4)
        self.rows = QVBoxLayout(tableWidget)         #Создадим внутри абстрактного виджета tableWidget блок для хранения строк. Сохраним его как параметр для дальнейшего доступа.
        self.rows.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.rows.setContentsMargins(0, 5, 10, 5)
        self.rows.setSizeConstraint(QLayout.SetMinAndMaxSize)
        newRowBtn = QPushButton("Добавить строку")
        newRowBtn.clicked.connect(self.new_row)
        newRowBtn.setStyleSheet('border: 1px solid black;\
                                background-color: #ffffff')
        newRowBtn.setMinimumHeight(50)
        newRowBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rows.addWidget(newRowBtn)
        # labels = [lab[0] for lab in tables[self.name]['fields']]
        scroller = QScrollArea()                #Виджет для прокрутки содержимого
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)   #Вертикальный скроллер всегда видимый (но не всегда активный)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)#Горизонтальный скроллер не видим никогда.
        scroller.setWidgetResizable(True)                           
        scroller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) #Заставляем скроллер растягиваться на всё доступное место.
        scroller.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroller.setWidget(tableWidget)
        table_box.addWidget(scroller)
        
        # menu = QVBoxLayout()
        # btn_new = QPushButton("+")
        # btn_new.clicked.connect(lambda: self.new_row())
        # font = btn_new.font()
        # font.setPointSize(18)
        # font.setBold(True)
        # btn_new.setFont(font)
        # btn_new.setFixedSize(50, 50)
        # menu.addWidget(btn_new)
        # table_box.addLayout(menu)

        save = QWidget()
        BoxSave = QHBoxLayout(save)
        SaveBtn = QPushButton("СОХРАНИТЬ")
        SaveBtn.setAutoFillBackground(True)
        SaveBtn.setStyleSheet("background-color: #11aa00;")
        palette = SaveBtn.palette()
        palette.setColor(QPalette.Window, QColor('green'))
        SaveBtn.setPalette(palette)
        font = SaveBtn.font()
        font.setPointSize(16)
        font.setBold(True)
        SaveBtn.setFont(font)
        SaveBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        SaveBtn.clicked.connect(self.db_save)
        BoxSave.addWidget(SaveBtn)
        BoxSave.setAlignment(Qt.AlignHCenter)

        Box_Right.addWidget(BoxTable, stretch=3)
        Box_Right.addWidget(save)

        BoxNext = QWidget()
        next = QHBoxLayout(BoxNext)
        next.setAlignment(Qt.AlignRight)
        self.Btn_next = QPushButton("Следующая Таблица ->")
        self.Btn_next.clicked.connect(lambda: self.win.next_plan_table(self))
        next.addWidget(self.Btn_next)
        Box_Right.addWidget(BoxNext)
        
        layout.addWidget(left_widget, stretch=2)
        layout.addWidget(right_widget, stretch=3)       
        self.widget.setLayout(layout)
            
    def db_save(self):
        print("СОХРАНЯЕМ СЛЕДУЮЩИЕ ДАННЫЕ:")
        for i in range(len(self.data)):
            print(f"{i}: {self.data[i]}")
        print("Дело сделано!")

    def new_row(self, data=[]):
        self.flag = "NEW"
        if not data:
            data = []
        newRow = QPushButton()
        newRow.setStyleSheet('border: 1px solid black;\
                                background-color: #ffffff')
        newRow.setMinimumHeight(50)
        newRow.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        newRow.clicked.connect(lambda: self.edit_row(self.rows.indexOf(newRow)))
        self.curRow = QHBoxLayout(newRow)

        self.f = RowForm(self, data)
        self.f.exec()

        if self.flag == "OK":
            self.rows.insertWidget(self.rows.count()-1, newRow)

    def edit_row(self, index):
        self.flag = "EDIT"
        self.curIndex = index
        print(index, end=": ")
        print(self.data[index])
        self.curRow = self.rows.itemAt(index).widget().children()[0]

        self.f = RowForm(self, self.data[index])
        self.f.exec()

        if self.flag == "DEL":
            self.rows.itemAt(index).widget().deleteLater()
        ...

    

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class AuthDialog(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlanTable")
        self.setMinimumSize(QSize(1024, 720))
        
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        self.teach = 0
        # self.w = AuthDialog()
        # self.w.show()
        self.pages = QStackedLayout()   
        self.tables = []                    #создаём стак
        self.draw()

#Авторизация

    def draw(self):
#Главная страница      
        self.page_main = QWidget()                          #делаем виджет для первой страницы
        PL_main = QVBoxLayout()                             #слой для страницы
        btn_plan = QPushButton("Таблицы")                      #кнопка "создать план"
        btn_plan.setMinimumHeight(75)
        btn_plan.clicked.connect(lambda: self.goTo(self.page_plan))
        PL_main.addWidget(btn_plan)
        btn_report = QPushButton("Документ")                   #кнопка "создать отчёт"
        btn_report.clicked.connect(self.docx_test)
        btn_report.setMinimumHeight(75)
        PL_main.addWidget(btn_report)
        PL_main.setAlignment(Qt.AlignVCenter)
        self.page_main.setLayout(PL_main)                   #соединяем слой с виджетом
        self.pages.addWidget(self.page_main)                #кладём виджет в стак

#Меню составления плана
        self.page_plan = QWidget()
        PL_plan = QVBoxLayout()
        PL_plan.addWidget(self.lbl("Разделы документа"))
        btn_plan_01 = QPushButton("Учебно-методическая работа")
        btn_plan_01.setMinimumHeight(75)
        btn_plan_01.clicked.connect(lambda: self.goTo(self.page_plan_p1))
        PL_plan.addWidget(btn_plan_01)
        btn_plan_02 = QPushButton("Научно-методическая работа")
        btn_plan_02.setMinimumHeight(75)
        btn_plan_02.clicked.connect(lambda: self.goTo(self.page_plan_p2))
        PL_plan.addWidget(btn_plan_02)
        btn_plan_03 = QPushButton("Повышение квалификации")
        btn_plan_03.setMinimumHeight(75)
        btn_plan_03.clicked.connect(lambda: self.goTo(self.page_plan_p3))
        PL_plan.addWidget(btn_plan_03)
        btn_plan_04 = QPushButton("Работа с обучающимися")
        btn_plan_04.setMinimumHeight(75)
        btn_plan_04.clicked.connect(lambda: self.goTo(self.page_plan_p4))
        PL_plan.addWidget(btn_plan_04)
        PL_plan.addLayout(self.sml_nav())
        PL_plan.setAlignment(Qt.AlignVCenter)
        self.page_plan.setLayout(PL_plan)
        self.pages.addWidget(self.page_plan)

#План по Учебно-методической работе
        self.page_plan_p1 = QWidget()
        PL_plan_p1 = QVBoxLayout()
        PL_plan_p1.addWidget(self.lbl("Учебно-методическая Работа"))
        btn_table1 = QPushButton("Проведение открытых уроков, классных часов, предметных недель, других мероприятий")
        btn_table1.setMinimumHeight(75)
        btn_table1.clicked.connect(lambda: self.goTo(self.tables[0].widget))
        PL_plan_p1.addWidget(btn_table1)
        btn_table2 = QPushButton("Участие в подготовке и проведении лицейских мероприятий")
        btn_table2.setMinimumHeight(75)
        btn_table2.clicked.connect(lambda: self.goTo(self.tables[1].widget))
        PL_plan_p1.addWidget(btn_table2)
        PL_plan_p1.addLayout(self.nav())
        self.page_plan_p1.setLayout(PL_plan_p1)
        self.pages.addWidget(self.page_plan_p1)

#таблица "Проведение открытых уроков, классных часов, предметных недель, других мероприятий"
        self.tables.append(Table(self, "t-01"))
        self.pages.addWidget(self.tables[-1].widget)
        
#таблица "Участие в подготовке и проведении лицейских мероприятий"
        self.tables.append(Table(self, "t-02"))
        self.pages.addWidget(self.tables[-1].widget)

#План по Научно-методической работе
        self.page_plan_p2 = QWidget()
        PL_plan_p2 = QVBoxLayout()
        PL_plan_p2.addWidget(self.lbl("Научно-методическая Работа"))
        btn_table1 = QPushButton("Запланированные Мероприятия")
        btn_table1.setMinimumHeight(75)
        btn_table1.clicked.connect(lambda: self.goTo(self.tables[2].widget))
        PL_plan_p2.addWidget(btn_table1)
        btn_table2 = QPushButton("Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок")
        btn_table2.setMinimumHeight(75)
        btn_table2.clicked.connect(lambda: self.goTo(self.tables[3].widget))
        PL_plan_p2.addWidget(btn_table2)
        btn_table3 = QPushButton("Экспертная Деятельность")
        btn_table3.setMinimumHeight(75)
        btn_table3.clicked.connect(lambda: self.goTo(self.tables[4].widget))
        PL_plan_p2.addWidget(btn_table3)
        PL_plan_p2.addLayout(self.nav())
        self.page_plan_p2.setLayout(PL_plan_p2)
        self.pages.addWidget(self.page_plan_p2)

#таблицы второго раздела
    #Таблица "Запланированные мероприятия"
        self.tables.append(Table(self, "t-03"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок"
        self.tables.append(Table(self, "t-04"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Экспертная Деятельность"
        self.tables.append(Table(self, "t-05"))
        self.pages.addWidget(self.tables[-1].widget)

#План по Повышению Квалификации
        self.page_plan_p3 = QWidget()
        PL_plan_p3 = QVBoxLayout()
        PL_plan_p3.addWidget(self.lbl("Повышение Квалификации"))
        btn_table1 = QPushButton("Обучение на курсах повышения квалификации, посещение опорных школ и др.")
        btn_table1.setMinimumHeight(75)
        btn_table1.clicked.connect(lambda: self.goTo(self.tables[5].widget))
        PL_plan_p3.addWidget(btn_table1)
        btn_table2 = QPushButton("Участие в сертифицированные вебинарах, семинарах и др.")
        btn_table2.setMinimumHeight(75)
        btn_table2.clicked.connect(lambda: self.goTo(self.tables[6].widget))
        PL_plan_p3.addWidget(btn_table2)
        btn_table3 = QPushButton("Участие в конкурсах профессионального мастерства")
        btn_table3.setMinimumHeight(75)
        btn_table3.clicked.connect(lambda: self.goTo(self.tables[7].widget))
        PL_plan_p3.addWidget(btn_table3)
        btn_table4 = QPushButton("Обобщение и представление опыта работы")
        btn_table4.setMinimumHeight(75)
        btn_table4.clicked.connect(lambda: self.goTo(self.tables[8].widget))
        PL_plan_p3.addWidget(btn_table4)
        btn_table5 = QPushButton("Участие в диагностике профессиональных дефицитов/предметных компетенций")
        btn_table5.setMinimumHeight(75)
        btn_table5.clicked.connect(lambda: self.goTo(self.tables[9].widget))
        PL_plan_p3.addWidget(btn_table5)
        btn_table6 = QPushButton("Участие во внешкольных мероприятий")
        btn_table6.setMinimumHeight(75)
        btn_table6.clicked.connect(lambda: self.goTo(self.tables[10].widget))
        PL_plan_p3.addWidget(btn_table6)
        btn_table7 = QPushButton("Посещение уроков, кл.часов, мероприятий у коллег в школе")
        btn_table7.setMinimumHeight(75)
        btn_table7.clicked.connect(lambda: self.goTo(self.tables[11].widget))
        PL_plan_p3.addWidget(btn_table7)
        PL_plan_p3.addLayout(self.nav())
        self.page_plan_p3.setLayout(PL_plan_p3)
        self.pages.addWidget(self.page_plan_p3)

    #Таблица "Обучение на курсах повышения квалификации, посещение опорных школ и др."
        self.tables.append(Table(self, "t-06"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие в сертифицированные вебинарах, семинарах и др."
        self.tables.append(Table(self, "t-07"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие в конкурсах профессионального мастерства"
        self.tables.append(Table(self, "t-08"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Обобщение и представление опыта работы"
        self.tables.append(Table(self, "t-09"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие в диагностике профессиональных дефицитов/предметных компетенций"
        self.tables.append(Table(self, "t-10"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие во внешкольных мероприятий"
        self.tables.append(Table(self, "t-11"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Посещение уроков, кл.часов, мероприятий у коллег в школе"
        self.tables.append(Table(self, "t-12"))
        self.pages.addWidget(self.tables[-1].widget)

#План по Работе с обучающимися
        self.page_plan_p4 = QWidget()
        PL_plan_p4 = QVBoxLayout()
        PL_plan_p4.addWidget(self.lbl("Работа с обучающимися"))
        btn_table1 = QPushButton("Участие обучающихся в конкурсных мероприятиях, входящих в перечень, \n утвержденный приказом Министертсва науки и высшего образования РФ")
        btn_table1.setMinimumHeight(75)
        btn_table1.clicked.connect(lambda: self.goTo(self.tables[12].widget))
        PL_plan_p4.addWidget(btn_table1)
        btn_table2 = QPushButton("Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др.")
        btn_table2.setMinimumHeight(75)
        btn_table2.clicked.connect(lambda: self.goTo(self.tables[13].widget))
        PL_plan_p4.addWidget(btn_table2)
        btn_table3 = QPushButton("Участие обучающихся в соревнованиях профессиональных компетенций ")
        btn_table3.setMinimumHeight(75)
        btn_table3.clicked.connect(lambda: self.goTo(self.tables[14].widget))
        PL_plan_p4.addWidget(btn_table3)
        btn_table4 = QPushButton("Дополнительные общеразвивающие программы (ДОП) по подготовке обучющихся 9-11 классов к ВсОШ")
        btn_table4.setMinimumHeight(75)
        btn_table4.clicked.connect(lambda: self.goTo(self.tables[15].widget))
        PL_plan_p4.addWidget(btn_table4)
        btn_table5 = QPushButton("Участие в профильных сменах")
        btn_table5.setMinimumHeight(75)
        btn_table5.clicked.connect(lambda: self.goTo(self.tables[16].widget))
        PL_plan_p4.addWidget(btn_table5) 
        PL_plan_p4.addLayout(self.nav())
        self.page_plan_p4.setLayout(PL_plan_p4)
        self.pages.addWidget(self.page_plan_p4)

        #Таблица "Участие обучающихся в конкурсных мероприятиях, входящих в перечень, \n утвержденный приказом Министертсва науки и высшего образования РФ"
        self.tables.append(Table(self, "t-13"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др."
        self.tables.append(Table(self, "t-14"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Участие обучающихся в соревнованиях профессиональных компетенций "
        self.tables.append(Table(self, "t-15"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Дополнительные общеразвивающие программы (ДОП) по подготовке обучющихся 9-11 классов к ВсОШ"
        self.tables.append(Table(self, "t-16"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Участие в профильных сменах"
        self.tables.append(Table(self, "t-17"))
        self.tables[-1].Btn_next.setEnabled(False) #Таблица последняя, поэтому переход на следующую недоступен
        self.pages.addWidget(self.tables[-1].widget)

        widget = QWidget()
        widget.setLayout(self.pages)
        self.setCentralWidget(widget)

    def serverConnect(self):
        response = requests.get(f"http://127.0.0.1:8000/")
        if response.text == "OK":
            print("Подключение к серверу работает. Продолжаем запуск.")
                
    def auth(self):
        pass

    def goTo(self, page):
        self.pages.setCurrentWidget(page)
    
    def next_plan_table(self, curtable):
        widget = self.tables[self.tables.index(curtable)+1].widget
        self.pages.setCurrentWidget(widget)

    def prev_plan_table(self, curtable):
        widget = self.tables[self.tables.index(curtable)-1].widget
        self.pages.setCurrentWidget(widget)

    def button_pushed(self):
        print("Кнопка работает, начальник! Честно-честно!")

    def sml_nav(self):
        nav = QHBoxLayout()
        btn_nav_menu = QPushButton("В меню")
        btn_nav_menu.setMinimumHeight(75)
        btn_nav_menu.clicked.connect(lambda: self.goTo(self.page_main))
        nav.addWidget(btn_nav_menu)
        btn_nav_doc = QPushButton("К созданию документа")
        btn_nav_doc.setMinimumHeight(75)
        btn_nav_doc.clicked.connect(self.button_pushed)
        nav.addWidget(btn_nav_doc)
        return nav

    def nav(self):
        nav = QHBoxLayout()
        btn_01 = QPushButton("В Меню")
        btn_01.clicked.connect(lambda: self.goTo(self.page_main))
        nav.addWidget(btn_01)
        nav.setAlignment(Qt.AlignBottom)
        return nav

    def lbl(self, text):
        lbl = QLabel(text)
        font = lbl.font()
        font.setPointSize(18)
        lbl.setFont(font)
        lbl.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        return lbl
    
    def docx_test(self):
        print("Генерация документа начата...")
        doc = Document()
        self.style = doc.styles["Normal"]
        self.style.font.name = "Times New Roman"
        self.style.font.size = Pt(12)
        doc.sections[0].orientation = WD_ORIENT.LANDSCAPE
        doc.sections[0].page_width = Mm(297)
        doc.sections[0].page_height = Cm(21)
        doc.sections[0].left_margin = Mm(30)
        doc.sections[0].right_margin = Mm(15)
        doc.sections[0].top_margin = Mm(20)
        doc.sections[0].bottom_margin = Mm(20)
        curdate = datetime.now()
        if curdate.month > 9:
            years = (curdate.year, curdate.year+1)
        else:
            years = (curdate.year-1, curdate.year)
        head = doc.add_paragraph()
        head.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hline = head.add_run('Индивидуальный план работы учителя МБОУ "Лицей №1" г.Братска')
        hline.bold = True
        hline.font.size = Pt(14)

        year = doc.add_paragraph()
        year.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        a = year.add_run(str(years[0]))
        a.bold = True
        a.font.size = Pt(14)
        a = year.add_run(" — ")
        a.font.size = Pt(14)
        a = year.add_run(str(years[1]))
        a.bold = True
        a.font.size = Pt(14)
        year.add_run(" учебный год")



        index = -1
        for block in docTables:
            doc.add_paragraph()
            blockhead = doc.add_paragraph(style="List Number")
            a = blockhead.add_run(block[0])
            a.bold = True
            a.italic = True
            a.font.size = Pt(14)
            for table in block[1:]:  #Проход по каждой таблице в блоке
                index += 1
                print(index)
                data = self.tables[index].data
                if index == 15:
                    m = max(len(data), len(self.tables[16].data))
                    for i in range(m):
                        if i < len(data) and i < len(self.tables[16].data):
                            data[i] += self.tables[16].data[i]
                        elif i < len(data) and i >= len(self.tables[16].data):
                            data[i] += ["" for index in range(9)]
                        elif i >= len(data) and i < len(self.tables[16].data):
                            data.insert(i ,["" for index in range(9)] + self.tables[16].data[i])
                
                p = doc.add_paragraph()
                p.add_run(table[0]).bold = True
                tab = doc.add_table(rows = 1, cols = len(table[1])+1)
                tab.style = "Table Grid"
                hedline = tab.rows[0].cells
                hedline[0].text = "№"
                for i in range(1, len(hedline)):
                    hedline[i].text = table[1][i-1]
                make_rows_bold(tab.rows[0])
                cnt = 1
                for line in data:
                    row = tab.add_row().cells
                    row[0].text = str(cnt)
                    cnt += 1
                    for i in range(0, len(table[2])):
                        num = table[2][i]
                        if index == 15 and (num == 0 or num == 9):
                            row[i+1].text = f"{line[num]} - {line[num+1]}"
                        else:
                            row[i+1].text = line[num]
                if index == 15:
                    break
                doc.add_paragraph()
        

        doc.save(f"test.docx")
        print(f'Документ "test.docx" готов!')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = app.font()
    font.setPointSize(12)
    app.setFont(font)

    window = MainWindow()
    window.show()

    app.exec_()