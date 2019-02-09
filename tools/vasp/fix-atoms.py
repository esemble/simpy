import shutil, sys

n0 = 9
n1 = n0 + 48

f = open("POSCAR", "r")
poscar = f.readlines()
f.close()

# the first line poscar[9]
shutil.copy("POSCAR", "POSCAR.0")
o = open("POSCAR", "w")
for i in range(n0):
    o.write(poscar[i])

for i in range(n0, n1):
    line = poscar[i].replace("T", "F")
    o.write(line)

for i in range(n1, len(poscar)):
    o.write(poscar[i])
o.close()

