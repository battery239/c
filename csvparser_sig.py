import csv
import re


class sig_inst():
    def __init__(self):
        self.name = ''
        self.width = '1'
        self.idle_val = None
        self.cb = []
        self.cbmode = []
        self.ctrl = []
        self.ctrl_val= []
    
    def __str__(self):
        output = ''
        for var in self.__dict__:
            output += str(var)+' : '+str(self.__dict__[var])+'\n' 
        return output

class sig_csvobj():
    def __init__(self,filepath):
        self.csv_file = csv.reader(open(filepath, 'r'))
        self.siglist=[]
        self.templist=[]
        self.sigbegin=False
        self.debug=False
        #self.top_name=''#{{{
            #self.ctl_mode=
            #self.bp_mode=
            #self.mask_mode=
            #self.bp_name=
            #self.vld_name=
            #self.rdy_name=
            #self.last_name=
            #self.mask_name=
            #self.data_name=
            #self.data_width=
            #self.msB=''#}}}
        
        self.main()
    
    def pr(self):
        for n in self._dict_:
            print n
            print self.__dict__[n]
        for sig in self.siglist:
            print sig

    def main(self):
        for l in self.csv_file:
            if l[0] == 'sig':
                self.sigbegin=True
                self.unlock()
                self.lock(L)
            elif not self.sigbegin:
                self.__dict__[l[0]]=l[1]
            else:
                self.sigprop(l)
        self.unlock()

    def lock(self,l):
        for signame in l[1:]:
            if signame:
                newinst=sig_inst()
                newinst.name=signame
                self.templist.append(newinst)

    def unlock(self):
        for sig in self.templist:
            self.siglist.append(sig)
        self.templist=[]
    
    def sigprop(self,l):
        idx=0
        cbmode=0
        for prop in l[1:]:
            if prop:
                if l[0]== 'idle_val':
                    self.templist[idx].idle_val=prop
                elif l[0] == 'ctrl':
                    ctrl=re.split("\*",prop)
                for i in ctrl:
                    if ':' in i:
                        (arg,val)=re.split("\:*",i)
                        self.templist[idx].ctrl.append(arg)
                        self.templist[idx].ctrl_val.append(val)
                    else:
                        self.templist[idx].ctrl.append(i)
                         else:
self.templist[idx].ctrl.append(i)
self.templist[idx].ctrl_val.append(None)
elif re.match("cb_",l[0]):
cb=l[0][3:]
if cb not in self.templist[idx].cb:
self.templist[idx].cb.append(cb)
self.templist[idx].cbmode.append(0)
cb_idx= self.templist[idx].cb.index(cb) 
self.templist[idx].cbmode[cb_idx] = prop 
else:
self.templist[idx].__dict__[l[0]] = prop
idx +=1