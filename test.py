import data as d
import csv
import datetime as dt

d.init_data('localhost', 'attend', 'attend_1234')

# f = open('sample_studentlist.csv', 'r', newline='')
# r = csv.reader(f)
# next(r)
# d.add_studentlist(r, 12, 'a')
# f.close()
# 
# f = open('sample_attend.csv', 'r', newline='')
# r = csv.reader(f)
# next(r)
# d.add_attendence_rec(r, 12, 'a', 2, 'eng', dt.datetime(2022, 1, 29, 8, 13))  # year, month, day, hour, minute

print(d.get_absent_late(12, 'a', dt.datetime(2022, 1, 29), 3))
print(d.get_absent_dates(12, 'a', 2))
print(d.get_late_count(12, 'a', 1))
