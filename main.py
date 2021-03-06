import sys
import sqlite3
import pymorphy2
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, \
    QTableWidgetItem

good = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO',
        'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ']


class Example(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)
        self.result = None
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run2)
        self.pushButton_3.clicked.connect(self.run3)
        con = sqlite3.connect('my.db')
        cur = con.cursor()
        self.show1()

    def run(self):
        m = pymorphy2.MorphAnalyzer()
        a = self.lineEdit.text()
        a1 = m.parse(a)
        a2 = ''
        for i in range(len(a1)):
            a2 += f'''{a}
Начальная форма: {a1[i].normal_form}
{self.trans(self.characteristics(a1[i]))}

'''
            self.save(a, a1[i].normal_form, self.trans(self.characteristics(a1[i])))
        self.textBrowser.setText(a2)
        self.show1()

    def run2(self):
        try:
            con = sqlite3.connect('my.db')
            cur = con.cursor()
            text1 = self.textEdit.toPlainText()
            if text1 == '':
                self.show1()
                self.label_4.setText('')
                return
            text = self.comboBox_2.currentText() + ' = ' + text1
            if self.comboBox_2.currentText() != 'id':
                text = self.comboBox_2.currentText() + ' = ' + f'"{text1}"'
            if self.comboBox.currentText() == 'DELETE':
                valid = QMessageBox.question(
                    self, '', "Действительно удалить элементы с " + text,
                    QMessageBox.Yes, QMessageBox.No)
                if valid == QMessageBox.Yes:
                    if self.comboBox_2.currentText() == 'id':
                        if not cur.execute(f"SELECT * FROM words WHERE {text}").fetchall():
                            raise sqlite3.OperationalError
                        cur.execute(f"DELETE FROM words WHERE part_of_speech = ' {text1}'")
                    elif not cur.execute("SELECT * FROM words WHERE " + text).fetchall():
                        raise sqlite3.OperationalError
                    else:
                        cur.execute("DELETE FROM words WHERE " + f'{text}')
                    con.commit()
                    self.show1()
                    self.label_4.setText('')
            else:
                result = ''
                if self.comboBox_2.currentText() == 'id':
                    if not cur.execute(f"SELECT * FROM words WHERE {text}").fetchall():
                        raise sqlite3.OperationalError
                elif not cur.execute("SELECT * FROM words WHERE " + text).fetchall():
                    raise sqlite3.OperationalError
                else:
                    result = cur.execute("SELECT * FROM words WHERE " + text).fetchall()
                if not result:
                    self.show1()
                    self.label_4.setText('')
                    return
                self.tableWidget.setRowCount(len(result))
                self.tableWidget.setColumnCount(len(result[0]))
                for i, elem in enumerate(result):
                    for j, val in enumerate(elem):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
                self.label_4.setText('')
        except sqlite3.OperationalError:
            self.label_4.setText('Не знаем мы такого ' + self.comboBox_2.currentText() + ' ' + text1)

    def run3(self):
        valid = QMessageBox.question(
            self, '', "Действительно удалить все элементы",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            valid1 = QMessageBox.question(
                self, '', "Вы точно уверены в том, что хотите удалить все элементы",
                QMessageBox.Yes, QMessageBox.No)
            if valid1 == QMessageBox.Yes:
                con = sqlite3.connect('my.db')
                cur = con.cursor()
                cur.execute('DELETE FROM words')
                con.commit()
                self.show1()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
            if rows == []:
                return
            ids = [self.tableWidget.item(i, 0).text() for i in rows]
            valid = QMessageBox.question(
                self, '', "Действительно удалить элементы с id " + ",".join(ids),
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                con = sqlite3.connect('my.db')
                cur = con.cursor()
                cur.execute("DELETE FROM words WHERE id IN (" + ", ".join(
                    '?' * len(ids)) + ")", ids)
                con.commit()
                self.show1()
        elif event.key() == Qt.Key_Enter:
            rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
            ids = [self.tableWidget.item(i, 0).text() for i in rows]
            con = sqlite3.connect('my.db')
            cur = con.cursor()
            res = cur.execute("SELECT * FROM words WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchall()
            a2 = ''
            for i in res:
                a = list(i)[4]
                a3 = ''
                for j in a.split(', '):
                    a3 += f'{j.capitalize()}\n'

                a2 += f'''{list(i)[1]}
Начальная форма: {list(i)[3]}
Часть речи:{list(i)[2]}
{a3} 
'''
            self.textBrowser.setText(a2)

    def trans(self, a):
        b = {'NOUN': 'имя существительное',
             'ADJF': 'имя прилагательное (полное)',
             'ADJS': 'имя прилагательное (краткое)',
             'COMP': 'компаратив',
             'VERB': 'глагол (личная форма)',
             'INFN': 'глагол (инфинитив)',
             'PRTF': 'причастие (полное)',
             'PRTS': 'причастие (краткое)',
             'GRND': 'деепричастие',
             'NUMR': 'числительное',
             'ADVB': 'наречие',
             'NPRO': 'местоимение',
             'PRED': 'предикатив',
             'PREP': 'предлог',
             'CONJ': 'союз',
             'PRCL': 'частица',
             'INTJ': 'междометие',
             'nomn': 'именительный',
             'gent': 'родительный',
             'datv': 'дательный',
             'accs': 'винительный',
             'ablt': 'творительный',
             'loct': 'предложный',
             'voct': 'звательный',
             'gen2': 'второй родительный(частичный)',
             'acc2': 'второй винительный',
             'loc2': 'второй предложный(местный)',
             'sing': 'единственное число',
             'plur': 'множественное число',
             'masc': 'мужской род',
             'femn': 'женский род',
             'neut': 'средний род',
             'LATN': 'Токен состоит из латинских букв',
             'PNCT': 'Пунктуация',
             'NUMB': 'Число',
             'intg': 'целое число',
             'real': 'вещественное число',
             'ROMN': 'Римское число',
             'UNKN': 'Токен не удалось разобрать',
             'anim': 'одушевлённое',
             'inan': 'неодушевлённое',
             'perf': 'совершенный вид',
             'impf': 'несовершенный вид',
             'tran': 'переходный',
             'intr': 'непереходный',
             '1per': '1 лицо',
             '2per': '2 лицо',
             '3per': '3 лицо',
             'pres': 'настоящее время',
             'past': 'прошедшее время',
             'futr': ' будущее время',
             'indc': 'изъявительное наклонение',
             'impr': 'повелительное наклонение',
             'incl': 'говорящий включён в действие',
             'excl': 'говорящий не включён в действие',
             'actv': 'действительный залог',
             'pssv': 'страдательный залог',

             }
        c = []
        for i in a.keys():
            c.append(f'{i}: {b[a[i]]}')
        return '''
'''.join(c)

    def characteristics(self, a1):
        a2 = {}
        p = a1
        b = {'Часть речи': p.tag.POS,
             'Одушевленность': p.tag.animacy,
             'Вид': p.tag.aspect,
             'Падеж': p.tag.case,
             'Род': p.tag.gender,
             'Включенность говорящего в действие': p.tag.involvement,
             'Наклонение': p.tag.mood,
             'Число': p.tag.number,
             'Лицо': p.tag.person,
             'Время': p.tag.tense,
             'Переходность': p.tag.transitivity,
             'Залог': p.tag.voice}

        for i in b.keys():
            if b[i] is not None:
                a2[i] = b[i]
        return a2

    def save(self, a, b, c):
        a2 = (', '.join(c.split('\n')[1:])).lower()
        if (', '.join(c.split('\n')[1:])).lower() == '':
            a2 = '-'
        a1 = (a, b, c.split('\n')[0].split(':')[-1].strip(), a2)
        con = sqlite3.connect('my.db')
        cur = con.cursor()
        a3 = cur.execute(
            '''SELECT * FROM words WHERE (name, normal_form, part_of_speech, characteristics) = (?, ?, ?, ?);''', a1)
        if a3.fetchone() is None:
            cur.execute(
                '''INSERT INTO words(name, normal_form, part_of_speech, characteristics) VALUES(?, ?, ?, ?);''', a1)
        con.commit()

    def show1(self):
        con = sqlite3.connect("my.db")
        cur = con.cursor()
        result = cur.execute("SELECT * FROM words").fetchall()
        self.tableWidget.setRowCount(len(result))
        if result:
            self.tableWidget.setColumnCount(len(result[0]))
        else:
            self.tableWidget.setColumnCount(0)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.setHorizontalHeaderLabels(['id', 'name', 'part_of_speech', 'normal_form', 'characteristics'])
        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
