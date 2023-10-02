import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import time
import copy
import sys
from math import ceil
import operator
import numpy as np
class SRT1(object):
  def __init__(self,ctsw,data,t_cs,alpha_constant):
    self.time = 0
    #self.taus = {}# make a dict
    self.time_context_switch = ctsw
    self.alpha = alpha_constant
    
    self.processList = copy.deepcopy(data)
    self.running = False#is cpu run or not
    self.io_run = False#is io run or not
    self.current_io_run_to = 0#没用到
    self.in_io_process = []
    self.process_terminate = 0 #我有多少process 跑过
    self.process_in_CPU = []#我想的是放我目前cpu在跑的process
    
    #testing code
    self.complete = []
    self.cpu_swit = 0
    self.total_wait = 0
    self.cpu_wait_time = 0
    self.cont_swit_total = 0
    self.total_preempt = 0
    self.cpu_preemt = 0

  def wait_time_add(self,queue):
    for i in queue:
      i.wait_time += 1;
    for i in self.complete:
      i.wait_time +=1

  def to_str(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret

  def get_proc_cpu_time(self,proc):
  #好像是一个计算时间用的，但是我用了就时间错误了，你可以试试
      if(proc.ms_burst_run == 0):
        return proc.get_cpu_time()
      else:
        return proc.get_cpu_time() - proc.ms_burst_run

  def check_ari(self,queue):
    temp = 0
    for i in self.processList:
      if(i.get_arr() == self.time):
        temp = 1
        queue.append(i)
        #queue = sorted(queue, key = lambda x: [x.predict_cpu_burst_time,x.get_id()]);
        queue.sort(key = operator.attrgetter("remain","id"))
        if(self.time < 10000):
          print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue [Q {}]"\
          .format(self.time,chr(i.get_id()),i.predict_cpu_burst_time,' '.join(self.to_str(queue))))
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
      self.check_ari(queue)
      if(i < self.time_context_switch//2-1):
        self.check_io_finish(queue) 

  def for_ti0(self,queue):
    self.check_io_finish(queue) 

  def add_con_sw_ti(self,queue,proc):
    self.cont_swit_total +=1
    if(proc.cpu_bound == 1):
      self.cpu_swit+=1
    for i in range((self.time_context_switch)//2):
      self.time +=1
      if(i==(self.time_context_switch)//2-1):
        if(len(self.complete)!=0):
          self.complete[0].re_new_re()
          queue.append(self.complete[0]);
          self.complete.pop(0)
          queue.sort(key = operator.attrgetter("remain","id"))
      self.wait_time_add(queue);
      self.check_ari(queue)
      self.check_io_finish(queue)
    
    if(len(self.complete)!=0):
        self.complete[0].re_new_re()
        queue.append(self.complete[0]);
        self.complete.pop(0)
        queue.sort(key = operator.attrgetter("remain","id"))

  def time_plus(self,time,queue):#没用到
    for i in range(time):
      self.time +=1;
      self.check_ari(queue)
#------------------------------------------------------------------------------#
  def cpu_burst(self,time_in,queue,proc):
    
    output= []
    if(len(queue)==0):
      output = "<empty>"
    else:
      output = ' '.join(self.to_str(queue))

    if(proc.ms_burst_run == 0): 
      if(self.time < 10000):
        print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst [Q {}]"\
        .format(self.time,chr(proc.get_id()),proc.predict_cpu_burst_time,time_in,output))
  
    else:
      if(self.time < 10000):
        print("time {}ms: Process {} (tau {}ms) started using the CPU for remaining {}ms of {}ms burst [Q {}]"\
        .format(self.time,chr(proc.get_id()),proc.predict_cpu_burst_time,proc.get_cpu_time() - proc.ms_burst_run,proc.get_cpu_time(),output))
    self.process_in_CPU= [];
    self.process_in_CPU.append(proc);
    self.running = True;
    check_c =self.check_io_finish(queue)
    if(check_c == 2):
      self.running = False;
      return False
    

    #----------------------------------#
    if(len(queue) != 0 and queue[0].remain < proc.remain):
      if(self.time < 10000):
        print("time {}ms: Process {} (tau {}ms) will preempt {} [Q {}]".format(self.time,chr(queue[0].get_id()),\
        queue[0].predict_cpu_burst_time,chr(proc.get_id()),' '.join(self.to_str(queue)) ))
      self.total_preempt +=1
      if(proc.cpu_bound == 1):
        self.cpu_preemt += 1
      self.total_wait -= self.time_context_switch//2
      if(proc.cpu_bound==1):
        self.cpu_wait_time -= self.time_context_switch//2
      queue.append(proc);
      proc.re_new_re()
      self.running = False;
      queue.sort(key = operator.attrgetter("remain","id"))
      return False

    

    
    for i in range(time_in):
      
      self.time += 1
      self.wait_time_add(queue);
      proc.ms_burst_run+= 1
      if(i < time_in -1):
        self.check_ari(queue)
      if(i < time_in -1 and self.io_run):
        check_c = self.check_io_finish(queue)
        if(check_c == 2):
          #queue.append(proc);
          #proc.re_new_re()
          #queue.sort(key = operator.attrgetter("remain","id"))
          self.running = False;
          return False
      
    

    if(proc.get_cpu_time() - proc.ms_burst_run == 0):
      proc.ms_burst_run = 0
      proc.num_process+=1
    else:
      queue.append(proc)
      proc.re_new_re()
      queue.sort(key = operator.attrgetter("remain","id"))
      self.check_ari(queue)
      self.check_io_finish(queue)
      self.running = False
      return False
    self.running = False;
    
    #--------------------------------#
    if(len(queue)==0):
      output = "<empty>"
    else:
      output = ' '.join(self.to_str(queue))
      
    if(proc.get_num_proc() < proc.number_cpu_brust):
      tmp = copy.deepcopy(proc.predict_cpu_burst_time)
      
      key = chr(proc.id)
      tau = proc.predict_cpu_burst_time
      alpha = self.alpha
      cpu_pre_time = proc.get_cpu_pre_time()
      t = 1 - np.float32(alpha)
      tau *= np.float32(t)
      tau += np.float32(cpu_pre_time) * np.float32(alpha)
      proc.predict_cpu_burst_time = ceil(tau)
      
      proc.remain = proc.predict_cpu_burst_time
      #queue = sorted(queue, key = lambda x: [x.predict_cpu_burst_time,x.get_id()]);
      if(proc.number_cpu_brust - proc.num_process > 0):
        proc.ms_burst_run = 0
        if(proc.number_cpu_brust - proc.num_process == 1):
          if(self.time < 10000):
            print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst to go [Q {}]"\
            .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process,\
              output))
          if(self.time < 10000):
            print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms [Q {}]"\
            .format(self.time,  chr(proc.get_id()), tmp, proc.predict_cpu_burst_time,output))
        else:
          if(self.time < 10000):
            print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} bursts to go [Q {}]"\
            .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process,\
              output))
          if(self.time < 10000):
            print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms [Q {}]"\
            .format(self.time,  chr(proc.get_id()), tmp, proc.predict_cpu_burst_time,output))
          
      else:
        if(len(queue) == 0):
          if(proc.number_cpu_brust - proc.num_process == 1):
            if(self.time < 10000):
              print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst to go [Q <empty>]"\
              .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process))
            if(self.time < 10000):
              print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms [Q <empty>]"\
              .format(self.time,chr(proc.get_id()), tmp, proc.predict_cpu_burst_time))
          else:
            if(self.time < 10000):
              print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} bursts to go [Q <empty>]"\
              .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process))
            if(self.time < 10000):
              print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms [Q <empty>]"\
              .format(self.time,chr(proc.get_id()), tmp, proc.predict_cpu_burst_time))
        
        else:
          if(proc.number_cpu_brust - proc.num_process == 1):
            if(self.time < 10000):
              print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst to go [Q {}]"\
              .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process,\
                ' '.join(self.to_str(queue))))
            if(self.time < 10000):
              print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms [Q {}]"\
              .format(self.time, chr(proc.get_id()), tmp, proc.predict_cpu_burst_time,' '.join(self.to_str(queue))))
          else:
            if(self.time < 10000):
              print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} bursts to go [Q {}]"\
              .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process,\
                ' '.join(self.to_str(queue))))
            if(self.time < 10000):
              print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms [Q {}]"\
              .format(self.time, chr(proc.get_id()), tmp, proc.predict_cpu_burst_time,' '.join(self.to_str(queue))))
          

    else:
      self.total_wait += proc.wait_time;
      if(proc.cpu_bound==1):
        self.cpu_wait_time += proc.wait_time
      if(len(queue) == 0 ):
        print("time {}ms: Process {} terminated [Q <empty>]".format(self.time,chr(proc.get_id())))
        self.add_con_sw_ti(queue,proc)
      else:
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),' '.join(self.to_str(queue))))
        self.add_con_sw_ti(queue,proc)

#------------------------------------------------------------------------------#
  def io_burst_bef(self,time_in,queue,proc):

    self.io_run = True;
    #queue = sorted(queue, key = lambda x: [x.predict_cpu_burst_time,x.get_id()]);
    temp_time = copy.deepcopy(self.time)

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
    io_run_to = self.time + time_in;
    io_run_to = int(io_run_to)
    self.io_run = True;
    self.in_io_process.append([proc,io_run_to])
    self.in_io_process.sort(key = lambda x:x[1])
#------------------------------------------------------------------------------#
  def check_io_finish(self,queue):

    checks1 = 0
    flag = False
    self.in_io_process.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    if(len(self.in_io_process)!= 0):
      while(while_it < len(self.in_io_process)):
        if(self.time == self.in_io_process[while_it][1]):
          if(len(self.process_in_CPU) ==1):
            for i in queue:
                i.re_new_re()
            #print(self.process_in_CPU[0].predict_cpu_burst_time - self.process_in_CPU[0].ms_burst_run,self.in_io_process[while_it][0].predict_cpu_burst_time)
            if((self.process_in_CPU[0].predict_cpu_burst_time - self.process_in_CPU[0].ms_burst_run > \
              self.in_io_process[while_it][0].predict_cpu_burst_time) and flag== False and self.running == True):
              queue.append(self.in_io_process[while_it][0]);
              checks1 = 2
              for i in queue:
                i.re_new_re()
              queue.sort(key = operator.attrgetter("remain","id"))
              if(self.time < 10000):
                print("time {}ms: Process {} (tau {}ms) completed I/O; preempting {} [Q {}]".format(\
              self.time,chr(self.in_io_process[while_it][0].get_id()),self.in_io_process[while_it][0].predict_cpu_burst_time,\
              chr(self.process_in_CPU[0].get_id()), ' '.join(self.to_str(queue))))
              if(self.process_in_CPU[0].cpu_bound == 1):
                self.cpu_preemt += 1
              if(self.process_in_CPU[0].cpu_bound==1):
                self.cpu_wait_time -= self.time_context_switch//2
              self.complete.append(self.process_in_CPU[0])
              self.in_io_process.pop(while_it)
              while_it = 0
              flag = True;
              self.total_preempt +=1
              self.total_wait -= self.time_context_switch//2
              continue
            else:
              if(checks1!=2):
                checks1 = 1
          queue.append(self.in_io_process[while_it][0])
          for i in queue:
            i.re_new_re()
          queue.sort(key = operator.attrgetter("remain","id"))
          if(self.time < 10000):
            print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue [Q {}]"\
            .format(self.time,chr(self.in_io_process[while_it][0].get_id()),self.in_io_process[while_it][0].predict_cpu_burst_time,' '.join(self.to_str(queue))))
          self.in_io_process.pop(while_it)
          while_it = 0
          if(len(self.in_io_process) == 0):
            self.io_run = False
        else:
          while_it +=1

    if(checks1 == 1):
      return 1
    elif(checks1 == 2):
      return 2
    else:
      return 0
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
    s=self.cpu_preemt
    t=self.total_preempt-self.cpu_preemt
    return ["SRT",a,b,c,d,e\
      ,f,g,h\
      ,k,L,m\
      ,n,o,r\
      ,s,t]
#------------------------------------------------------------------------------#
  def SRT(self):
    print("time {}ms: Simulator started for {} [Q <empty>]".format(self.time,"SRT"))
    queue = []#ready queue 
    
    while(1):#self.time < 18300
      
      if(self.running == False and len(queue) != 0):

        proc = copy.deepcopy(queue[0])
        
        queue.pop(0)
        self.add_con_sw_ti0(queue,proc);
        cpu_burst_time_temp = self.get_proc_cpu_time(proc); 
        io_burst_time_temp = proc.get_io_time()
        
        check = self.cpu_burst(cpu_burst_time_temp,queue,proc)
        if(check == False):
          self.add_con_sw_ti(queue,proc)
          continue

        if(io_burst_time_temp != 0):
          self.io_burst_bef(io_burst_time_temp,queue,proc)
          continue
        else:
          self.process_terminate += 1
          continue

      if(len(queue) == 0 and self.running == False and self.io_run == False\
       and self.process_terminate != 0):
        break

      if(self.running == False):

        ck1 = self.check_ari(queue)

        if(ck1 == True):
          continue
        if(self.io_run):
          ck2 = self.check_io_finish(queue)
          
          if(ck2 == 1):

            continue
        self.time += 1
        self.wait_time_add(queue);

        self.check_ari(queue)

        if(self.io_run):

          self.check_io_finish(queue)
          
          

    print("time {}ms: Simulator ended for SRT [Q <empty>]".format(self.time))
