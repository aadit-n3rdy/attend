import csv

def get_student_list(_class, sec):
    fname =  "data/student_list/" + str(_class) + "_" + sec + "/students.csv"
    try:
        f = open(fname, "r", newline='')
    except FileNotFoundError:
        print("ERROR: file {} not found".format(fname))
        return -1
    l = f.read().splitlines()
    f.close()
    return l

        
