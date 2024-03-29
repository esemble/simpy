import os

# lammps unit real
kcal2ev = 4.3363e-2
b2ev = 6.2415e-4

forces_frames = []
energy_frames = []

def parse_block(lines):
    forces = []
    for i in range(9, len(lines)):
        tokens = lines[i].strip().split()
        for j in tokens[-3:]:
            forces.append(float(j))
    return forces

f = open("dump.lammpstrj", "r")
for i in f:
    if i.strip().startswith("ITEM: NUMBER OF ATOMS"):
        break
for i in f:
    tokens = i.strip().split()
    n_atoms = int(tokens[0])
    break
f.close()

f = open("dump.lammpstrj", "r")
flag = 1
lines = []
n = 0
while(flag):
    flag = 0
    for i in f:
        flag = 1
        lines.append(i)
        n += 1
        if n % (9 + n_atoms) == 0:
            forces = parse_block(lines)
            forces_frames.append(forces)
            n = 0 
            lines = []
            break
f.close()

f = open("log.lammps", "r")
for i in f:
    if i.strip().startswith("PotEng"):
        break

stress_frames = []
for i in f:
    if i.strip().startswith("Loop time"):
        break
    tokens = i.strip().split()
    energy_frames.append(float(tokens[0]))
    t2 = []
    for ii in tokens[1:]:
        t2.append(float(ii))
    stress_frames.append(t2)
        
f.close()

if not os.path.exists("lammps_raw"):
    os.mkdir("lammps_raw")

os.chdir("lammps_raw")
o = open("energy.raw", "w")
for i in energy_frames:
    tokens = i*kcal2ev
    o.write("%.10f "%tokens+"\n")
o.close()

o = open("force.raw", "w")
for i in forces_frames:
    for j in i:
        tokens = j*kcal2ev
        o.write("%.10f "%tokens)
    o.write("\n")
o.close()

o = open("virial.raw", "w")
for i in stress_frames:
    print(i)
    xx, yy, zz, xy, xz, yz = [ii*b2ev for ii in i]
    yx, zx, zy = xy, xz, yz
    o.write("%.10f %.10f %.10f %.10f %.10f %.10f %.10f %.10f %.10f\n"%(xx, xy, xz, yx, yy, yz, zx, zy, zz))
o.close()

os.chdir("..")
