#!/usr/bin/env python
import os
import time
import random

def job_list(username):
    jobRun = []
    jobWait = []
    jobErr = []
    f = os.popen("qstat -n -u %s"%username)
    for i in f:
        if len(i.split()) == 11:
            if i.startswith('_'):
                pass
            else:
                a = i.split()
                jobId = a[0].split('.')[0]
                if a[-2] == "R":
                    jobRun.append(jobId)
                elif a[-2] == "Q":
                    jobWait.append(jobId)
                elif a[-2] == "E":
                    jobErr.append(jobId)
    f.close()
    return jobRun, jobWait, jobErr
def job_path(jobList):
    job_path = {}
    for i in jobList:
        lines = ""
        f = os.popen("qstat -f %d"%int(i))
        for j in f:
            if j.strip().startswith("Variable_List"):
                break
        for j in f:
            if j.strip().startswith("etime"):
                break
            else:
                lines = lines + j.strip()
        f.close()
        for j in lines.split(","):
            if j.startswith("PBS_O_WORKDIR"):
                temp = j.split("=")
                job_path[i] = temp[1]
    return job_path

def resub(job_path, freenodes_list):
    for (i,j) in job_path.items():
        if os.path.isdir(j):
            os.chdir(j)
            temp = random.randint(0,(len(freenodes_list)-1))
            nodes_available = freenodes_list[temp]
            os.system("qsub -l nodes=%s:ppn=%s %s"%(nodes_available, "8", "grompp.sh"))
            time.sleep(0.8)
        else:
            print "----------error--------%d-----"%int(i)
def job_state():
    jobRun, jobWait, jobErr = job_list("chengtao")
    jobList = job_path(jobRun)
    print "-------------------------------Job-Running-------------------------------------"
    jobListKey = jobList.keys()
    jobListKey.sort()
    for i in jobListKey: 
        print "%-7s%-90s"%(i, jobList[i])
    print "-------------------------------Job-Waiting-------------------------------------"
    jobList = job_path(jobWait)
    jobListKey = jobList.keys()
    jobListKey.sort()
    for i in jobListKey: 
        print "%-7s%-90s"%(i, jobList[i])
    print "-------------------------------Job-Error---------------------------------------"
    jobList = job_path(jobErr)
    jobListKey = jobList.keys()
    jobListKey.sort()
    for i in jobListKey: 
        print "%-7s%-90s"%(i, jobList[i])
    
if __name__ == "__main__":
    job_state()
