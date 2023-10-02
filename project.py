#!/usr/bin/env python3
#!pip install numpy
import sys
import math
from FCFS import *
from SJF import *
from SRT import *
from RR import *

class Rand48(object):
    def __init__(self, seed):
        self.n = seed

    def seed(self, seed):
        self.n = seed

    def srand(self, seed):
        self.n = (seed << 16) + 0x330e

    def next(self):
        self.n = (0x5DEECE66D * self.n + 0xB) & (2 ** 48 - 1)
        return self.n

    def drand(self):
        return self.next() / 2 ** 48

    def lrand(self):
        return self.next() >> 17

    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

class process(object):
  def __init__(self,inputp):
    #all these value needs taken from input 
    #here just a example of calculation
    if (inputp[0]>25):
      self.id = 71 + inputp[0]
    else:
      self.id = 65+inputp[0] #from input list chr(proc.get_id())
    self.arrival_time = inputp[1]
    self.number_cpu_brust = inputp[2];
    self.predict_cpu_burst_time = inputp[3]
    self.lambda_in = inputp[4]
    self.rand48 = inputp[5]
    self.upper_bound = inputp[6]
    self.cpu_bound = inputp[7]
    self.num_process = 0;#
    self.ms_burst_run = 0#
    #for simout
    self.wait_time = 0
    
    self.all_number_cpu_brust = []
    self.all_io_brust_time = []
    self.all_io_bound_cpu = []
    self.all_cpu_bound_cpu = []
    
    for i in range(self.number_cpu_brust):
      if(self.cpu_bound==1):
        output = "CPU-bound process"
        temp = self.next_exp()*4
        self.all_number_cpu_brust.append(temp)
        self.all_cpu_bound_cpu.append(temp)
        if(i == self.number_cpu_brust -1):
          break
        self.all_io_brust_time.append(math.floor(self.next_exp()*10/8))
      else:
        output = "I/O-bound process"
        temp=self.next_exp()
        self.all_number_cpu_brust.append(temp)
        self.all_io_bound_cpu.append(temp)
        if(i == self.number_cpu_brust -1):
          break
        temp=self.next_exp()
        self.all_io_brust_time.append(temp*10)
    out = "burst"
    if(self.number_cpu_brust>1):
      out = "bursts"
    print("{} {}: arrival time {}ms; {} CPU {}"\
    .format(output,chr(self.id),self.arrival_time,self.number_cpu_brust,out))
    self.remain = self.predict_cpu_burst_time - self.ms_burst_run;
  def print_result(self):
    for i in range(self.number_cpu_brust):
        if(i == self.number_cpu_brust -1):
          print("--> CPU burst {}ms"\
          .format(self.all_number_cpu_brust[i]))
        else:
          print("--> CPU burst {}ms --> I/O burst {}ms"\
          .format(self.all_number_cpu_brust[i],self.all_io_brust_time[i]))
    

  
  def re_new_re(self):
    self.remain = self.predict_cpu_burst_time - self.ms_burst_run;
  def check_end(self):
    if(self.num_process < self.number_cpu_brust):
      return False
    return True

  def get_id(self):
    return self.id
  def get_arr(self):
    return self.arrival_time

  def add_num_proc(self):
    self.num_process +=1

  def get_num_proc(self):
    return self.num_process
  def get_cpu_pre_time(self):
    return self.all_number_cpu_brust[self.num_process-1]

  def get_cpu_time(self):
    return self.all_number_cpu_brust[self.num_process]
  def get_io_time(self):
    if(self.num_process > len(self.all_io_brust_time)-1):
      return 0
    else:
      return self.all_io_brust_time[self.num_process]


  def next_exp(self):
    while(1):
      arrival_time =  math.ceil(((math.log(self.rand48.drand()))/self.lambda_in)*-1.0)
      if(arrival_time <= self.upper_bound):
        return arrival_time

def up3(number):
  return math.ceil(number * 1000) / 1000

def rand(rand48,in_lambda,up_bound):
  while(1):
    ret =((math.log(rand48.drand()))/in_lambda)*-1
    if(ret <= up_bound):
      return ret

def main():
  f = open("simout.txt","w")
  if(9 < len(sys.argv) or len(sys.argv) <9):
    print("InValid number of argv input")
    sys.exit()
  
  #argv from input
  num_proc_id = int(sys.argv[1])#1
  num_cpu_bound = int(sys.argv[2])#2
  seed = int(sys.argv[3])#3
  in_lambda = float(sys.argv[4])#4
  up_bound = int(sys.argv[5])#5
  time_context_switch = int(sys.argv[6])
  alpha_constant = float(sys.argv[7])
  time_slics = int(sys.argv[8])
  
  rand48 = Rand48(seed)
  rand48.srand(seed)
  cpu = 0
  out = "process"
  if(num_cpu_bound>1):
    out="processes"
  print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(num_proc_id,num_cpu_bound,out))
  predict_cpu_burst_time = 1/in_lambda
  list_process = []
  
  #project_p1
  for i in range(int(num_proc_id)):
    arrival_time = math.floor(rand(rand48,in_lambda,up_bound));
    number_cpu_brust = math.ceil(rand48.drand()*64)
    pid = i
    if(num_proc_id-i==num_cpu_bound):
      cpu = 1
    inputp = [pid,arrival_time,number_cpu_brust,int(predict_cpu_burst_time),in_lambda,rand48,up_bound,cpu]
    proc = process(inputp)
    list_process.append(proc)
    #proc.print_result()
  
  #project_p2
  list_process = sorted(list_process, key=operator.attrgetter('arrival_time'))
  print()
  print("<<< PROJECT PART II -- t_cs={}ms; alpha={:.2f}; t_slice={}ms >>>".format(time_context_switch,alpha_constant,time_slics))

  cpu1 = FCFS(time_context_switch,list_process,time_slics)
  cpu1.FCFS()
  out1 = cpu1.simout()
  print()
  
  cpu2 = SJF(time_context_switch,list_process,time_slics,alpha_constant)
  cpu2.SJF()
  out2 = cpu2.simout()
  print()
  cpu3 = SRT1(time_context_switch,list_process,time_slics,alpha_constant)
  cpu3.SRT()
  out3 = cpu3.simout()

  print()
  cpu4 = RR(time_context_switch,list_process,time_slics)
  cpu4.RR()
  out4 = cpu4.simout()
 
  

  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out1[0],up3(out1[1]*100),\
  up3(out1[2]),up3(out1[3]),up3(out1[4]),\
  up3(out1[5]),up3(out1[6]),up3(out1[7]),\
  up3(out1[8]),up3(out1[9]),up3(out1[10]),\
    out1[11],out1[12],out1[13],\
    out1[14],out1[15],out1[16]\
    ))
  f.write("\n")
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out2[0],up3(out2[1]*100),\
  up3(out2[2]),up3(out2[3]),up3(out2[4]),\
  up3(out2[5]),up3(out2[6]),up3(out2[7]),\
  up3(out2[8]),up3(out2[9]),up3(out2[10]),\
    out2[11],out2[12],out2[13],\
    out2[14],out2[15],out2[16]\
    ))
  f.write("\n")
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out3[0],up3(out3[1]*100),\
  up3(out3[2]),up3(out3[3]),up3(out3[4]),\
  up3(out3[5]),up3(out3[6]),up3(out3[7]),\
  up3(out3[8]),up3(out3[9]),up3(out3[10]),\
    out3[11],out3[12],out3[13],\
    out3[14],out3[15],out3[16]\
    ))
  
  f.write("\n")
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out4[0],up3(out4[1]*100),\
  up3(out4[2]),up3(out4[3]),up3(out4[4]),\
  up3(out4[5]),up3(out4[6]),up3(out4[7]),\
  up3(out4[8]),up3(out4[9]),up3(out4[10]),\
    out4[11],out4[12],out4[13],\
    out4[14],out4[15],out4[16]\
    ))
  f.close()
main()