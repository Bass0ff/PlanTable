import sqlite3
import sys
from xml.etree.ElementPath import findtext
from PySide2.QtCore import Qt, QSize, QDate
from PySide2.QtWidgets import *
from PySide2.QtGui import QPalette, QColor
from docx import Document

#

#СПИСОК ИЗМЕНЕНИЙ С КОНЦА ДЕКАБРЯ
#-Из-за непостоянности концепции "плана" решил убрать разделение вовсе, оставив саму таблицу как есть целиком.
#-Увеличил шрифт в приложении
#-Обобщил функции добавления и удаления строк в таблицах, а также считывания строк из БД
#-Встретился с завучем Лицея №1:
#   -Узнал, что списков мероприятий толком нет и не бывает в принципе, так как о большей части всего в таблице 
#       становится известно непосредственно в течение года, а не в его начале.
#   -Убрал несколько, как оказалось, лишних столбцов в таблицах
#   -Получил списки, которые по словам самого завуча можно было знать заранее
#-Добавил к некоторым спискам возможность редактирования и предусмотрел считывание уникальных записей из БД
#-Пришёл к идее хранить структуры таблиц программы в виде словаря
#-Сделал приблизительный вариант бокового меню навигации. Переход осуществляется к разделам, а не к таблицам по отдельности. 
#-Сделал переходы по всем таблицам и реализовал их полную работу

#TODO:

#

#   Добавить авторизацию (?перед открытием программы?)
#   Заголовки для столбцов
#   Доделать визуал для начальных менюшек
#   Нормальный ввод для классов: с буквой от А до В и с числом от 5 до 11
#   Настройку ширины бокового меню ..?
#   !Вынести доп.поля из третьей таблицы - они рушат разметку!
#   **Сделать режим настройки для потенциального изменения структуры таблиц в будущем**

tables = {  #Глобальное описание структур таблиц плана
    "table-01": ["part1",   #start, end, result, name, theme, class, form
                ["Date", (0,1)],
                ["EList", "Русский Язык", "Математика", "Алгебра", "Геометрия", "Литература", "Физика", (6,)],
                ["SText", (5,)],
                ["Text", (4,)],
                ["Text", (3,)],
                ["Check", (2,)]],
    "table-02": ["part1",
                ["Date", (0,1)],
                ["EList", "Заседание Кафедры", "Педсовет", "Педагогическое чтение", "Конференция", "Олимпиада", "Конкурс", "Выставка", "Предметная неделя", (3,)],
                ["EList", "Очная", "Заочная", "Дистанционная", (6,)],
                ["List", "Протокол", "Выписка", "План", "Отзыв", (2,)]],

    "table-03": ["part2",   #start, end, result, name, place, worked_as, level
                ["Text", (3,)],
                ["Text", (2,)],
                ["Text", (4,)],
                ["Date", (0,1)]],
    "table-04": ["part2",
                ["Text", (3,)],
                ["Text", (5,)],
                ["Date", (0, 1)],
                ["Text", (2,)]],
    "table-05": ["part2",
                ["Date", (0,1)],
                ["Text", (3,)],
                ["List", "судья", "эксперт", "жюри", (5,)],
                ["List", "муниципальный", "региональный", "всероссийский", "международный", (6,)]],

    "table-06": ["part3",   #start(0), end1, general.result2, name3, theme4, form5, place6, worked_as7, level8, time9, organizator10, part3.result11, link12
                ["Date", (0,1)],
                ["Text", (4,)],   #
                ["Text", (6,)],   #
                ["Text", (9,)],   #
                ["Text", (11,)],   #
                ["EList", "очный", "дистанционный", "очный, с применением дистанционных технологий", (5,)]],
    "table-07": ["part3",
                ["Date", (0,1)],
                ["Text", (4,)],
                ["Text", (10,)],
                ["Text", (5,)],
                ["Text", (9,)],
                ["Text", (2,)]],
    "table-08": ["part3",   #start(0), end1, general.result2, name3, theme4, form5, place6, worked_as7, level8, time9, organizator10, part3.result11, link12
                ["Date", (0,1)],
                ["Text", (3,)],   #name
                ["List", "школьный", "муниципальный", "региональный", "всероссийский", (8,)], #level
                ["List", "очная", "заочная", "дистанционная", (5,)],  #form
                ["List", "муниципальный", "региональный", "всероссийский", "международный", (6,)],    #place
                ["Text", (2,)],   #result
                ["Text", (11,)],   #part3.result
                ["Text", (12,)]],  #link
    "table-09": ["part3",
                ["Date", (0,1)],
                ["Text", (3,)],   #name
                ["List", "очная", "заочная", "дистанционная", (5,)],  #form
                ["List", "муниципальный", "региональный", "всероссийский", "международный", (8,)],    #level
                ["Text", (4,)],   #theme
                ["EList", "выступление", "публикация", "мастер-класс", (7,)], #worked_as
                ["EList", "статья", "метод", "разработка", (11,)],    #part3.result
                ["Text", (2,)],   #result
                ["Text", (12,)]],  #link
    "table-10": ["part3",   #start(0), end1, general.result2, name3, theme4, form5, place6, worked_as7, level8, time9, organizator10, part3.result11, link12
                ["Date", (0,1)],
                ["Text", (3,)],
                ["Text", (2,)]],
    "table-11": ["part3",
                ["Date", (0,1)],
                ["EList", "Школа Современного Педагога", "конференция", "семинар", "консультация", "стажировочная площадка", "урок коллег из другой школы", (3,)],
                ["List", "муниципальный", "региональный", "всероссийский", "международный", (8,)],
                ["List", "организатор", "участник", (7,)],
                ["Text", (6,)],
                ["Text", (4,)],
                ["Text", (10,)]],
    "table-12": ["part3",
                ["Date", (0,1)],
                ["EList", "Русский Язык", "Математика", "Алгебра", "Геометрия", "Литература", "Физика", (5,)],
                ["Text", (6,)],
                ["Text", (4,)],
                ["Text", (3,)]],

    "table-13": ["part4",   #start, end, general.result, general.name, theme, class, level, part4.result, part4.name
                ["Date", (0,1)],
                ["Text", (3,)],
                ["Text", (8,)],
                ["EList", "отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный", (6,)],
                ["Text", (2,)]],
    "table-14": ["part4",
                ["Date", (0,1)],
                ["Text", (3,)],
                ["Text", (8,)],
                ["EList", "отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный", (6,)],
                ["Text", (2,)]],
    "table-15": ["part4",
                ["Date", (0,1)],
                ["Text", (3,)],
                ["Text", (4,)],
                ["Text", (8,)],
                ["EList", "отборочный", "заключительный", "дистанционный", "школьный", "муниципальный", "районный", "региональный", "всероссийский", "международный", "межмуниципальный", "межрегиональный", (6,)],
                ["Text", (2,)]],
    "table-16": ["part4",
                ["Text", (3,)],
                ["Date", (0,)],
                ["Date", (1,)],
                ["Text", (8,)]],  
    "table-17": ["part4",
                ["Text", (3,)],
                ["Date", (0,)],
                ["Date", (1,)],
                ["Text", (8,)]],
}

docTables = [ #Шаблоны для заполнения документов
    ["Проведение открытых уроков, классных часов, предметных недель, других мероприятий", ["Дата", "Предмет", "Класс", "тема", "Цель, для какой цели проводится", "Отметка о выполнении"], [0, 6, 5, 4, 3, 2]],
    ["Участие в подготовке и проведении лицейских мероприятий", ["Дата", "Название мероприятия", "Форма участия", "Вид сданной документации"], [0, 3, 6, 2]],
    ["Запланированные мероприятия", ["Запланированные мероприятия", "Конкретный результат", "Место проведения", "Дата"], [3, 2, 4, 0]],
    ["Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок", ["Название творческой группы, инновационной/стажировочной площадки", "Личное участие в работе группы, площадки", "Дата", "Результат"], [3, 5, 0, 2]],
    ["Экспертная Деятельность", ["Дата", "Название мероприятия", "Вид экспертной детельности", "Уровень"], [0, 3, 5, 6]],
    ["Обучение на курсах повышения квалификации, посещение опорных школ и др.", ["Дата обучения", "Тема курсовой подготовки", "Базовое учреждение обучения (по удостоверению)", "Количество часов", "Документ об окончании обучения", "Формат обучения"], [0, 4 ,6, 9, 11]],
    ["Участие в сертифицированные вебинарах, семинарах и др.", ["Дата", "Тема мероприятия", "Организатор мероприятия", "Формат обучения", "Количество часов", "Документ"], [0, 4, 10, 5, 9, 2]],
    ["Участие в конкурсах профессионального мастерства", ["Дата", "Название", "Уровень", "Формат", "Этап", "Результат участия", "Документ", "Активная ссылка на размещение материалов в сети интернет"], [0, 3, 8, 5, 6, 2, 11, 12]],
    ["Обобщение и представление опыта работы", ["Дата", "Название мероприятия", "Форма участия", "Уровень", "Тема представления опыта", "Выступление, публикация, мастер-класс", "Вид публикации", "Название органа, издания, исходные данные", "Активная ссылка на размещение материалов в сети интернет"], [0, 3, 5, 8, 4, 7, 11, 2, 12]],
    ["Участие в диагностике профессиональных дефицитов/предметных компетенций", ["Дата", "Название диагностики", "Результат"], [0, 3, 2]],
    ["Участие во внешкольных мероприятий", ["Дата", "Тип мероприятия", "Уровень", "Статус", "Место проведения", "Тема мероприятия", "Кто проводил"], [0, 3, 8, 7, 6, 4, 10]],
    ["Посещение уроков, кл.часов, мероприятий у коллег в школе", ["Дата", "Предмет", "Класс", "Тема", "Цель проведения, для какой категории проводится"], [0, 5, 6, 4, 3]],
    ["Участие обучающихся в конкурсных мероприятиях, входящих в перечень, утвержденный приказом Министерcтва науки и высшего образования РФ", ["Дата", "Наименование мероприятия", "ФИ обучающегося, класс", "Этап олимпиады", "Результат уастия, подтверждающий документ"], [0, 3, 8, 6, 2]],
    ["Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др.", ["Дата", "Наименование мероприятия", "ФИ обучающегося или группа учеников, класс", "Уровень", "Результат участия, подтверждающий документ"], [0, 3, 8, 6, 2]],
    ["Участие обучающихся в соревнованиях профессиональных компетенций", ["Дата", "Наименование соревнований", "Название компетенции", "ФИ обучающегося или группа учеников, класс", "Уровень", "Результат участия, подтверждающий документ"], [0, 3, 4, 8, 6, 2]],
    ["Участие обучающихся в программах образовательного фонда «Талант и успех» (образовательные центры «Сириус» и «Персей»)", ["Название программы", "Сроки прохождения", "ФИ обучающегося", "Название смены", "Сроки", "ФИ обучающегося (участника смены)"], [3, 0, 8, 12, 9, 17]]
]

def make_rows_bold(*rows):
    for row in rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True

class Table(QWidget):
    def __init__(self, header: str, win, table_name: str):
        self.name = table_name
        self.widget = QWidget()
        self.win = win
        self.data = []
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

        # Btn_filt = QPushButton("Фильтр")
        # Btn_filt.clicked.connect(win.button_pushed)
        # filter.addWidget(Btn_filt)

        if table_name == "table-03":
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

        lbl = QLabel(header)
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

        BoxFilter = QWidget()
        filter = QHBoxLayout(BoxFilter)
        filter.setAlignment(Qt.AlignLeft)
        Btn_filt = QPushButton("Фильтр")
        Btn_filt.clicked.connect(self.win.button_pushed)
        filter.addWidget(Btn_filt)
        Box_Right.addWidget(BoxFilter)

        BoxTable = Color('#aaaaaa')
        table_box = QVBoxLayout(BoxTable)
        table_box.setAlignment(Qt.AlignTop)
        header = QHBoxLayout()
        header.setAlignment(Qt.AlignTop)
        table_box.addLayout(header)

        cells = QWidget()
        cells.setMinimumSize(self.win.width()/5 * 2, self.win.height()/ 4)
        self.table_lines = []
        self.table_counter = 0
        self.table = QVBoxLayout(cells)
        self.table.setContentsMargins(0, 5, 10, 5)
        self.table.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.table.setAlignment(Qt.AlignTop)

        self.table_num = int(table_name[-2:])

        self.type = tables[table_name][0]  #Название таблицы с деталями для каждого типа таблиц
        res = 0
        match self.type:
            case "part1":
                command = f"SELECT start, end, result, name, theme, class, form FROM general INNER JOIN part1 ON general.id = part1.event_id WHERE general.tab = {self.table_num} AND general.teacher = {self.win.teach}"
                res = self.win.cursor.execute(command)
            case "part2":
                command = f"SELECT start, end, result, name, place, worked_as, level FROM general INNER JOIN part2 ON general.id = part2.event_id WHERE general.tab = {self.table_num} AND general.teacher = {self.win.teach}"
                res = self.win.cursor.execute(command)
            case "part3":
                command = f"SELECT start, end, result, name, theme, form, place, worked_as, level, time, organizator, document, link FROM general INNER JOIN part3 ON general.id = part3.event_id WHERE general.tab = {self.table_num} AND general.teacher = {self.win.teach}"
                res = self.win.cursor.execute(command)
            case "part4":
                command = f"SELECT start, end, result, name, theme, class, level, document, pupil FROM general INNER JOIN part4 ON general.id = part4.event_id WHERE general.tab = {self.table_num} AND general.teacher = {self.win.teach}"
                res = self.win.cursor.execute(command)
        for line in res:
            self.data.append(list(line))
            print(f"HAVING DATA: {line}")
            self.db_row(line, tables[table_name])

        scroller = QScrollArea()
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroller.setWidgetResizable(True)
        scroller.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroller.setWidget(cells)
        table_box.addWidget(scroller)
        
        menu = QVBoxLayout()
        self.btn_new = QPushButton("+")
        self.btn_new.clicked.connect(lambda: self.new_row(tables[table_name]))
        font = self.btn_new.font()
        font.setPointSize(18)
        font.setBold(True)
        self.btn_new.setFont(font)
        self.btn_new.setFixedSize(50, 50)
        menu.addWidget(self.btn_new)
        table_box.addLayout(menu)

        save = QWidget()
        BoxSave = QHBoxLayout(save)
        self.SaveBtn = QPushButton("СОХРАНИТЬ")
        self.SaveBtn.setAutoFillBackground(True)
        self.SaveBtn.setStyleSheet("background-color: #11aa00;")
        palette = self.SaveBtn.palette()
        palette.setColor(QPalette.Window, QColor('green'))
        self.SaveBtn.setPalette(palette)
        font = self.SaveBtn.font()
        font.setPointSize(16)
        font.setBold(True)
        self.SaveBtn.setFont(font)
        self.SaveBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.SaveBtn.clicked.connect(self.db_save)
        BoxSave.addWidget(self.SaveBtn)
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
    
    def delete_line(self, id: int):
        print(f"УДАЛЯЕМ СТРОКУ #{id}")  
        #self.data.pop(id)        
        row = self.table.itemAt(id-1).layout()  #Выбираем саму строку
        for i in range(0, row.count()):         #Удаляем её содержимое
            row.itemAt(i).widget().deleteLater()
        row.deleteLater()                       #Удаляем опустошённую строку
        self.table_lines.pop(id-1)              #Удаляем указатель на строку

    def data_format(self, line):
        a = type(line)
        if a == QDateEdit:
            return str(line.date().year()) + "-" + str(line.date().month()) + "-" + str(line.date().day())
        elif a == QLineEdit:
            return line.text()
        elif a == QComboBox:
            return line.currentText()
        elif a == QCheckBox:
            return str(line.isChecked())
            
    def db_save(self):
        pattern = tables[self.name]
        text_main = "start, end, result, name, teacher, tab"
        match self.type:
            case "part1": 
                pat = ["", "" , "", "", "no", "no", "", ]
                text_add = "theme, class, form, event_id"
            case "part2": 
                pat = ["", "", "no", "no", "no", "no", "no"]
                text_add = "place, worked_as, level, event_id"
            case "part3": 
                pat = ["", "", "no", "no", "no", "no", "no", "no", "no", "no", "no", "no", "no"]
                text_add = "theme, form, place, worked_as, level, time, organizator, document, link, event_id"
            case "part4": 
                pat = ["", "", "no", "", "no", "no", "no", "no", ""]
                text_add = "theme, class, level, document, pupil, event_id"

        lines = []
        for i in range(0, self.table.count()): #Проход по строкам в таблице
            line = []
            res = pat.copy()
            for j in range(0, self.table.itemAt(i).layout().count()): #Проход по столбцам в таблице
                line.append(self.table.itemAt(i).layout().itemAt(j).widget())
            
            for j in range(len(pattern)-1):
                for k in pattern[j+1][-1]:
                    res[k] = self.data_format(line[j])
            print(res, end="\n\n")
            if not(tuple(res) in self.data):
                self.data.append(list(res))
                print("NEW LINE - ", end="")
            lines.append(res)

        self.win.cursor.execute(f"DELETE FROM general WHERE teacher=0 AND tab={self.table_num}")

        for line in lines:
            print(line)
            gen_inp = ""
            for i in range(0, 4):
                gen_inp += f"'{line[i]}'"
                if i != (len(line)-1):
                    gen_inp += ", "
            gen_inp += f"{self.win.teach}, "
            gen_inp += f"{self.table_num}"
            command = f"INSERT INTO general ({text_main}) VALUES ({gen_inp})"
            print(command)
            self.win.cursor.execute(command)

            id_db = self.win.cursor.execute("SELECT id FROM general ORDER BY id DESC LIMIT 1")
            id = int(id_db.fetchone()[0])
            id_str = f", {id}"

            add_inp = ""
            for i in range(4, len(line)):
                add_inp += f"'{line[i]}'"
                if i != (len(line)-1):
                    add_inp += ", "
            add_inp += id_str
            command = f"INSERT INTO {self.type} ({text_add}) VALUES ({add_inp})"
            print(command, end="\n\n")
            self.win.cursor.execute(command)
        self.win.database.commit()    
        print("Дело сделано!")

    def db_row (self, line: tuple, pattern: list):
        row = QHBoxLayout()
        for i in range(1, len(pattern)):
            value = line[pattern[i][-1][0]]
            match pattern[i][0]:
                case "Text":
                    field = QLineEdit()
                    field.setText(value)
                    row.addWidget(field)
                case "SText":
                    field = QLineEdit()
                    field.setMaximumWidth(35)
                    field.setText(value)
                    row.addWidget(field)
                case "Number":
                    field = QSpinBox()
                    field.setMinimum(pattern[i][1])
                    field.setMaximum(pattern[i][2])
                    field.setValue(int(value))
                    row.addWidget(field)
                case "Date":
                    field = QDateEdit()
                    field_data = value.split("-")
                    field.setDate(QDate(int(field_data[0]),int(field_data[1]),int(field_data[2])))
                    row.addWidget(field)
                case "List":
                    field = QComboBox()
                    field.addItems(pattern[i][1:-1])
                    index = field.findText(value)
                    field.setCurrentIndex(index)
                    row.addWidget(field)
                case "EList":
                    field = QComboBox()
                    field.setEditable(True)
                    field.addItems(pattern[i][1:-1])
                    index = field.findText(value)
                    if index == -1:
                        field.addItem(value)
                    index = field.findText(value)
                    field.setCurrentIndex(index)
                    row.addWidget(field)
                case "Check":
                    box = QCheckBox()
                    if value == "True":
                        box.setChecked(True)
                    row.addWidget(box)

        delete = QPushButton("X")
        delete.setObjectName(str(self.table_counter))
        self.table_counter += 1
        self.table_lines.append(delete.objectName())
        font = delete.font()
        font.setBold(True)
        delete.setFont(font)
        delete.setMaximumSize(30,30)
        delete.clicked.connect(lambda: self.delete_line(self.table_lines.index(delete.objectName())+1))
        row.addWidget(delete)
        self.table.addLayout(row)

    def new_row(self, pattern: list):
        row = QHBoxLayout()
        for i in range(1, len(pattern)):
            match pattern[i][0]:
                case "Text":
                    field = QLineEdit()
                    row.addWidget(field)
                case "SText":
                    field = QLineEdit()
                    field.setMaximumWidth(35)
                    row.addWidget(field)
                case "Number":
                    field = QSpinBox()
                    field.setMinimum(pattern[i][1])
                    field.setMaximum(pattern[i][2])
                    row.addWidget(field)
                case "Date":
                    field = QDateEdit()
                    field.setDate(QDate.currentDate())
                    row.addWidget(field)
                case "List":
                    field = QComboBox()
                    field.addItems(pattern[i][1:])
                    row.addWidget(field)
                case "EList":
                    field = QComboBox()
                    field.setEditable(True)
                    field.addItems(pattern[i][1:])
                    row.addWidget(field)
                case "Check":
                    box = QCheckBox()
                    row.addWidget(box)
        delete = QPushButton("X")
        delete.setObjectName(str(self.table_counter))
        self.table_counter += 1
        self.table_lines.append(delete.objectName())
        font = delete.font()
        font.setBold(True)
        delete.setFont(font)
        delete.setMaximumSize(30,30)
        delete.clicked.connect(lambda: self.delete_line(self.table_lines.index(delete.objectName())+1))
        row.addWidget(delete)
        self.table.addLayout(row)

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("PlanTable")
        self.setMinimumSize(QSize(1024, 720))
        self.db_init("database.db")
        self.doc = Document()
        self.teach = 0
        self.pages = QStackedLayout()   
        self.tables = []                    #создаём стак

#Авторизация
        #dlg_auth = QDialog(self)


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
        Header = "Проведение открытых уроков, классных часов, предметных недель, других мероприятий"
        self.tables.append(Table(Header, self, "table-01"))
        self.tables[0].btn_prev.setEnabled(False) #Таблица первая, поэтому переход на предыдущую недоступен
        self.pages.addWidget(self.tables[-1].widget)
        
#таблица "Участие в подготовке и проведении лицейских мероприятий"
        Header = "Участие в подготовке и проведении лицейских мероприятий"
        self.tables.append(Table(Header, self, "table-02"))
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
        Header = "Запланированные мероприятия"
        self.tables.append(Table(Header, self, "table-03"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок"
        Header = "Работа в рамках творческих групп, инновационной/стажировочной деятельности площадок"
        self.tables.append(Table(Header, self, "table-04"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Экспертная Деятельность"
        Header = "Экспертная Деятельность"
        self.tables.append(Table(Header, self, "table-05"))
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
        Header = "Обучение на курсах повышения квалификации, посещение опорных школ и др."
        self.tables.append(Table(Header, self, "table-06"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие в сертифицированные вебинарах, семинарах и др."
        Header = "Участие в сертифицированные вебинарах, семинарах и др."
        self.tables.append(Table(Header, self, "table-07"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие в конкурсах профессионального мастерства"
        Header = "Участие в конкурсах профессионального мастерства"
        self.tables.append(Table(Header, self, "table-08"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Обобщение и представление опыта работы"
        Header = "Обобщение и представление опыта работы"
        self.tables.append(Table(Header, self, "table-09"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие в диагностике профессиональных дефицитов/предметных компетенций"
        Header = "Участие в диагностике профессиональных дефицитов/предметных компетенций"
        self.tables.append(Table(Header, self, "table-10"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Участие во внешкольных мероприятий"
        Header = "Участие во внешкольных мероприятий"
        self.tables.append(Table(Header, self, "table-11"))
        self.pages.addWidget(self.tables[-1].widget)

    #Таблица "Посещение уроков, кл.часов, мероприятий у коллег в школе"
        Header = "Посещение уроков, кл.часов, мероприятий у коллег в школе"
        self.tables.append(Table(Header, self, "table-12"))
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
        Header = "Участие обучающихся в конкурсных мероприятиях, входящих в перечень, \n утвержденный приказом Министертсва науки и высшего образования РФ"
        self.tables.append(Table(Header, self, "table-13"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др."
        Header = "Участие обучающихся в других конкурсных мероприятиях, научно-практических конференциях, ШРД, ФНР и др."
        self.tables.append(Table(Header, self, "table-14"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Участие обучающихся в соревнованиях профессиональных компетенций "
        Header = "Участие обучающихся в соревнованиях профессиональных компетенций "
        self.tables.append(Table(Header, self, "table-15"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Дополнительные общеразвивающие программы (ДОП) по подготовке обучющихся 9-11 классов к ВсОШ"
        Header = "Дополнительные общеразвивающие программы (ДОП) по подготовке обучющихся 9-11 классов к ВсОШ"
        self.tables.append(Table(Header, self, "table-16"))
        self.pages.addWidget(self.tables[-1].widget)

        #Таблица "Участие в профильных сменах"
        Header = "Участие в профильных сменах"
        self.tables.append(Table(Header, self, "table-17"))
        self.tables[-1].Btn_next.setEnabled(False) #Таблица последняя, поэтому переход на следующую недоступен
        self.pages.addWidget(self.tables[-1].widget)

        widget = QWidget()
        widget.setLayout(self.pages)
        self.setCentralWidget(widget)

    def db_init(self, name: str):
        self.database = sqlite3.connect("database.db")
        self.cursor = self.database.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON") #Включить поддержку sqlite внешних ключей
        for table_name in ["personal", "general", "part1", "part2", "part3", "part4"]:
            line = f"SELECT name FROM sqlite_master WHERE name='{table_name}'"
            check_table = self.cursor.execute(line)
            if check_table.fetchone() is None:  #Если таблица вдруг не найдена, её нужно создать
                print(f"Таблица {table_name} не найдена. Создаю таблицу...")
                match table_name:
                    case "personal":
                        self.cursor.execute("CREATE TABLE personal(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                            name TEXT, qualification TEXT, prof TEXT, subj TEXT, theme TEXT, time TEXT, method TEXT)")
                    case "general":
                        self.cursor.execute("CREATE TABLE general(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                            start TEXT, end TEXT, result TEXT, name TEXT, teacher INTEGER, tab INTEGER, \
                                            FOREIGN KEY (teacher) REFERENCES personal(id) ON DELETE CASCADE)")
                    case "part1":
                        self.cursor.execute("CREATE TABLE part1(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                            theme TEXT, class TEXT, form TEXT, event_id INTEGER, \
                                            FOREIGN KEY (event_id) REFERENCES general(id) ON DELETE CASCADE)")
                    case "part2":
                        self.cursor.execute("CREATE TABLE part2(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                            place TEXT, worked_as TEXT, level TEXT, event_id INTEGER, \
                                            FOREIGN KEY (event_id) REFERENCES general(id) ON DELETE CASCADE)")
                    case "part3":
                        self.cursor.execute("CREATE TABLE part3(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                            theme TEXT, form TEXT, place TEXT, worked_as TEXT, level TEXT, time INTEGER, organizator TEXT, document TEXT, \
                                            link TEXT, event_id INTEGER, FOREIGN KEY (event_id) REFERENCES general(id) ON DELETE CASCADE)")
                    case "part4":
                        self.cursor.execute("CREATE TABLE part4(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                            theme TEXT, class TEXT, level TEXT, document TEXT, pupil TEXT, event_id INTEGER, FOREIGN KEY (event_id) \
                                            REFERENCES general(id) ON DELETE CASCADE)")
        check = self.cursor.execute("SELECT * FROM personal WHERE id=0")
        if check.fetchone() is None:
            self.cursor.execute("INSERT INTO personal (id, name, qualification) VALUES (0, 'test', 'dev')")
            self.database.commit()
            print("Тестовый профиль с индексом 0 создан.")
        print("База данных подключена и проверена. Продолжаю запуск...")
                
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
        print("Тестовая генерация документа начата...")
        for tablepage in self.tables:

            index = self.tables.index(tablepage)
            print(index)
            data = tablepage.data
            if index == 15:
                m = max(len(data), len(self.tables[16].data))
                for i in range(m):
                    if i < len(data) and i < len(self.tables[16].data):
                        data[i] += self.tables[16].data[i]
                    elif i < len(data) and i >= len(self.tables[16].data):
                        data[i] += ["" for index in range(9)]
                    elif i >= len(data) and i < len(self.tables[16].data):
                        data.insert(i ,["" for index in range(9)] + self.tables[16].data[i])

            self.doc.add_paragraph()
            p = self.doc.add_paragraph()
            p.add_run(docTables[index][0]).bold = True
            table = self.doc.add_table(rows=1, cols=len(docTables[index][1]))
            hed_line = table.rows[0].cells
            for i in range(len(hed_line)):
                hed_line[i].text = docTables[index][1][i]
                make_rows_bold(table.rows[0])
            for line in data:
                row = table.add_row().cells
                for i in range(len(docTables[index][2])):
                    #print(len(line))
                    num = docTables[index][2][i]
                    if index == 15 and (num == 0 or num == 9):
                        row[i].text = f"{line[num]} - {line[num+1]}"
                    else:
                        row[i].text = line[num] 
            if index == 15:
                break

        

        self.doc.save("test.docx")
        print('Документ "test.docx" готов!')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = app.font()
    font.setPointSize(12)
    app.setFont(font)

    window = MainWindow()
    window.show()

    app.exec_()