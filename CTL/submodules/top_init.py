import re
import os
import copy
from datetime import datetime
from getpass import getuser
import csvparser_sig as cvp



def gen(sig_csvobj,tpl_dir,out_dir):
    os.popen('mkdir -p '+out_dir+'/src')
    os.popen('mkdir -p '+out_dir+'/unit_test')
    srcdir=tpl_dir+'/src/'
    src_lst=os.listdir(srcdir)
    unitdir =tpl_dir+'/unit_test/'
    unit_list=os.listdir(unitdir)
    top_cfg(sig_csvobj)
    for fname in src_lst:
        if os.path.isfile(srcdir+fname) and (os.path.splitext(srcdir+fname)[1]!='.swp') and (os.path.splitext(srcdir+fname)[1]!='.swo'):
            workfile = tpl_file(srcdir,fname,sig_csvobj)
            workfile.out(out_dir+'/src/')
    for fname in unit_list:
        if os.path.isfile(unitdir+fname) and (os.path.splitext(unitdir+fname)[1]!='.swp') and (os.path.splitext(unitdir+fname)[1]!='.swo'):
            workfile = tpl_file(unitdir,fname,sig_csvobj)
            workfile.out(out_dir+'/unit_test/')
    listf = tpl_file(tpl_dir+'/', 'xxx_utils.list',sig_csvobj)
    listf.out(out_dir+'/')

def top_cfg(c):#{{{
    if c.ctl_mode=='packet' :#{{{
        data=cvp.sig_inst()
        data.name=c.data_name
        data.width=c.data_width
        data.ctrl.append('bus')
        data.ctrl_val.append('8')
        data.ctrl.append('maxlens')
        data.ctrl_val.append(c.maxlens)
        c.siglist.append(data)
    
        last=cvp.sig_inst()
        last.name=c.last_name
        last.width='1'
        last.ctrl=['last']
        last.ctrl_val=['']
        c.siglist.append(last)
    
        if ('sop_name' in c.__dict__) and c.sop_name:
            sop=cvp.sig_inst()
            sop.name=c.sop_name
            sop.width='1'
            sop.ctrl=['sop']
            sop.ctrl_val=['']
            c.siglist.append(sop)
    
        if c.mask_mode =='tail':
            mask=cvp.sig_inst()
            mask.ctrl.append('cycend')
            mask.ctrl_val.append('')
            mask.name=c.mask_name
            mask.width=str(int(c.data_width)/8)
            c.siglist.append(mask)
        elif c.mask_mode == 'offset_A' or c.mask_mode == 'offset_B':
            mask= cvp.sig_inst()
            mask.ctrl.append('cycend')
            mask.ctrl_val.append('')
            mask.name=c.mask_name
            mask.width = str(bin(int(c.data_width)/8).count('0')-1)
            c.siglist.append(mask)
        elif c.mask_mode=='both':
            c.direction='msb'
            mask=cvp.sig_inst()
            mask.name=c.mask_name
            mask.width=str(int(c.data_width)/8)
            c.siglist.append(mask)
            mask_h=cvp.sig_inst()
            mask_h.name=c.mask_name+'_h'
            c.mask_name_h=mask_h.name
            mask_h.width=str(int(c.data_width)/8)
            mask_h.self='1'
            mask_h.ctrl.append('norand')
            mask_h.ctrl_val.append('')
            c.siglist.append(mask_h)
            mask_t=cvp.sig_inst()
            mask_t.name = c.mask_name+'_t'
            c.mask_name_t=mask_t.name
            mask_t.width=str(int(c.data_width)/8)
            mask_t.self='1'
            mask_t.ctrl.append('norand')
            mask_t.self ='1'
            mask_t.ctrl.append('norand')
            mask_t.ctrl_val.append('')
            c.siglist.append(mask_t)
            startpos =cvp.sig_inst()
            startpos.name=c.mask_name+'_hbubble'
            c.mask_name_b=startpos.name
            startpos.width=str(int(c.data_width)/8)
            startpos.self='1'
            c.siglist.append(startpos)
        #}}}
    if c.bp_mode == 'bp_cycle':
        c.bpcycle = True
        c.bp_mode='bp'
    if c.bp_mode=='hs':
        vld=cvp.sig_inst()
        vld.name=c.vld_name
        vld.width='1'
        vld.ctrl=['mon_must','sigonly']
        vld.ctrl_val=['','']
        vld.idle_val='0'
        rdy=cvp.sig_inst()
        rdy.name=c.rdy_name
        rdy.width='1'
        rdy.ctrl = ['drv_must', 'mon_must','sigonly']
        rdy.ctrl_val=['','','']
        c.siglist.append(vld)
        c.siglist.append(rdy)
    elif c.bp_mode == 'bp':
        vld=cvp.sig_inst()
        vld.name=c.vld_name
        vld.width='1'
        vld.ctrl=['mon_must','sigonly']
        vld.ctrl_val=['','']
        vld.idle_val ='0'
        c.siglist.append(vld)
        bp=cvp.sig_inst()
        bp.name=c.bp_name
        bp.width='1'
        bp.ctrl = ['drv_must','sigonly']
        bp.ctrl_val=['0','']
        bp.idle_val='0'
        c.siglist.append(bp)


    for s in c.siglist:
        if 'pack' in s._dict_:
            wd=0
            for member in re.split(",*",s.pack):
                for si in c.siglist:
                    if si.name==member:
                        wd+=int(si.width)
            s.width=wd
        if not ('self' in s.__dict__):
            s.cb.append('drv')
            s.cbmode.append('out')
            s.cb.append('mon')
            s.cbmode.append('in')
            if c.bp_mode=='hs':
                if s.name==c.rdy_name:
                    s.cbmode[s.cb.index('drv')]='in'
            elif c.bp_mode=='bp':
                if s.name==c.bp_name:
                    s.cbmode[s.cb.index('drv')]='in'
        if ('sample_mode' in s.__dict__) and ('@' in s.sample_mode): 
            s.at=[]
            for member in re.split("\@*",s.sample_mode):
                member = member.strip()
                if member:
                    s.at.append(member)
#}}}

class tpl_file:
    def __init__(self,fdir,fname,sig_csvobj):
        self.tplfile= open(fdir+fname,"r")
        self.fname=fname
        self.top_name = sig_csvobj.top_name
        self.csvobj=sig_csvobj
        self.outlines=[]
        self.infile()
        self.init_cb()
        self.filemode()
        self.cleanup()

def infile(self):#{{{
    for line in self.tplfile:
        self.outlines.append(line)
    for line in self.tplfile:
        self.outlines.append(line)
    self.tplfile.close()#}}}

def cleanup(self):#{{{
swap_en =0
idx =0
tmplines = copy.copy(self.outlines)
for l in tmplines:
if ('//‘ in l) and (l.lstrip()[:2]=='//'):
if ('Lcs mark begin'in L):
swap_en = 1
elif ('lcs mark'in l):
swap en =0
del self.outlines [idx]
else:
if swap en:
del self.outlines[idx]
else:
idx +=1
if (os.path.splitext(self.fname)[1]=='.sv'):
mtime datetime.now().strftime("Y-m-d %H:M:S")
self.outlines.insert(0,
”/米*米********米米米米****************水*****章***米米**水**
*****n)
self.outlines.insert(1,'// Generated by genCTL script ver.1.0\n')
self.outlines.insert(2,'// Author:'+getuser()+'\n')
self.outlines.insert(3,'/Created Time:'+mtime+'\n')
self.outlines.insert(4
def out(self,out dir):#f{
outfile open(out_dir+self.fname.replace('xxx',self.top_name),"w+")
for line in self.outlines:
outfile.write(line.replace('xxx',self.top name).replace('XXX',self.top_name.upper())) outfile.close()#})}
def ins_mark(self,mark,ins_lines):#({
total idx 0
for line in self.outlines:
if ('lcs mark'in line)and (mark==re.split("\:*"Line)[-1][:-1]):
indent Line.count('')
index total idx+1
for ins line in ins_lines:
self.outlines.insert(index,''*indent+ins line+'\n')
index +1
total_idx +1#))}
def init cb(self):#{f{
self.cb list =[
for sig in self.csvobj.siglist:
for cbname in sig.cb:
if (cbname+'cb')not in self.cb list:
self.cb list.append(cbname+'cb')
self.dict_cbname+_cb']=[门
self.dict_[cbname+'_cb'].append((sig.name,sig.cbmode[sig.cb.index(cbname)】))#})
def filemode(self):#{f{
if self.fname =='xxx interface.sv':
self.init_intf()
elif self.fname ='xxx dec.sv':
self.init dec()
elif self.fname ='xxx driver.sv':
self.init driver()
elif self.fname =='xxx rdy driver.sv':
self.init rdy driver()
elif self.fname ='xxx monitor.sv':
self.init_monitor()
elif self.fname ='xxx xaction.sv':
self.init xaction())
elif self.fname ='harness.sv':
self.init_harness()#)}
def init_dec(self):#{f{
wd_lines [
for sig in self.csvobj.siglist:
wd_lines.append('parameter '+sig.name.upper()+'WD ='+str(sig.width)+';')
self.ins _mark('wd',wd_lines);#
def init intf(self):#{
c self.csvobj
dec_lines [
mon link_lines [
drv link lines [
mon bp rdy link lines [
drv_bp_rdy_link lines [
xz4_lines =[
xz5_lines [
for sig in self.csvobj.siglist:
if 'self'not in sia.dict
 fior sig in self.csvobj.siglist:
if 'self'not in sig.dict
dec_lines.append('logic ['+sig.name.upper()+WD-1:0]'+sig.name+';')
if c.bp mode=='hs'and sig.name==c.rdy name or c.bp mode=='bp'and sig.name==c.bp_name:
drv bp rdy link lines.append('assign or force bus.'+sig.name+'dut'+sig.name+';')
mon bp rdy link lines.append('assign or force dut'''+sig.name+'=bus.'+sig.name+';')
else
mon link lines.append('assign or force bus.'+sig.name+'=dut '+sig.name+'; W)
drv_link lines.append('assign or force dut''+sig.name+'bus.'+sig.name+';\\')
if (sig.name =c.vld_name)or (sig.name =c.rdy_name)or c.bp_mode ='bp'and sig.name==c.
bp name):
xz4_lines.append('prj_assert_vld_xz(clk,rst_n,'+sig.name+')')
else
xz4 lines.append(''prj_assert_sign_xz(clk,rst_n,'+c.vld name+','+sig.name+')')
if c.bp mode=='hs'and sig.name!=c.rdy name:
xz5_lines.append(''prj_assert_sign_hold(clk,rst_n,'+c.vld_name+','+c.rdy_name+','+sig.
name+')')
self.ins_mark('dec',dec lines)
self.ins_mark('xz4',xz4 lines)
self.ins_mark('xz5',xz5_lines)
self.ins mark('mon link',mon link lines)
self.ins mark('drv_link',drv_link lines)
self.ins mark('mon_bp_rdy_link',mon_bp_rdy_link_lines)
self.ins_mark('drv_bp_rdy_link',drv_bp_rdy_link_lines)
for cbname in self.cb_list:
cb_lines [
cb_lines.append('clocking '+cbname+'@(posedge clk);')
cb lines.append('default input #INPUT_SKEW;')
cb lines.append('default output #OUTPUT SKEW;')
for sig in self.dict [cbname]:#Local vars[cbname]:
sigline =
if 'in'in sig[1]:
sigline sigline+'input
elif 'out'in sig[1]:
sigline sigline+'output
siglinesigline+sig[0]+';'
cb lines.append(sigline)
cb lines.append('endclocking\n')
self.ins_mark('cb',cb_lines)
bp_cb_lines =[
bp cb lines.append('clocking drv bp cb @(posedge clk);'
bp_cb_lines.append('default input #INPUT_SKEW;')
bp_cb_lines.append('default output #OUTPUT_SKEW;')
bp_cb lines.append('output '+c.bp_name+';')
bp_cb_lines.append('endclocking\n')
self.ins_mark('bp_cb',bp_cb_lines)
rdy cb lines=【]
rdy_cb_lines.append('clocking drv_rdy_cb @(posedge clk);')
rdy_cb_lines.append('default input #INPUT_SKEW;')
rdy_cb_lines.append('default output #OUTPUT_SKEW;'
rdy_cb_lines.append('input '+c.vld_name+';')
rdy_cb_lines.append('output '+c.rdy_name+';')
rdy_cb_lines.append('endclocking\n')
self.ins_mark('rdy_cb',rdy_cb_lines)
#self.ins mark('xz1',['@(posedge clk)disable iff(rst_n)!sisunknown('+c.vld_name+');']
self.ins mark('xz2',['@(posedge clk)disable iff(!rst_n Il '+c.vld_name+'!=1)!sisunknown(sign);
1) #if c.bp mode=='hs':
#self.ins mark('xz3',['@(posedge clk)disable iff(rst_n)'+c.rdy name+==0 66'+c.vld name+
=1 sstable(sign);'])#}}}
def init driver(self):#{{
c self.csvobj
drvsig_lines [
drvidle lines [
for sig in self.csvobj.siglist:
if 'drv'in sig.cb:
if 'out'in sig.cbmode[sig.cb.index('drv')]:
if sig.idle val !None:
drvsig lines.append('this.bus.drv cb.'+sig.name+'=-'+sig.idle_val+';')
drvidle_lines.append('this.bus.drv_cb.'+sig.name+'='+sig.idle val+';')
else:
drvsig_lines.append('this.bus.drv cb.'+sig.name+'=cyc q[i].'+sig.name+';')
self.ins_mark('drvsig',drvsig_lines)
self.ins mark('drvidle',drvidle_lines)
if c.bp_mode=='bp':#{{f
bpl lines =[
bp21ines=【]
bp3 lines
bp4 lines =[
bp5_lines =[
bp6_lines [

 bpl lines.append('bit '+c.bp name+'flag;')
bpl_lines.append('int '+c.bp name+'cnt;')
bp2 lines.append('if(this.bus.mon cb.'+c.bp_name+'==1)begin')
if c.ctl mode=='packet':
mline
if 'bpcycle'not in c.dict
mline =66 this.bus.mon_cb.'+c.last_name
bp2_lines.append('if(this.bus.mon_cb.'+c.vld_name+mline+'===1)'+c.bp_name+'cnt ++;'
elif c.ctl mode=='cycle':
bp2 lines.append('if(this.bus.mon cb.'+c.vld name+'===1)'+c.bp name+'cnt ++;'
bp2_lines.append('if('+c.bp_name+'_cnt >this.cfg.bp_delay)this.'+c.bp_name+'_flag 1;')
bp2 lines.append('end')
bp2 lines.append('else begin')
bp2_lines.append('if(this.'+c.bp_name+'cnt 0)this.'+c.bp_name+'cnt --;'
bp2 lines.append('else this.'+c.bp name+'flag 0;')
bp2_lines.append('end')
bp3_lines.append('if(this.in_fifo.is empty =0 66 this.'+c.bp name+'flag ==0)begin')
bp4_lines.append('else if(this.seq_item port.has do_available =1 6&this.'+c.bp_name+'_flag==
0)begin')
bp5_lines.append('this.'+c.bp name+'flag =0;')
bp5_lines.append('this.'+c.bp_name+'_cnt 0;')
bp6_lines.append('while(this.cfg.dyn_rst_mode =prj_dec:IMMEDIATE &this.'+c.bp_name+'_flag =
1)begin')
bp6_lines.append('this.drive idle();')
bp6_lines.append('@(this.bus.drv_cb);')
bp6_lines.append('end')
self.ins _mark('bp1',bp1 lines)
self.ins_mark('bp2',bp2_lines)
self.ins mark('bp3',bp3 lines)
self.ins_mark('bp4',bp4_lines)
self.ins_mark('bp5',bp5_lines)
self.ins_mark('bp6',bp6_lines)#})}
drvrdy_lines =[
drvmust [
mline ='
for sig in self.csvobi.siglist:
if 'drv must'in sig.ctrl:
drvmust.append(sig.name)
if drvmust:
drvrdy_lines.append('while(1)begin')
mline='if('
for s in drvmust:
mline +('this.bus.drv_cb.'+s+'==1 66')
drvrdy lines.append (mline[-4]+')break;'
drvrdy lines.append('else @(this.bus.drv_cb);'
drvrdy lines.append('end')
self.ins mark('drvrdy',drvrdy_lines)
drvmode lines =[
drvmode_dict={'DRV_0':''e','DRV_1':''1','DRV_RAND':'surandor','DRvX':'八'hx'}
for m in drvmode dict:
drvmode_lines.append('prj_dec:'+m+':begin')
for sig in self.csvobj.siglist:
if 'drv'in sig.cb:
if 'out'in sig.cbmode[sig.cb.index('drv')]and (sig.idle_val==None):
if (m =="DRV RAND")and (int(sig.width)>32):
drvmode lines.append('this.bus.drv_cb.'+sig.name+'<prj_func:get_nbits_rand('+self.
top_name+'dec:'+sig.name.upper()+'WD);')
else:
drvmode lines.append('this.bus.drv_cb.'+sig.name+'<='+drvmode dict[m]+';')
drvmode lines.append ('end')
self.ins mark('drvmode',drvmode lines)
def init_monitor(self):#{
monmust_lines =[
monmust=【]
for sig in self.csvobj.siglist:
if 'mon must'in sig.ctrl:
monmust.append(sig.name)
monmust_lines.append('if(this.bus.mon_cb.'+self.csvobj.vld name+'=1)this.is working 1;')
monmust_lines.append('else if(cyc_q.size ==0)this.is _working =0;')
if monmust:
mline ='if('
for s in monmust:
mline +('this.bus.mon cb.'+s+'==1 66')
monmust_lines.append(mline[:-4]+')begin')
else:
monmust_lines.append('if(0)begin')
self.ins mark('mon must',monmust_lines)
self ins mark('mon must end't'end'1

 self.ins_mark('mon must_end',['end'])
mon_sig_lines [
for sig in self.csvobj.siglist:
if 'mon'in sig.cb:
if ('in'in sig.cbmode[sig.cb.index('mon')])and ('sigonly'not in sig.ctrl):
mon sig lines.append('cyc tr.'+sig.name+'this.bus.mon _cb.'+sig.name+';')
self.ins mark('mon sig',mon_sig_lines)
for sig in self.csvobj.siglist:
if 'last'in sig.ctrl:
self.ins_mark('close',['if(this.bus.mon_cb.'+sig.name+'1 this.cfg.xaction mode==
pri dec:CYCLE)begin'])
self.ins_mark('close_end',['end'])#]]]
def init xaction(self):#((
c self.csvobj
sigdec lines=【
sigrgs_lines =[
busedsig [
cesig [
ncsig [
lastsig [
lenssig cvp.sig inst()
for sig in c.siglist:
if ('self'in sig.dict and ('nocompare'not in sig.dict_):
if not c.debug:
self.ins_mark('comp',['prj_compare('+sig.name+')'])
if 'bus'in sig.ctrl:
busedsig.append(sig)
if 'cycend'in sig.ctrl:
cesig.append(sig.name)
if (('sample_mode'in sig.dict and ('nochange'in sig.sample_mode)):
sig.ctrl.append('nochange')
sig.ctrl_val.append('')
if ('nochange'in sig.ctrl):
ncsig.append(sig.name)
if 'last'in sig.ctrl:
Lastsig.append(sig.name)
if 'maxlens'in sig.ctrl:
Lenssig sig
if 'sigonly'not in sig.ctrl:
if ('cycend'in sig.ctrl)or ('norand'in sig.ctrl):
sigdec_lines.append('bit [xxx_dec:'+sig.name.upper()+'_WD -1:0]'+sig.name+':')
else:
sigdec_lines.append('rand bit[xxx_dec:'+sig.name.upper()+'WD -1:0]'+sig.name+':')
sigrgs_line =''uvm_field_int('+sig.name+',UVM_ALL_ON|UVM_NOCOMPARE)'
if c.ctl mode=='packet':
if(sig.name !c.mask_name+'_h'and sig.name !c.mask_name+'t'and sig.name a c.mask_name+
hbubble'):
if (('nochange'in sig.ctrl)or ('at'in sig.dict)):
self.ins_mark('all_comp',[''prj_compare('+sig.name+')'])
elif(sig.name !c.mask_name+'_h'and sig.name !c.mask_name+'_t'and sig.name !c.
mask_name+'_hbubble'):
self.ins_mark('cyc_comp',[''prj_compare('+sig.name+')'])
#if ('nocompare'not in sig.dict_)and ('self'not in sig.dict and (('nochange'in
sig.ctrl)or ('at'in sig.dict)):
sigrgs_Line sigrgs_line[:-15]+')'
elif c.ctl mode=='cycle':
if ('nocompare'not in sig.dict_)and ('self'not in sig.dict )
sigrgs_line sigrgs _line[:-15]+')'
sigrgs Lines.append(sigrgs line)
self.ins_mark('sigdec',sigdec lines)
self.ins_mark('sigrgs',sigrgs_lines)
qdec_lines =[
qrgs_lines
comp lines=【
prnt lines [
bus3 Lines [
bus5 lines =[
els lines [
els2 lines =[
elssig =[
maskedsig [
for sig in c.siglist:
if ('sigonly'not in sig.ctrl)and ('nochange'not in sig.ctrl)and ('last'not in sig.ctrl)amd
('sop'not in sig.ctrl)and ('at'not in sig.dict and ('self'not in sig.dict and (sig.mamel
=c.mask name):
qrgs_lines.append('"uvm_field_queue_int('+sig.name+'q.UVH_ALL__NOCONPARE)')
if ('nocompare'not in sig.ctrl):
if c.ctl mode=='packet':
comp_lines.append(''prj_compare_queue('+sig.name+'q)')
if 'bus'in sig.ctrl:
maskedsig.append(sig)

 if bus'in sig.ctrl:
maskedsig.append(sig)
prnt_lines.append('printer.print_string("'+sig.name+'_q",prj_func:prj_print_queue("'+sig.
name+'q",'+sig.name+'g));'
qdec lines.append('rand bit['+sig.ctrl_val[sig.ctrl.index('bus')]+'-1:0]'+sig.name+'_q[s];' bus3_lines.append('bit [xxx dec:'+sig.name.upper()+'WD -1:0]vr_'+sig.name+';')
bus3_lines.append('bit['+sig.ctrl_val[sig.ctrl.index('bus')]+'-1:0]tmp_'+sig.name+'q[s];') bus3_lines.append('tmp_'+sig.name+'q this.'+sig.name+'q;')
bus5_lines.append('vr_cyc.'+sig.name+'vr_'+sig.name+';')
else:
qdec lines.append('rand bit[xxx dec:'+sig.name.upper()+'WD -1:0]'+sig.name+'q[s]:')
els_lines.append('this.'+sig.name+'q.push back(cyc q[i].'+sig.name+');')
els2_lines.append('vr_cyc.'+sig.name+'this.'+sig.name+'_q[i];'
elssig.append(sig)
elif ('at'in sig._dict_):
mline
mline2 =
for m in sig.at:
mline +'vr_cyc.'+m+'==1 66'
mline2 +'cyc_q[i].'+m+'==1
els_lines.append('if ('+mline2[:-4]+')this.'+sig.name+'cyc q[i].'+sig.name+';')
els2_lines.append('vr_cyc.'+sig.name+'=('+mline[-4]+')?this.'+sig.name+':surandom;')
self.ins mark('qdec',gdec lines)
self.ins_mark('qrgs',qrgs_lines)
self.ins_mark('comp',comp_lines)
self.ins_mark('prnt',prnt_lines)
self.ins mark('els',els_lines)
self.ins mark('els2',els2_lines)
self.ins mark('bus3',bus3_lines)
self.ins mark('bus5',bus5 _lines)
if c.ctl mode=='packet':
bus2_lines []#({
if c.direction=='msb':
bus2_lines.append('for (int j=0;j<BUS_WD;j++)begin')
else:
bus2_lines.append('for (int j=BUS WD-1;j>=0;j--)begin')
mline =
if c.mask mode=='both':
mline +=if(cyc_q[i].'+c.mask_name+'[BUS WD -1-j]1)'
elif c.mask mode=='tail':
mline +if((cyc_q[i].'+c.mask name+'[BUS _WD -1-j]=1)(i!=cyc_q.size-1))'
elif c.mask mode=='offset A':
mline +if((i!=cyc_q.size-1)II'
if c.direction=='msb':
mline +'j<=cyc_q[i].'+c.mask name+')'
else:
mline+='j>=(xxx_dec::'+c.data_name.upper()+'ND/8-1-cyc_qli】.'+c,mask_name+')'
elif c.mask mode=='offset B':
mline +if((i!=cyc_q.size-1)II (cyc_q[i].'+c.mask_name+'==0)'
if c.direction=='msb':
mline +='j<cyc_q[i].'+c.mask name+')'
else:
mline +='j>=(xxx_dec:'+c.data_name.upper()+'WD/8 -cyc_q[i].'+c.mask name+'))
mline +'this.'+c.data_name+'_q.push_back(cyc_q[i].'+c.data_name+'[xx_dec:'+c.data name.
upper()+WD-1-8*j-:8]);
bus2_lines.append(mline)
bus2 lines.append('end')
self.ins_mark('bus2',bus2_lines)#)}
if c.ctl mode=='packet':
bus4 lines [
if c.direction=='msb':
bus4_Lines.append('for(int j=BUS WD-1;j>=0;j--)begin')
else:
bus4_lines.append('for(int j=0;j<BUS_WD;j++)begin')
if c.mask mode=='offset_A':
mline ='if ((i!=this.cyc_num-1)II'
if c.direction=='msb':
mline +='j>=xxx_dec:'+c.data_name.upper()+'WD/8 -1 -vr_cyc.'+c.mask name
else:
mline +='j=vr_cyc.'+c.mask name
bus4_lines.append(mline+')begin')
elif c.mask mode='offset B':
mline 'if ((i!=this.cyc_num-1)II (vr_cyc.'+c.mask_name+'==0)II'
if c.direction=='msb':
mline +'j>=xxx_dec:'+c.data_name.upper()+'_WD/8 -vr_cyc.'+c.mask_name
else:
mline +='jsvr_cyc.'+c.mask name
bus4_lines.append(mline+')begin')
else:
bus4_lines.append('if (vr_cyc.'+c.mask name+'[j]==1)begin')
bus4 lines.append('if(tmp_'+c.data_name+'q.size==0)begin'uvm_error(get_type_mame().
spsprintf("tmp data_q is empty while unpack tr,i=0d,j=0d",i,j))end')
bus4 lines.append('
bus4_lines.append('
else vr'+c.data name+'[8*j +B]tmp'+c.data_name+'q.pop_front();'
end")
bus4_lines.append('else vr_'+c.data_name+'[8*j +8]surandom;'

 ous4 lines.append(else vr +c.data name+[8*]+8]surando
bus4 lines.append('end')
bus4_lines.append('vr_cyc.'+c.data name+'vr_'+c.data_name+';'
self.ins _mark('bus4',bus4 Lines)
cons1 lines []#{{
cons2 lines [
pack1 lines [
pack2_lines [
for s in c.siglist:
if 'sigonly'not in s.ctrl:
cons1 lines.append('extern constraint '+s.name+'cons;'
cons2 lines.append('constraint xxx xaction:'+s.name+'cons {'
if c.ctl mode=='packet'and c.mask mode=='both'and s.name==c.mask name b:
cons2_lines.append('this.'+s.name+'BUS WD;')
elif s.name==c.data name and c.ctl mode=='packet':
cons2_lines.append('this.'+s.name+'q.size lens;')
elif s in elssig and c.ctl mode=='packet':
cons2_lines.append('this.'+s.name+'q.size this.cyc_num;')
if 'pack'in s.dict_:
pline ="(
mline 'this.'+s.name+'={'
for member in re.split(",*",s.pack):
pline +="this."+member+',
mline +"this."+member+',
mline mline[:-2]+"}:"
if c.ctl mode=='cycle':
pline pline[:-2]+")this."+s.name+";"
else:
pline pline[-2]+"}cyc q[0]."+s.name+";"
pack2 Lines.append(mline)
packl lines.append(pline)
if 'force val'in s.dict
cons2_lines.append('this.'+s.name+'='+s.force_val+":')
cons2_lines.append('}')
if c.ctl mode=='packet':
cons1 lines.append('extern constraint lens_cons;'
consl_lines.append('extern constraint cyc_num_cons;'
cons2_lines.append('constraint xxx_xaction:lens_cons ('
cons2_lines.append('this.lens inside {[1:'+lenssig.ctrl_val[lenssig.ctrL.index('maxtens')]+']):
)
cons2_lines.append('}')
cons2_lines.append('constraint xxx_xaction:cyc_num_cons {'
if c.mask mode=='both':
bub ='+this.'+c.mask_name_b+')'
else:
bub =
if 'bus'in lenssig.ctrl:
cons2_lines.append('(this.Lens'+bub+'BUS_WD 0 -this.cyc_num ==(this.Lens'+bub+'/BUS WD cons2 lines.append('(this.Lens'+bub+'BUS_WD !0 -this.cyc_num ==(this.lens'+bub+'/
BUS WD +1;')
cons2_lines.append('solve this.lens before this.cyc_num;')
if c.mask mode=='both':
cons2 lines.append('solve this.'+c.mask_name_b+'before this.cyc_num;')
cons2_lines.append('}')
self.ins mark('cons2',cons2 lines)
self.ins_mark('cons1',consl lines)
self.ins_mark('pack2',pack2_lines)
self.ins_mark('packl',packl_lines)
mask1_lines []#(f{
mask2_lines [
mask3 lines [
mask4 lines [
mask5_lines [
mask6 lines [
mask7_lines=[门]
if c.ctl mode=='packet':
if c.mask mode=='both':
self.ins mark('post',[this.'+c.mask name h+'cyc q[e].'+c.mask name+':','this.'+c.
mask_name_t+=cyc_qls].'+c.mask name+";')
mask1 lines.append('if (i==0)begin')
mask2_lines.append('vr_cyc.'+c.mask name+'=\'1;'
mask3 lines.append('if (i==0)vr_cyc.'+c.mask name+'=this.'+c.mask mame h+':')
mask3_lines.append('if (i==this.cyc_num-1)vr_cyc.'+c.mask name+'this.'+c.mask_mame_t+':')
mask4 lines.append('int vr lens this.lens this.'+c.mask name b+':')
mask5 lines.append('this.'+c.mask name h+'a 0:"
mask6_lines.append('this.'+c.mask_name_t+'=\'1;')
mask6_lines.append('if (vr_lens\BUS WD =0)begin')
if c.direction='msb':
askl Lines.apoend('fortint i=BUs w .1:i>:i.-lhein'

 if c.direction=='msb':
maskl lines.append('for(int j=BUS WD -1;j>=0;j--)begin')
mask5_lines.append('for(int i=0;i<BUS WD this.'+c.mask name b+';i++)this.'+c.mask_name_h+
[]=1;
mask6_lines.append('for(int i=0;i<BUS WD vr_lensBUS_WD;i++)this.'+c.mask name_t+'[i]
=0;) else:
maskl_lines.append('for(int j=0;j<BUS WD;j++)begin')
mask5 lines.append('for(int i=this.'+c.mask name_b+';i<BUS WD;i++)this.'+c.mask_name_h+'[i]
=1;)
mask6_lines.append('for(int i=vr_lens*%BUS_WD;i<BUS_WD;i++)this.'+c.mask_name_t+'[i]0;
)
maskl lines.append(' if(cyc q[i].'+c.mask name+'[j]=0)this.'+c.mask_name_b+'++;')
mask1 lines.append('
else break;'
mask1_lines.append('end')
maskl lines.append('end')
mask6_lines.append('end')
mask7_lines.append('if(this.cyc num =1)begin')
mask7_lines.append('this.'+c.mask _name_t+'this.'+c.mask_name_h+'this.'+c.mask_name_t+';
)
mask7_lines.append('this.'+c.mask name h+'this.'+c.mask name_t+';')
mask7_lines.append('end')
elif c.mask mode=='tail':
maskl_lines.append('this.'+c.mask name+'=(i==cyc_q.size-1)?cyc_q[i].'+c.mask_name+':\'1;')
mask2_lines.append('vr_cyc.'+c.mask name+'(i==this.cyc num-1)?this.'+c.mask _name+':\'1;')
mask4 lines.append('this.'+c.mask name+'=\'1;')
mask4 lines.append('if(this.lens*BUS WD !=0)begin')
if c.direction=='msb':
mask4_lines.append('for(int i=0;i<BUS WD -this.lensBUS WD;i++)this.'+c.mask_name+'[i]
0;)
else:
mask4_lines.append('for(int i=this.Lens*BUS WD;i<BUS WD;i++)this.'+c.mask_name+'[i]0;
)
mask4_lines.append('end')
elif c.mask mode=='offset A':
mask2_lines.append('vr_cyc.'+c.mask name+'=(i==this.cyc_num-1)?this.'+c.mask_name+':
surandom;')
mask4 lines.append('this.'+c.mask name+'=\'1;')
mask4_lines.append('if(this.Lens*BUS WD !=0)begin')
mask4_lines.append('this.'+c.mask name+'this.lensBUS WD -1;')
mask4_lines.append('end')
elif c.mask mode=='offset_B':
mask2_lines.append('vr_cyc.'+c.mask name+'=(i==this.cyc_num-1)?this.'+c.mask_name+':
surandom;'
mask4_lines.append('this.'+c.mask name+'this.lens*BUS WD;')
self.ins mark('mask1',maskl lines)
self.ins mark('mask2',mask2 lines)
self.ins mark('mask3',mask3_lines)
self.ins mark('mask4',mask4 lines)
self.ins mark('mask5',mask5_lines)
self.ins mark('mask6',mask6 lines)
self.ins_mark('mask7',mask7_lines)#
self.ins mark('post',[this.lens this.'+c.data_name+'_q.size;']
for s in busedsig:
self.ins_mark('buswd','parameter BUS_WD xxx_dec::'+s.name.upper()+'_WD/'+s.ctrl_val[s.ctrl.
index('bus')]+';'])
nc1 lines [
nc2 lines [
nc3_lines [
for sname in ncsig:
ncl lines.append('this.'+sname+'cyc_q[0].'+sname+';'
nc2 lines.append('if(cyc_q[i].'+sname+'!this.'+sname+')prj_error(spsprintf("'+sname+'has
changed from %0d(cyc0)to %0d(cyc 0d)",this.'+sname+',cyc_q[i].'+sname+',i))')
nc3_lines.append('vr_cyc.'+sname+'=this.'+sname+';')
self.ins mark('nc1',ncl lines)
self.ins mark('nc2',nc2_lines)
self.ins_mark('nc3',nc3_lines)
lastl lines [
if c.ctl mode=='packet':
lastl_lines.append('vr_cyc.'+c.last_name+'(i =this.cyc_num -1);')
if ('sop name'in c.dict and (c.sop name):
Lastl_lines.append('vr_cyc.'+c.sop_name+'=(i =0);')
self.ins mark('last1',last1_lines)
#}}
def init harness(self):#{{
c self.csvobi
bpx1 lines [
bpx2_lines [

 px2 lines [
if c.bp mode=='bp':
bpx1 lines.append('assign bus.'+c.bp _name+'=1;')
bpx2 _lines.append('assign bus.'+c.bp name+'0;'
elif c.bp mode=='hs':
bpx1 lines.append('assign bus.'+c.rdy name+'=1;')
bpx2_lines.append('assign bus.'+c.rdy _name+'0;'
self.ins mark('bpx1',bpx1_lines)
self.ins mark('bpx2',bpx2_lines)#})}
def init rdy driver(self):#{{
c self.csvobj
drvmode lines [
drvmode_dict={'DRV_0':'"e','DRV_1':'八'1'，'DRV_RAND':'surandom','DRvX':'\'hx'} for m in drvmode dict:
drvmode_lines.append('prj dec:'+m+':begin')
drvmode_lines.append('this.bus.drv_rdy_cb.'+c.rdy _name+'<='+drvmode_dict[m]+';' drvmode lines.append('end')
self.ins mark('drvmode',drvmode_lines)
wvalid_lines [
wvalid_lines.append('if(this.bus.'+c.vld_name+')break;'
self.ins mark('wvalid',wvalid lines)
dready0 _lines [this.bus.drv_rdy _cb.'+c.rdy name+'<=rdy_tr.rdy;'
dreadyl_lines ['this.bus.drv_rdy_cb.'+c.rdy name+'<=0;']
self.ins mark('dready0',dready0 lines)
self.ins mark('dready1',dready1 lines)
#}}
