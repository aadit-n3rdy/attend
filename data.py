import csv
import datetime
import os

try:
    import mysql.connector as sql
except ModuleNotFoundError:
    import mariadb as mysql


''' 
Database structure:
    attend:
        <class_name>_studentlist
        <class_name>_attendence

<class_name>_student_list:
rno int primary key
name varchar(255) not null

<class_name>_attendence:
date DATE,
period int,
sub char(3),
absent bit(4),
late bit(4)
primary key(date, period)

Subject codes:
    mat: maths/entre
    phy: phyics
    cem: chem
    eng: english
    ele: elective (bio/cs)
    sci: science
    sec: second language
    thi: third language
    soc: social studies

eg:
    data/student_list/12_a.csv
    data/register/29-01-2022/12_a/2_cse.csv

Record format:
    [Name, time of joining, time spent]

'''

connection = None
cursor = None

def init_data(host, user, pwd):
    ''' Inits the connection and the cursor '''
    global connection, cursor
    try:
        connection = mysql.connect(host = host, user = user, passwd = pwd, database = "attend")
        cursor = connection.cursor()
    except Exception as e:
        print(e)

def __list_to_bitset(l):
    ''' Converts the list of absent or late
    into a bitset of absent or late '''
    i = 0
    for rno in l:
        i += 1<<(rno-1)
    return i

def __bitset_to_list(b):
    ''' Converts bitset of absent or late
    to list of absent or late '''
    l = []
    for i in range(0, 33):
        if b & 1<<i != 0:
            l.append(i+1)
    return l

def __gen_student_list_tname(_class, sec):
    ''' Table name for studentlist'''
    return "{}_{}_studentlist".format(_class, sec)

def __gen_attendence_tname(_class, sec):
    ''' Table name for attendence'''
    return "{}_{}_attendence".format(_class, sec)

def get_student_list(_class, sec):
    cursor.execute("select * from {};".format(__gen_student_list_tname(_class, sec)))
    return list(cursor)

def add_studentlist(csv_file, _class, sec):
    ''' To add a new class to the database '''
    sl_tname = __gen_student_list_tname(_class, sec)
    att_tname = __gen_attendence_tname(_class, sec)
    try:
        cursor.execute('''create table {} 
            (rno int, 
            name varchar(255) not null, 
            primary key(rno));'''.format(sl_tname))
    except mysql.Error as e:
        if e.errno == 1050:
            return "Student list already exists"
        else:
            return "Error creating studentlist table: " + str(e.errno)
    try:
        cursor.execute('''create table {} 
            (date date, 
            period int, 
            sub char(3), 
            absent bit(32), 
            late bit(32), 
            primary key(date, period));'''.format(att_tname))
    except mysql.Error as e:
        if e.errno == 1050:
            return "Attendence table already exists"
    connection.commit()
    cmd = "insert into {} values( {}, '{}');"
    for row in csv_file:
        cursor.execute(cmd.format(sl_tname, int(row[0]), row[1]))
    connection.commit()

def add_attendence_rec(csv_file, _class, sec, period, sub, start):
    ''' To upload the .csv from a meeting '''
    student_list = get_student_list(_class, sec)
    absent_rnos = []
    late_rnos = []
    csv_data = list(csv_file)

    for row in csv_data:
        row[1] = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if row[1].hour < 6:
            row[1] = row[1] + datetime.timedelta(hours=6)
        t = row[2].split(':')
        row[2] = 60*int(t[0]) + int(t[1]) + int(t[2])/60

    cd_flat = [i for row in csv_data for i in row]
    cd_names = cd_flat[::3]

    for i in student_list:
        if i[1] not in cd_names:
            absent_rnos.append(i[0])
        else:
            index = cd_names.index(i[1])
            if csv_data[index][2] < 5:
                absent_rnos.append(i[0])
            elif (csv_data[index][1] - start).total_seconds() > 300:
                late_rnos.append(i[0])
    absent_bs = __list_to_bitset(absent_rnos)
    late_bs = __list_to_bitset(late_rnos)

    insert_cmd = "insert into {} values('{}', {}, '{}', {}, {});".format(
        __gen_attendence_tname(_class, sec),
        datetime.datetime.strftime(start, '%Y-%m-%d'),
        period,
        sub,
        bin(absent_bs),
        bin(late_bs))

    cursor.execute(insert_cmd)
    connection.commit()

    return absent_rnos, late_rnos

def get_absent_late(_class, sec, date, period):
    ''' Returns tuple of absent list and late list. Each list
    is a list of (rno, name) tuples '''
    tname = __gen_attendence_tname(_class, sec)
    cmd = "select absent, late from {} where date = '{}' and period = {}".format(
            tname,
            datetime.datetime.strftime(date, '%Y-%m-%d'),
            period)
    cursor.execute(cmd)
    if cursor.rowcount == 0:
        return "Invalid details"
    row = next(cursor)
    absent_bs = int.from_bytes(row[0], "big")
    late_bs = int.from_bytes(row[1], "big")
    absent_rnos = __bitset_to_list(absent_bs)
    late_rnos = __bitset_to_list(late_bs)
    absent_list = []
    late_list = []

    cmd = "select * from {} where rno = {};"
    tname = __gen_student_list_tname(_class, sec)
    for i in absent_rnos:
        cursor.execute(cmd.format(tname, i))
        if cursor.rowcount != 0:
            absent_list.append(next(cursor))
    for i in late_rnos:
        cursor.execute(cmd.format(tname, i))
        if cursor.rowcount != 0:
            late_list.append(next(cursor))
    return absent_list, late_list

def get_absent_dates (_class, sec, rno):
    ''' Returns a dictionary of dates when student was absent
    and no. of dates. dictionary keys are dates, values are list of periods
    in that day for which student was absent '''
    tname = __gen_attendence_tname(_class, sec)
    cmd = "select date, period from {} where absent & 1<<{} != 0;".format(tname, rno-1)
    cursor.execute(cmd)
    d = {}
    for i in cursor:
        if i[0] in d.keys():
            d[i[0]].append(i[1])
        else:
            d[i[0]] = [i[1]]
    n = len(d)
    return d, n

def get_late_count (_class, sec, rno):
    ''' Returns no. of periods for which a student was late '''
    tname = __gen_attendence_tname(_class, sec)
    cmd = "select count(*) from {} where late & 1<<{} != 0;".format(tname, rno-1)
    cursor.execute(cmd)
    return next(cursor)[0]

def combine_csv (csv1, csv2, output_csv):
    w.writerow(["Full Name", "First Seen", "Time in Call"])
    for row in csv1:
        output_csv.writerow(row)
    for row in csv2:
        output_csv.writerow(row)

def split_csv (input_csv, sec_a, sec_b, _class):
    studentlist_1 = get_student_list(_class, 'a')
    studentlist_1 = [i[1] for i in studentlist_1]
    studentlist_2 = get_student_list(_class, 'b')
    studentlist_2 = [i[1] for i in studentlist_2]

    for row in input_csv:
        if row[0] in studentlist_1:
            sec_a.writerow(row)
        elif row[0] in studentlist_2:
            sec_b.writerow(row)
