#!/usr/bin/env python

import os, shutil, sys
import socket

if socket.gethostname() == "fermion.wag.caltech.edu":
    print socket.gethostname()
    pbs = """#PBS -S /bin/tcsh
#PBS -l nodes=node-4-1:ppn=7,walltime=72:00:00
#PBS -j oe
#PBS -o pbs.out
#PBS -q qm
#PBS -N run

module load cuda/8.0
source /ul/haixiao/GCC/gcc-4.9.3-ion.csh
source /ul/haixiao/intel/bin/compilervars.csh intel64

cd $PBS_O_WORKDIR

cat $PBS_NODEFILE > vasp.nodes

# Determine the number of processors we were given
set nprocs = `wc -l < $PBS_NODEFILE`

echo "Setting up MPS..."
set node=`cat $PBS_NODEFILE | uniq`
set result=`ssh $node /ul/wolearyc/bin/setupMPS $PBS_JOBID`
if ($result == NONE_AVAILABLE) then
    echo "MPS setup failed: Not enough GPUs."
    exit
endif
echo "Running on GPUs:" $result > LOG

# Unset this so VASP doesn't bypass MPI.
unsetenv CUDA_VISIBLE_DEVICES
# Set these so VASP can locate server
setenv CUDA_MPS_PIPE_DIRECTORY /tmp/$PBS_JOBID/pipe
setenv CUDA_MPS_LOG_DIRECTORY /tmp/$PBS_JOBID/log

echo "Running..."
cd phonon
mpirun -np $nprocs vasp_gpu >> LOG
echo "Done. Quitting MPS."
ssh $node /ul/wolearyc/bin/quitMPS $PBS_JOBID

cd ..
ln -s ./phonon/KPOINTS KPOINTS
ln -s ./phonon/POTCAR POTCAR
ln -s ./phonon/POSCAR POSCAR.phon
ln -s ./phonon/OUTCAR OUTCAR.phon

echo "Setting up MPS..."
set node=`cat $PBS_NODEFILE | uniq`
set result=`ssh $node /ul/wolearyc/bin/setupMPS $PBS_JOBID`
if ($result == NONE_AVAILABLE) then
    echo "MPS setup failed: Not enough GPUs."
    exit
endif
echo "Running on GPUs:" $result > LOG

# Unset this so VASP doesn't bypass MPI.
unsetenv CUDA_VISIBLE_DEVICES
# Set these so VASP can locate server
setenv CUDA_MPS_PIPE_DIRECTORY /tmp/$PBS_JOBID/pipe
setenv CUDA_MPS_LOG_DIRECTORY /tmp/$PBS_JOBID/log

setenv VASP_RAMAN_RUN 'mpirun -np 7 vasp_gpu > log &> job.out'
setenv VASP_RAMAN_PARAMS '01_21_2_0.01'
vasp_raman > vasp_raman.out

echo "Done. Quitting MPS."
ssh $node /ul/wolearyc/bin/quitMPS $PBS_JOBID
"""

elif "armstrong" in socket.gethostname():
    pbs = """#!/bin/bash

#PBS -A ONRDC33663381
#PBS -V
#PBS -j oe
#PBS -N VASP
#PBS -q standard
#PBS -l select=4:ncpus=44:mpiprocs=44
#PBS -l walltime=12:00:00

export BIN_LOC=/p/home/taocheng/src/vasp/vasp.5.3
export exe=$BIN_LOC/vasp.std
echo "The executable is: " $exe

export DATADIR=$PBS_O_WORKDIR

export NPROCS=`wc -l $PBS_NODEFILE | cut -f1 -d " "`
export JOBID=`echo $PBS_JOBID | awk -F'.' '{print $1}'`
export OUTPUTDIR=$WORKDIR/VASP/$JOBID
echo "The output will temporarily be written to :" $OUTPUTDIR
echo "Job: " $JOBID "is starting with " $NPROCS "cores on:"
cat $PBS_NODEFILE
echo

echo $PBS_JOBID >  $DATADIR/jobinfo
cat $PBS_NODEFILE >>  $DATADIR/jobinfo
echo $OUTPUTDIR >>  $DATADIR/jobinfo

cd $PBS_O_WORKDIR

#
# Run EXE
#

date
export VASP_RAMAN_RUN='aprun -n 176 $exe > log'
export VASP_RAMAN_PARAMS='05_148_2_0.01'
python ./vasp_raman.py > vasp_raman.out

echo
date
echo "Job has finished."
cd ..

exit 0
"""

incar_phonon ="""! general
SYSTEM = phonon
ISTART = 0 
ICHARG = 2 
PREC = N 
ENCUT = 400.0 
NELMIN = 4
EDIFF = 1.0E-4 
IBRION = 5
ISMEAR = 1
SIGMA = 0.2
LWAVE = .FALSE. 
LCHARG = .FALSE. 
LREAL = Auto
IALGO = 48
ADDGRID = .TRUE.
! phonon
POTIM = 0.01
! parallelisation
NPAR = 7
! output
LELF = .FALSE.
LVTOT = .FALSE.
NWRITE=3
"""
incar_raman = """! general
SYSTEM = raman
ISTART = 0 
NWRITE = 3
ICHARG = 2 
PREC = N 
ENCUT = 400.0 
NELMIN = 4
EDIFF = 1.0E-4 
ISMEAR = 1
SIGMA = 0.2
LWAVE = .FALSE. 
LCHARG = .FALSE. 
LREAL = Auto
IALGO = 38
ADDGRID = .TRUE.
! raman
LEPSILON=.TRUE.
! parallelisation
NPAR = 7
ISYM = 0
! output
LELF = .FALSE.
LVTOT = .FALSE.
"""

o = open("pbs", "w")
o.write(pbs)
o.close()
os.system("chmod +x pbs")

o = open("INCAR", "w")
o.write(incar_raman)
o.close()

if not os.path.exists("phonon"):
    os.mkdir("phonon")

shutil.copy("./inp/POSCAR", "phonon")
shutil.copy("./inp/POTCAR", "phonon")
shutil.copy("./inp/KPOINTS", "phonon")

os.chdir("phonon")
o = open("INCAR", "w")
o.write(incar_phonon)
o.close()

