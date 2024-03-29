import os

FOLDERS = ["B1", "B2", "B3", "B4"]
ELEMENT = "GaN"
FLAGS = []
for i in FOLDERS:
    FLAGS.append(ELEMENT + i)

get_energy = "bash ~/soft/simpy/tools/vasp/sum_energy.sh"
get_vols = "cmdall 'python ~/soft/simpy/lib/e_2_contcar.py' > vols"
get_bulk_modulus = "python ~/soft/simpy/tools/vasp/eos.py"
get_geo = "cat ./*/geo > geo"
add_flag = "python ~/soft/simpy/tools/reax/addflag.py %flag%"

n = 0
for i in FOLDERS:
    if os.path.exists(i):
        os.chdir(i)
        os.chdir("scan")
        os.system(get_energy)
        os.system(get_vols)
        os.system(get_bulk_modulus)
        os.system(get_geo)
        cmd = add_flag
        cmd = cmd.replace("%flag%", FLAGS[n])
        os.system(cmd)
        os.chdir("..")
        os.chdir("..")
        n += 1

