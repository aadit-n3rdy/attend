import csv

def __gen_file_name(_class, sec):
    return "data/student_list/{}_{}/students.csv".format(_class, sec)

def get_student_list(_class, sec):
    fname = __gen_file_name(_class, sec)
    try:
        f = open(fname, "r", newline='')
    except FileNotFoundError:
        print("ERROR: file {} not found".format(fname))
        return -1
    l = f.read().splitlines()
    f.close()
    return l

def get_absentees(_class, sec, present):
    student_list = get_student_list(_class, sec)
    if student_list == -1:
        return -1
    absentees = []
    for s in student_list:
        if s not in present:
            absentees.append(s)
    return absentees
