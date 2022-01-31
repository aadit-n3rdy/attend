import csv
import datetime
import os
import glob


''' 
File hierarchy:
    data/
        student_list/
            <class>_<sec>.csv
        register/
            <date in dd-mm-yy>/
                <class>_<sec>/
                    <period>_<sub>.csv

Subject codes:
    mat: maths
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

def __gen_student_list_fname(_class, sec):
    return "data/student_list/{}_{}.csv".format(_class, sec)

def __gen_period_fname(date, _class, sec, period, sub):
    return "data/register/{}/{}_{}/{}_{}.csv".format(
            date.strftime("%d-%m-%y"),
            _class,
            sec,
            period,
            sub
        )
def __get_period_fname(date, _class, sec, period):
''' Get filename when subject is unknown '''
    fnames = glob.glob(__gen_period_fname(date, _class, sec, period, "*"))
    if len(fnames) != 1:
        print("ERROR: file does not exist, or bad filesystem")
        return -1
    return fnames[0]

def get_student_list(_class, sec):
    fname = __gen_student_list_fname(_class, sec)
    l = []
    with open(fname, "r", newline=''):
        r = csv.reader(f)
        for i in r:
            l.append(i[0])
    return l

def add_attendence_rec(csv_file, date, _class, sec, period, sub):
''' To upload the .csv from a meeting '''

    fname = __gen_period_fname(date, _class, sec, period, sub)
    student_list = get_student_list(_class, sec)
    os.makedirs(os.path.dirname(fname), exist_ok=True)  # Ensure the folder exists
    with open(fname, 'w', newline='') as f:
        w = csv.writer(f)
        for row in csv_file:
            sname = row[0]
            ''' For each student in the class, check if they were
            in the meeting, if so correct the time from the csv file
            (it does not have am or pm) and add to the db, if they did not join
            then make fields empty and add '''
            if sname in student_list:
                t = row[2]
                h = int(t[:2])
                if h < 6:
                    h += 12
                t = "{%02u}{}".format(h, t[2:])
                w.writerow([row[0], t, row[2]])
                student_list.remove(sname)
        for name in student_list:
            w.writerow([name, "", ""])

def get_absentees(date, _class, sec, period, min_time="00:05:00"):
    ''' Student is considered absent if they spend less than
    min_time in meeting'''
    absentees = []
    fname = __get_period_fname(date, _class, sec, period)
    with open(fname, 'r', newline='') as f:
        r = csv.reader(f)
        for row in r:
            if r[1] == '' or r[3] < min_time:
                absentees.append(r[0])
    return absentees

def get_late(date, _class, sec, period, after_time):
    ''' Late if time of joining is after after_time '''
    late = []
    fname = __get_period_fname(date, _class, sec, period)
    with open(fname, 'r', newline='') as f:
        r = csv.reader(f)
        for row in r:
            if r[1] != '' and r[1] > after_time:
                late.append(r[0])
    return late

def get_absent_dates(name, _class, sec, ):
    dates = []
    fnames = glob.glob(__gen_period_fname("??:??:??", _class, sec, "1", "???"))
    ''' Go through all dates for the given class and sectionm if not present
    in first period then assume absent'''
    for fname in fnames:
        with open(fname, 'r', newline='') as f:
            r = csv.reader(f)
            for row in r:
                if r[0] == name and r[1] == '':
                    dates.append(fname[:8])
    return dates
