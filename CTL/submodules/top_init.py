mportre
import os
import copy
from datetime import datetime
from getpass import getuser
import csvparser_sig as cvp
def gen(sig_csvobj,tpl_dir,out_dir):
os.popen('mkdir -p '+out_dir+'/src')
os.popen('mkdir -p '+out_dir+'/unit_test')
srcdir = tpl_dir+'/src/'
src_lst=os.listdir(srcdir)
unitdir = tpl_dir+'/unit_test/'
unit_list= os.listdir(unitdir)nit_list =os.listo
top_cfg(sig_csvobj)
for fname in src_lst:
if os.path.isfile(srcdir+fname) and (os.path.splitext(srcdir+fname)[1]!='.swp') and (os.path.
splitext(srcdir+fname)[1]!='.swo'):
workfile = tpl_file(srcdir,fname,sig_csvobj)
workfile.out(out_dir+'/src/')
for fname in unit_list:
if os.path.isfile(unitdir+fname)and (os.path.splitext(unitdir+fname)[1]!='.swp') and (os.path.splitext(unitdir+fname)[1]!='.swo'):
workfile = tpl_file(unitdir,fname,sig_csvobj)
workfile.out(out_dir+'/unit_test/')
listf=tpllistf = tpl_file(tpl_dir+'/', 'xxx_utils.list',sig_csvobj)
listf.out(out_dir+'/')
def top_cfg(c):#{{{
ifc.ctl_mode=='packe'packet' :#{{{
data= cvp.sig_inst()
data.name=c.da
data.wia.width= c.data_width
data.ctrl.append('bus')
data.ctrl_val.append('8')
data.ctrl.append('maxlens')
data.ctrl_val.append(c.maxlens)
c.siglist.append(data)
last=cvp.sig_inst()
Last.name=c.last_nar
last.width='1'
last.ctrl =['last']
last.ctrl_val= ['']
list.append(last)
if ('sop_name' in c._dict_)and c.sop_name:
sop=cvp.sig_inst()
sop.name=c.sop_name
sop.width='1'
sop.ctrl_val=[']
list.append(sop)
if c.mask_mode
mask = cvp.sig_inst()
mask.ctrl.append('cycend')
mask.ctrl_val.append()
.name=c.mask_name
sk.width = str(int(c.data(c.data_width) /8)
c.siglist.append(mask)
elif c.mask_mode == 'offset_A'or c.mask_mode == 'offset_B':
mask= cvp.si
mask.ctrl.append('cycend')
mask.ctrl_val.append(')
k.name=c.mc.mask_name
ask.width= str(binin(int(c.data_width)/8).count('θ')-1)
siglist.append(mask)c.sigli
mask = cvp.sig_inst()
ask.name=c.mask_name
ask.width=str(int(c.data_width)/
c.siglist.append(mask)
mask_h=cvp.sig_inst()
c.mask_name_h=mask_h.name
mask_h.width = str(int(c.data_width)
ask_h.self='1'
h.ctrl.append('norand')
ask_h.ctrl_val_val.append(')
c.siglist.append(mask_
mask_t=cvp.sig_inst()
ask_t.name=c.mask_name+'_t'
ask_name_t =mask_t.name
sk_t.width=str(int(c.data_widwidth)/8)
ask_t.self='1'
mask_t.ctrl.append('norand')
