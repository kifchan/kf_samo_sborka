from __future__ import print_function
import os
import sys
import time
from tkinter import messagebox  # всплывающее окно
import shutil  # стандартное копированиe
from shutil import copyfile
import subprocess  # вызов робокопи
import json


#
#### Автоустановка пакетов
required_modules = ["pyperclip", "json", "cryptography", "ftplib", "tqdm", "colorama"]

# Проверка наличия и установка каждого модуля
for module in required_modules:
    try:
        globals()[module] = __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])
        globals()[module] = __import__(module)  # Повторный импорт после установки
### Конец автоустановки пакетов

# Импорт библиотек
from cryptography.fernet import Fernet
from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor
#from tqdm import tqdm

# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
'''
Скрипт для отправки собранного сада на стор, с переименование папок по кол-ву файлов. 
Из таблицы копируем адрес в буфер, жмём хоткей для запуска скрипта
Если стор не доступен, собирать будет локально в папку !!!Готовые
Для работы скрипта, в рабочей папке должна быть папка с сетевым именем компа, например kf-05
'''

# import colored
### pip install colored --upgrade - цвета

# Имя текущего компа в сети
# computername = (os.environ['COMPUTERNAME'])
rabfolder = 'D:\\Рабочая папка'
userfolder = ""  # Путь к нужной папке пользователя который будет найден "D:\Рабочая папка\admin"
rabfolder_arr = []  # Список папок в рабочей папке
rabfile_arr = []  # Ищем текстовый файл с именем сотрудника
txt_file = ""  # Сам текстовый файл


###############


def getnumber():
    y = 0
    for x in rabfolder_arr:
        y += 1
        print(str(y) + ". " + x)
    print("")
    userfolder = input("Введите порядковый номер папки из списка выше, она будет использована для сборки садов в "
                       "будущем:")
    if userfolder.isdigit():
        z = len(rabfolder_arr) + 1
        if int(userfolder) > 0:
            if int(userfolder) < int(z):
                userfolder = rabfolder_arr[int(userfolder) - 1]
                print(userfolder)
                return userfolder
            else:
                print("Неверный номер")
                getnumber()
        else:
            print("Неверный номер")
            getnumber()
    else:
        getnumber()


# Начало скрипта
# получить список папок в рабочей папке rabfolder_arr
for file in os.listdir(rabfolder):
    d = os.path.join(rabfolder, file)
    if os.path.isdir(d):
        if "!sborka" not in d:
            if "!!!Готовые" not in d:
                rabfolder_arr.append(os.path.join(rabfolder, file))

# Найти текстовик в рабочей папке
for file in os.listdir(rabfolder):
    if os.path.isfile(os.path.join(rabfolder, file)):
        if ".txt" in file:
            rabfile_arr.append(os.path.join(rabfolder, file))

# Если текстовых файлов больше одного, тогда сделать всякое разное
if len(rabfile_arr) > 0:
    counttxt = 0
    for x in rabfile_arr:
        if os.path.exists(os.path.splitext(x)[0]):
            counttxt += 1
        else:
            index = rabfile_arr.index(x)
            rabfile_arr.pop(index)
    if int(counttxt) > 1:
        print(">> Удалите все текстовые файлы из рабочей папки, они мешают работе скрипта <<")
        print(">> Удалите все текстовые файлы из рабочей папки, они мешают работе скрипта <<")
        input(">> Удалите все текстовые файлы из рабочей папки, они мешают работе скрипта <<")
        exit()
    if int(counttxt) < 1:
        print(">>> Удалите все текстовые файлы из рабочей папки, они мешают работе скрипта <<<")
        print(">>> Удалите все текстовые файлы из рабочей папки, они мешают работе скрипта <<<")
        input(">>> Удалите все текстовые файлы из рабочей папки, они мешают работе скрипта <<<")
        exit()
    if int(counttxt) == 1:
        if len(rabfile_arr) > 1:
            print("Работе скрипта мешают лишние файлы")
            input("Удалите текстовые документы из D:\\Рабочая папка")
            exit()
        if len(rabfile_arr) == 1:
            userfolder = os.path.join(os.path.splitext(rabfile_arr[0])[0])
            txt_file = os.path.join(rabfile_arr[0])
            print("Рабочая папка " + userfolder)

if len(rabfolder_arr) < 1:
    input("Рабочая папка пуста, скрипт закрыввается")
    exit()
if len(rabfolder_arr) == 1:
    userfolder = rabfolder_arr[0]
    print("Рабочая папка " + userfolder)
if len(rabfolder_arr) > 1:
    if userfolder == "":
        if os.path.isfile(txt_file):
            if os.path.exists(os.path.join(rabfolder, os.path.splitext(txt_file)[0])):
                print("Рабочая папка, " + userfolder)
            else:
                userfolder = getnumber()
        else:
            userfolder = getnumber()  # Запуск поиска папки userfolder
            with open(userfolder + ".txt", "w+") as txt_file:
                txt_file.write("Этот файл нужен для работы скрипта kf_samo_sborka")
                txt_file.write("Удали или переименуй его, если хочешь указать другую рабочую папку")
    else:
        print("")

##############
# копирование текста из буфера
folder = pyperclip.paste()
# folder = r"\\NS\kf\2024.09. Сентябрь\2024.09.27\пк тест1"

pyperclip.copy(folder)
# удаление всех пробелов после текста
folder = folder.rstrip()
sadname = os.path.basename(folder)
planNS = None
file_arr1 = []  # PSD в печати
file_arr2 = []  # JPG в обработке (или на сторе)
file_arr3 = []  # JPG в печати
file_arr4 = []  # Список планов в печати
file_arr5 = []  # JPG в собраном плане на сторе, финальная стадия

otvet = ""

sadfolder = userfolder + "\\печать\\" + sadname  # Путь к саду локальный
obrabotkafolder = folder  # Для сверки кол-ва файлов

# Пред НАЧАЛО, проверка наличия папки с именем компа
checkfolder = userfolder + "\\печать\\"
if not os.path.exists(checkfolder):
    print("Неверная структура папок, не хватает папки печать в " + userfolder)
    print(" ")
    print(" ")
    input("Exit")
    exit()

# Если вообще нет папки с садом, то ошибка и стоп
if os.path.isdir(sadfolder) == False:
    print("Не найдена папка с садом на твоем ПК, либо нет ссылки в буфере!")
    print(" ")
    print(" ")
    input("Exit")
    exit()

# Если нет доступа к стору напрямую, отправлять по фтп
if os.path.isdir(folder):
    ftp_send_status = False
    gotovoe_folder = folder + "\\" + sadname  # Путь сохранения на сторе
    if not os.path.exists(gotovoe_folder):
        os.makedirs(gotovoe_folder)
else:
    # Путь сохранения локальный
    # gotovoe_folder = (userfolder + "\\!!!Готовые\\" + sadname)
    # Создать в папке готовое папку с садом если её нет
    # if not os.path.exists(gotovoe_folder):
    #    os.makedirs(gotovoe_folder)
    # print("Нет доступа к стору, сохранение будет произведено в рабочую папку \\!!!Готовые")
    # print(gotovoe_folder)
    ftp_send_status = True

# Если нет доступа к стору, использовать папку обработки для сверки кол-ва файлов
if os.path.isdir(folder):
    obrabotkafolder = folder
    if not os.path.exists(obrabotkafolder):
        print("На сторе не найдена папка с садом!")
        print("Для подсчёта файлов будет использоавана папка из обработки, убедитесь что она есть")
else:
    if os.path.exists(userfolder + "\\обработка\\" + sadname):
        obrabotkafolder = userfolder + "\\обработка\\" + sadname


def sborka():
    # Если джипегов меньше чем псд
    if len(file_arr3) < len(file_arr1):
        if len(file_arr3) > 0:
            print("(сравнивается кол-во PSD и JPG файлов у вас в печати)")
            input("Предупреждение, в " + plan + " джипегов меньше чем ПСД (Для продолжения нажмите Enter)")
    # Если джипегов больше чем псд

    if len(file_arr3) > len(file_arr1):
        if len(file_arr3) > 0:
            print("(сравнивается кол-во PSD и JPG файлов у вас в печати)")
            input("Предупреждение, в " + plan + " джипегов больше чем ПСД (Для продолжения нажмите Enter)")

    #  Считает кол-во файлов в собранной папке на сторе, после слияния
    def finalcountfiles(gotovoe_folder, planNS):
        for r, d, f in os.walk(os.path.join(gotovoe_folder, planNS)):
            for file in f:
                if file.lower().endswith(".jpg"):
                    if "PSD" not in os.path.join(r, file):
                        if "_mask" not in os.path.join(r, file):
                            file_arr5.append(os.path.join(r, file))
        return file_arr5

    def local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus):
        # Переименовывание перед копированием
        if renamestatus:
            try:
                os.rename(sadfolder + "\\" + currentplanname, sadfolder + "\\" + plan + str(len(file_arr1)))
                currentplanname = plan + str(len(file_arr1))
                # print("Source path renamed to destination path successfully.")
            except IsADirectoryError:
                input("Source is a file but destination is a directory.")
            except NotADirectoryError:
                input("Source is a directory but destination is a file.")
            except PermissionError:
                input(
                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                input(
                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                input(
                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                input("Если не получается устранить проблему перезагрузитесь")
                exit()
            except OSError as error:
                input(error)

        if planNS is not None:  # Если Существует planNS
            try:
                if currentplanname != planNS:  # Если на сторе уже есть папка с планом и название НЕ совпадает
                    print("")
                    print("Переносится папка " + currentplanname + " на сторе уже есть собранная папка " + planNS +
                          " выберите действие:")
                    print(
                        "1. Добавить файлы в уже существующую папку " + planNS + " с заменой, а затем переименовать её "
                                                                                 "указав актуальное общее кол-во файлов")
                    print(
                        "2. Оставить папку на сторе без изменений, а ваши файлы переместить в отедельную папку " + currentplanname)
                    print(
                        "3. Добавить файлы в уже существующую папку " + planNS + " с заменой (Без переименования папки)")
                    while True:
                        answer = input("Ваш ответ: ").strip().lower()
                        if answer == "1":
                            source_file_path = sadfolder + "\\" + currentplanname
                            dest_file_path = (os.path.join(gotovoe_folder, planNS))
                            if (os.path.exists(dest_file_path)) == False:
                                os.mkdir(os.path.join(dest_file_path))
                            print(source_file_path)
                            subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            if os.path.exists(source_file_path + "\\JPG"):
                                if not (os.path.exists(dest_file_path + "\\JPG")):
                                    os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                                source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                                dest_file_path = gotovoe_folder + "\\" + currentplanname + "\\JPG"
                                subprocess.call(
                                    ["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            fcountns = str(len(finalcountfiles(gotovoe_folder, planNS)))
                            print(fcountns)
                            try:
                                os.rename(dest_file_path, gotovoe_folder + "\\" + plan + fcountns)
                                # print("Source path renamed to destination path successfully.")
                            except IsADirectoryError:
                                input("Source is a file but destination is a directory.")
                            except NotADirectoryError:
                                input("Source is a directory but destination is a file.")
                            except PermissionError:
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input("Если не получается устранить проблему перезагрузитесь")
                                exit()
                            except OSError as error:
                                input(error)
                            break
                        elif answer == "2":
                            print(f"Вы выбрали: {answer}")
                            print(os.path.basename(os.path.normpath(userfolder)))

                            source_file_path = sadfolder + "\\" + currentplanname
                            userplan = planNS + " " + os.path.basename(os.path.normpath(userfolder))
                            dest_file_path = (os.path.join(gotovoe_folder, userplan))
                            if (os.path.exists(dest_file_path)) == False:
                                os.mkdir(os.path.join(dest_file_path))
                            print(source_file_path)
                            subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            if os.path.exists(source_file_path + "\\JPG"):
                                if not (os.path.exists(dest_file_path + "\\JPG")):
                                    os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                                source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                                dest_file_path = gotovoe_folder + "\\" + userplan + "\\JPG"
                                if (os.path.exists(dest_file_path)) == False:
                                    os.mkdir(os.path.join(dest_file_path))
                                subprocess.call(
                                    ["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            fcountns = str(len(finalcountfiles(gotovoe_folder, userplan)))
                            print(fcountns)
                            try:
                                os.rename(dest_file_path, gotovoe_folder + "\\" + plan + fcountns
                                          + " " + os.path.basename(os.path.normpath(userfolder)))
                                # print("Source path renamed to destination path successfully.")
                            except IsADirectoryError:
                                input("Source is a file but destination is a directory.")
                            except NotADirectoryError:
                                input("Source is a directory but destination is a file.")
                            except PermissionError:
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input("Если не получается устранить проблему перезагрузитесь")
                                exit()
                            except OSError as error:
                                input(error)
                            break
                        if answer == "3":
                            source_file_path = sadfolder + "\\" + currentplanname
                            dest_file_path = (os.path.join(gotovoe_folder, planNS))
                            if (os.path.exists(dest_file_path)) == False:
                                os.mkdir(os.path.join(dest_file_path))
                            print(source_file_path)
                            subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            if os.path.exists(source_file_path + "\\JPG"):
                                if not (os.path.exists(dest_file_path + "\\JPG")):
                                    os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                                source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                                dest_file_path = gotovoe_folder + "\\" + currentplanname + "\\JPG"
                                subprocess.call(
                                    ["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            break
                        else:
                            print("Повторите ввод")

                # Если planNS = currentplan
                else:
                    print("")
                    print("Переносится папка " + currentplanname + " на сторе уже есть собранная папка " + planNS +
                          " выберите действие:")
                    print(
                        "1. Добавить файлы в уже существующую папку " + planNS + " с заменой, а затем переименовать её "
                                                                                 "указав актуальное общее кол-во файлов")
                    print(
                        "2. Оставить папку на сторе без изменений, а ваши файлы переместить в отедельную папку " + currentplanname)
                    print(
                        "3. Добавить файлы в уже существующую папку " + planNS + " с заменой (Без переименования папки)")
                    while True:
                        answer = input("Ваш ответ: ").strip().lower()
                        if answer == "1":
                            source_file_path = sadfolder + "\\" + currentplanname
                            dest_file_path = (os.path.join(gotovoe_folder, planNS))
                            if (os.path.exists(dest_file_path)) == False:
                                os.mkdir(os.path.join(dest_file_path))
                            print(source_file_path)
                            subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            if os.path.exists(source_file_path + "\\JPG"):
                                if not (os.path.exists(dest_file_path + "\\JPG")):
                                    os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                                source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                                dest_file_path = gotovoe_folder + "\\" + currentplanname + "\\JPG"
                                subprocess.call(
                                    ["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            fcountns = str(len(finalcountfiles(gotovoe_folder, planNS)))
                            print(fcountns)
                            try:
                                os.rename(dest_file_path, gotovoe_folder + "\\" + plan + fcountns)
                                # print("Source path renamed to destination path successfully.")
                            except IsADirectoryError:
                                input("Source is a file but destination is a directory.")
                            except NotADirectoryError:
                                input("Source is a directory but destination is a file.")
                            except PermissionError:
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input("Если не получается устранить проблему перезагрузитесь")
                                exit()
                            except OSError as error:
                                input(error)
                            break
                        elif answer == "2":
                            print(f"Вы выбрали: {answer}")
                            print(os.path.basename(os.path.normpath(userfolder)))

                            source_file_path = sadfolder + "\\" + currentplanname
                            userplan = planNS + " " + os.path.basename(os.path.normpath(userfolder))
                            dest_file_path = (os.path.join(gotovoe_folder, userplan))
                            if (os.path.exists(dest_file_path)) == False:
                                os.mkdir(os.path.join(dest_file_path))
                            print(source_file_path)
                            subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            if os.path.exists(source_file_path + "\\JPG"):
                                if not (os.path.exists(dest_file_path + "\\JPG")):
                                    os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                                source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                                dest_file_path = gotovoe_folder + "\\" + userplan + "\\JPG"
                                if (os.path.exists(dest_file_path)) == False:
                                    os.mkdir(os.path.join(dest_file_path))
                                subprocess.call(
                                    ["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            fcountns = str(len(finalcountfiles(gotovoe_folder, userplan)))
                            print(fcountns)
                            try:
                                os.rename(dest_file_path, gotovoe_folder + "\\" + plan + fcountns
                                          + " " + os.path.basename(os.path.normpath(userfolder)))
                                # print("Source path renamed to destination path successfully.")
                            except IsADirectoryError:
                                input("Source is a file but destination is a directory.")
                            except NotADirectoryError:
                                input("Source is a directory but destination is a file.")
                            except PermissionError:
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input(
                                    "Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                                input("Если не получается устранить проблему перезагрузитесь")
                                exit()
                            except OSError as error:
                                input(error)
                            break
                        if answer == "3":
                            source_file_path = sadfolder + "\\" + currentplanname
                            dest_file_path = (os.path.join(gotovoe_folder, planNS))
                            if (os.path.exists(dest_file_path)) == False:
                                os.mkdir(os.path.join(dest_file_path))
                            print(source_file_path)
                            subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            if os.path.exists(source_file_path + "\\JPG"):
                                if not (os.path.exists(dest_file_path + "\\JPG")):
                                    os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                                source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                                dest_file_path = gotovoe_folder + "\\" + currentplanname + "\\JPG"
                                subprocess.call(
                                    ["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                            break
                        else:
                            print("Повторите ввод")

            except Exception as e:
                print(f"Ошибка поиска на локальной машине: {e}")

        else:  # Если кол-во файлов у ретушера и на сторе совпадает
            if not renamestatus:
                print(currentplanname + " - переименование пропущено")
                source_file_path = sadfolder + "\\" + currentplanname
                dest_file_path = (os.path.join(gotovoe_folder, currentplanname))
                if (os.path.exists(dest_file_path)) == False:
                    os.mkdir(os.path.join(dest_file_path))
                print(source_file_path)
                subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                if os.path.exists(source_file_path + "\\JPG"):
                    if not (os.path.exists(dest_file_path + "\\JPG")):
                        os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                    source_file_path = sadfolder + "\\" + currentplanname + "\\JPG"
                    dest_file_path = gotovoe_folder + "\\" + currentplanname + "\\JPG"
                    subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])

            if renamestatus:  # переименование
                try:
                    os.rename(sadfolder + "\\" + currentplanname, sadfolder + "\\" + plan + str(len(file_arr1)))
                    # print("Source path renamed to destination path successfully.")
                except IsADirectoryError:
                    input("Source is a file but destination is a directory.")
                except NotADirectoryError:
                    input("Source is a directory but destination is a file.")
                except PermissionError:
                    input("Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                    input("Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                    input("Не получается переименовать папку. Возможно открыта она или находящиеся в ней файлы.")
                    input("Если не получается устранить проблему перезагрузитесь")
                    exit()
                except OSError as error:
                    input(error)
                print(plan + str(len(file_arr1)) + " - переименован")
                source_file_path = sadfolder + "\\" + plan + str(len(file_arr1))
                dest_file_path = (os.path.join(gotovoe_folder, plan + str(len(file_arr1))))
                if (os.path.exists(dest_file_path)) == False:
                    os.mkdir(os.path.join(dest_file_path))
                print(source_file_path)
                subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])
                if os.path.exists(source_file_path + "\\JPG"):
                    if not (os.path.exists(dest_file_path + "\\JPG")):
                        os.mkdir(os.path.join(dest_file_path + "\\JPG"))
                    source_file_path = sadfolder + "\\" + plan + str(len(file_arr1)) + "\\JPG"
                    dest_file_path = (os.path.join(gotovoe_folder, plan + str(len(file_arr1)) + "\\JPG"))
                    subprocess.call(["robocopy", source_file_path, dest_file_path, "*.jpeg", "*.jpg", "/MOVE", "/IS"])

    # если ПСД файлов меньше чем файлов в обработке
    if len(file_arr1) < len(file_arr2):
        result = len(file_arr2) - len(file_arr1)
        print(" ")
        print(plan + " - в этом плане не хватает файлов: " + str(result))
        print("(сравнивается кол-во PSD у вас в печати и кол-во сырых файлов на NS)")
        print(" ")
        if currentplanname != plan + str(len(file_arr1)):
            while True:
                otvet = input(
                    "Переименовать " + currentplanname + " в " + plan + str(len(file_arr1)) + " перед копированием? "
                                                                                              "+ да, - нет ")
                if otvet == "+":
                    renamestatus = True
                    local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)
                    break
                elif otvet == "-":
                    renamestatus = False
                    local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)
                    break
                else:
                    print(plan + str(len(file_arr1)))
                    print("Повторите ввод")
        else:
            renamestatus = False
            local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)

    # Если кол-во файлов больше чем нужно, то спросить и копировать куда следует
    if len(file_arr1) > len(file_arr2) > 0:
        result = len(file_arr1) - len(file_arr2)
        print(" ")
        print(plan + " - в этом плане файлов больше чем ожидалось на: +" + str(result))
        print("(сравнивается кол-во PSD у вас в печати и кол-во сырых файлов на NS)")
        print(" ")
        if currentplanname != plan + str(len(file_arr1)):
            while True:
                otvet = input("Переименовать " + currentplanname + " в " + plan + str(len(file_arr1)) + " перед копированием? "
                              "+ да, - нет ")
                if otvet == "+":
                    renamestatus = True
                    local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)
                    break
                elif otvet == "-":
                    renamestatus = False
                    local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)
                    break
                else:
                    print(plan + str(len(file_arr1)))
                    print("Повторите ввод")
        else:
            renamestatus = False
            local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)

    # Если кол-во файлов верное, просто копировать их на стор
    if len(file_arr1) == len(file_arr2) > 0:
        print(plan)
        print(" ")
        if currentplanname != plan + str(len(file_arr1)):
            while True:
                otvet = input("Переименовать " + currentplanname + " в " + plan + str(len(file_arr1)) + " перед копированием? "
                              "+ да, - нет ")
                if otvet == "+":
                    renamestatus = True
                    local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)
                    break
                elif otvet == "-":
                    renamestatus = False
                    local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)
                    break
                else:
                    print(plan + str(len(file_arr1)))
                    print("Повторите ввод")
        else:
            renamestatus = False
            local_save_to_ns(sadfolder, gotovoe_folder, plan, file_arr1, currentplanname, renamestatus)

# НАЧАЛО. Поиск папок с планами в печати
for r, d, f in os.walk(sadfolder):
    for folderz in d:
        if "_" in folderz:
            folderz = folderz.split("_")[:-1]
            plan = ""
            for x in folderz:
                plan += x + "_"
            file_arr1 = []
            for r, d, f in os.walk(sadfolder):
                for dir in d:
                    if plan in dir:
                        currentplanname = dir
                        for r, d, f in os.walk(sadfolder + "\\" + dir + "\\PSD"):

                            for file in f:
                                if file.lower().endswith(".psd"):
                                    file_path = os.path.join(r, file)
                                    if file_path not in file_arr1:
                                        file_arr1.append(os.path.join(r, file))
                file_arr2 = []
                for r, d, f in os.walk(obrabotkafolder):
                    for dir in d:
                        if plan in dir:
                            for r, d, f in os.walk(obrabotkafolder + "\\" + dir):
                                for file in f:
                                    if file.lower().endswith(".jpg"):
                                        file_path = os.path.join(r, file)
                                        if os.path.join(r, file) not in file_arr2:  # Проверяем, есть ли путь в списке
                                            file_arr2.append(file_path)
                # Считаем джипеги в печати
                file_arr3 = []
                for r, d, f in os.walk(sadfolder):
                    for dir in d:
                        if plan in dir:
                            for r, d, f in os.walk(sadfolder + "\\" + dir):
                                for file in f:
                                    if file.lower().endswith(".jpg"):
                                        if "PSD" not in os.path.join(r, file):
                                            if "_mask" not in os.path.join(r, file):
                                                file_path = os.path.join(r, file)
                                                if file_path not in file_arr3:
                                                    file_arr3.append(os.path.join(r, file))

            # Проверяем есть ли уже на NS папка с таким планом
            if ftp_send_status:
                try:
                    with ftplib.FTP(ftp_host) as ftp:
                        ftp.login(ftp_user, ftp_pass)
                        # Проверяем наличие папки с планом на FTP
                        if check_ftp_folder(ftp, os.path.join(folder, sadname)):
                            print("Папка найдена на FTP.")
                        else:
                            print("Папка не найдена на FTP.")
                except ftplib.all_errors as e:
                    print(f"Ошибка соединения с FTP: {e}")
            else:
                try:
                    for r, d, f in os.walk(os.path.join(folder, sadname)):
                        for folderx in d:
                            folder_prefix = folderx.rsplit('_', 1)[0] + "_"
                            if plan == folder_prefix:
                                planNS = folderx
                                print(f"Папка найдена на сторе: {planNS}")
                                break
                        else:
                            planNS = None
                except Exception as e:
                    print(f"Ошибка поиска на на сторе: {e}")

            sborka()