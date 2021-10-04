from string import Template

f = open("sample_temp.html", 'r')
s = f.read()
f.close()

t = Template(s)
print(t.substitute(random="Thingies"))
