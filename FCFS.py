import time
import copy
import sys
import math
import operator

class FCFS(object):
  def __init__(self,ctsw,data,t_cs):
    self.time = 0;
    self.time_context_switch =ctsw;
    self.processList = copy.deepcopy(data)
    self.running = False#is cpu run or not
    self.io_run = False#is io run or not
    self.current_io_run_to = 0#没用到
    self.in_io_process = []
    self.process_terminate = 0
    self.time_slice = t_cs
    self.cpu_swit= 0
    #testing code
    self.total_wait = 0
    self.cpu_wait_time = 0
    self.cont_swit_total = 0
    self.total_preempt = 0 

  def wait_time_add(self,queue):
    for i in queue:
      i.wait_time += 1;

  def to_str(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret

  def check_ari(self,queue):
    temp = 0
    for i in self.processList:
      if(i.get_arr() == self.time):
        temp = 1
        queue.append(i)
        if(self.time < 10000):
          print("time {}ms: Process {} arrived; added to ready queue [Q {}]"\
            .format(self.time,chr(i.get_id()),' '.join(self.to_str(queue))))
    if(temp == 1):
      return True
    else:
      return False

  def add_con_sw_ti0(self,queue,proc):
    self.cont_swit_total +=1
    if(proc.cpu_bound == 1):
      self.cpu_swit+=1
    for i in range((self.time_context_switch)//2):
      self.time +=1
      self.wait_time_add(queue);
      if(i < self.time_context_switch//2-1):
        self.check_ari(queue)
        self.check_io_finish(queue) 

  def for_ti0(self,queue):
    self.check_ari(queue)
    self.check_io_finish(queue) 

  def add_con_sw_ti(self,queue,proc):
    self.cont_swit_total +=1
    if(proc.cpu_bound == 1):
      self.cpu_swit+=1
    for i in range((self.time_context_switch)//2):
      self.time +=1
      self.wait_time_add(queue);
      self.check_ari(queue)
      self.check_io_finish(queue)

  def time_plus(self,time,queue):#没用到
    for i in range(time):
      self.time +=1;
      self.check_ari(queue)
#------------------------------------------------------------------------------#
  def cpu_burst(self,time_in,queue,proc):
    #print("cpu_burst1")
    if(len(queue) == 0):
      if(self.time < 10000):
        print("time {}ms: Process {} started using the CPU for {}ms burst [Q <empty>]"\
          .format(self.time,chr(proc.get_id()),time_in))
    else:
      if(self.time < 10000):
        print("time {}ms: Process {} started using the CPU for {}ms burst [Q {}]"\
          .format(self.time,chr(proc.get_id()),time_in,' '.join(self.to_str(queue))))
    self.for_ti0(queue)
    #----------------------------------#
    self.running = True;
    for i in range(time_in-1):
      self.time += 1
      self.wait_time_add(queue);
      if(i < time_in -1):
        self.check_ari(queue)
      if(self.io_run):
        self.check_io_finish(queue)
    proc.add_num_proc()
    self.running = False;
    #--------------------------------#
    self.time +=1
    self.wait_time_add(queue);
    #print(self.time)
    if(proc.num_process < proc.number_cpu_brust):
      if(len(queue) == 0):
        if(proc.number_cpu_brust - proc.num_process == 1):
          if(self.time < 10000):
            print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q <empty>]"\
              .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process))
        else:
          if(self.time < 10000):
            print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q <empty>]"\
              .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process))
      else:
        if(proc.number_cpu_brust - proc.num_process == 1):
          if(self.time < 10000):
            print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q {}]"\
              .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process,\
                ' '.join(self.to_str(queue))))
        else: 
          if(self.time < 10000):
            print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]"\
              .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process,\
                ' '.join(self.to_str(queue))))
    else:
      #print(chr(proc.get_id()))
      if(proc.cpu_bound==1):
        self.cpu_wait_time += proc.wait_time
      self.total_wait += proc.wait_time;
      if(len(queue) == 0 ):
        print("time {}ms: Process {} terminated [Q <empty>]".format(self.time,chr(proc.get_id())))
        self.check_ari(queue)
        self.check_io_finish(queue)
        self.add_con_sw_ti(queue,proc)
      else:
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),' '.join(self.to_str(queue))))
        self.check_ari(queue)
        self.check_io_finish(queue)
        self.add_con_sw_ti(queue,proc)
    #print("cpu_burst2")
#------------------------------------------------------------------------------#
  def io_burst_bef(self,time_in,queue,proc):
    #print("io_burst_bef1")
    self.io_run = True;
    temp_time = copy.deepcopy(self.time)
    #self.add_con_sw_ti(queue)
    if(len(queue) == 0):
      if(self.time < 10000):
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q <empty>]"\
          .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2))
    else:
      if(self.time < 10000):
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q {}]"\
          .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2,' '.join(self.to_str(queue))))
    self.check_ari(queue)
    self.check_io_finish(queue)
    self.add_con_sw_ti(queue,proc)
    self.io_run = True;
    io_run_to = self.time + time_in;
    io_run_to = int(io_run_to)
    self.in_io_process.append([proc,io_run_to])
    self.in_io_process.sort(key = lambda x:x[1])

    #print("io_burst_bef2")

#------------------------------------------------------------------------------#
  def check_io_finish(self,queue):
    #print(self.in_io_process)
    #print(self.time)
    checks1 = 0
    self.in_io_process.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    if(len(self.in_io_process)!= 0):
      while(while_it < len(self.in_io_process)):
        if(self.time == self.in_io_process[while_it][1]):
          #for sk in self.in_io_process:
             #print(chr(sk[0].get_id()),self.time)
          checks1 = 1
          queue.append(self.in_io_process[while_it][0])
          if(self.time < 10000):
            print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]"\
              .format(self.time,chr(self.in_io_process[while_it][0].get_id()),' '.join(self.to_str(queue))))
          self.in_io_process.pop(while_it)
          while_it = 0
          if(len(self.in_io_process) == 0):
            self.io_run = False
        else:
          while_it +=1

    if(checks1 == 1):
      return True
    else:
      return False
#------------------------------------------------------------------------------#
  def check_time_slice(self,queue,time_in):#for RR
    if(time_in > self.time_slice):
      return True
    return False
#------------------------------------------------------------------------------#
  def check_alg_finish(self,queue):#没用到
    for i in queue:
      if(i.check_end() == False):
        return False
    return True
  def simout(self):
    count_total_burst_time = 0
    count_total_io_time = 0
    count_toal_cpu = 0
    for i in self.processList:
      for j in i.all_number_cpu_brust:
        count_total_burst_time += j
      for p in i.all_cpu_bound_cpu:
        count_toal_cpu += p
      for q in i.all_io_bound_cpu:
        count_total_io_time +=q
    #print("total_burst_time",count_total_burst_time)
    #print("wait",self.total_wait)
    count_burst = 0
    count_io = 0
    count_cpu = 0
    for i in self.processList:
      count_io += len(i.all_io_bound_cpu)
      count_cpu += len(i.all_cpu_bound_cpu)
      count_burst += len(i.all_number_cpu_brust)
    temp = (self.total_wait+count_total_burst_time+ self.time_context_switch*(self.cont_swit_total//2) )
    temp1 = (self.cpu_wait_time+count_toal_cpu+self.time_context_switch*(self.cpu_swit//2))
    temp2 = ((self.total_wait-self.cpu_wait_time)+count_total_io_time+self.time_context_switch*((self.cont_swit_total-self.cpu_swit)//2))
    #print(count_total_io_time/count_io)
    a=count_total_burst_time/self.time
    b=count_total_burst_time/count_burst
    e=self.total_wait/count_burst
    if(count_cpu != 0):
      c=count_toal_cpu/count_cpu
      f=self.cpu_wait_time/count_cpu
      k=temp1/count_cpu
    else:
      c=0
      f=0
      k=0
    if(count_io!=0):  
      d=count_total_io_time/count_io
      g=(self.total_wait-self.cpu_wait_time)/count_io
      L=temp2/count_io
    else:
      d=0
      g=0
      L=0
    h=temp/count_burst
    m=(self.cont_swit_total)//2
    n=self.cpu_swit//2
    o=(self.cont_swit_total)//2-self.cpu_swit//2
    r=self.total_preempt
    s=0
    t=self.total_preempt-0
    return ["FCFS",a,b,c,d,e\
      ,f,g,h\
      ,k,L,m\
      ,n,o,r\
      ,s,t]
#------------------------------------------------------------------------------#
  def FCFS(self):
    print("time {}ms: Simulator started for {} [Q <empty>]".format(self.time,"FCFS"));
    queue = []#ready queue 
    while(1):
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        queue.pop(0);
        self.add_con_sw_ti0(queue,proc);
        cpu_burst_time_temp = proc.get_cpu_time()
        io_burst_time_temp = proc.get_io_time()
        #print("IO:",io_burst_time_temp)
        self.cpu_burst(cpu_burst_time_temp,queue,proc);
        if(io_burst_time_temp != 0):
          self.io_burst_bef(io_burst_time_temp,queue,proc);
          continue
        else:
          self.process_terminate += 1
          continue
      if(len(queue) == 0 and self.running == False and self.io_run == False\
       and self.process_terminate != 0):
        break
      if(self.running == False):
        #print(self.running, len(queue),self.io_run)
        ck1 = self.check_ari(queue)
        if(ck1 == True):
          continue
        if(self.io_run):
          ck2 = self.check_io_finish(queue)
          if(ck2 == True):
            continue
        self.time +=1
        self.wait_time_add(queue);
        self.check_ari(queue)
        if(self.io_run):
          self.check_io_finish(queue)
    print("time {}ms: Simulator ended for FCFS [Q <empty>]".format(self.time))

    