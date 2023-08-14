import re
import os
import copy
from datetime import datetime
from getpass import getuser
import csvparser_sig as cvp

def gen(sig_csvobj, tpl_dir, out_dir):
    os.popen('mkdir -p ' + out_dir + '/src')
    os.popen('mkdir -p ' + out_dir + '/unit_test')
    srcdir = tpl_dir + '/src/'
    src_lst = os.listdir(srcdir)
    unitdir = tpl_dir + '/unit_test/'
    unit_list = os.listdir(unitdir)
    tpl_file.top_cfg(sig_csvobj)
    
    for fname in src_lst:
        if os.path.isfile(srcdir + fname) and (os.path.splitext(srcdir + fname)[1] != '.swp') and (os.path.splitext(srcdir + fname)[1] != '.swo'):
            workfile = tpl_file(srcdir, fname, sig_csvobj)
            workfile.out(out_dir + '/src/')
            
    for fname in unit_list:
        if os.path.isfile(unitdir + fname) and (os.path.splitext(unitdir + fname)[1] != '.swp') and (os.path.splitext(unitdir + fname)[1] != '.swo'):
            workfile = tpl_file(unitdir, fname, sig_csvobj)
            workfile.out(out_dir + '/unit_test/')
            
    listf = tpl_file(tpl_dir + '/', 'xxx_utils.list', sig_csvobj)
    listf.out(out_dir + '/')


def top_cfg(c):
    if c.ctl_mode == 'packet':
        data = cvp.sig_inst()
        data.name = c.data
        data.wia.width = c.data_width
        data.ctrl.append('bus')
        data.ctrl_val.append('8')
        data.ctrl.append('maxlens')
        data.ctrl_val.append(c.maxlens)
        c.siglist.append(data)
        last = cvp.sig_inst()
        last.name = c.last_nar
        last.width = '1'
        last.ctrl = ['last']
        last.ctrl_val = ['']
        c.siglist.append(last)
        
        if ('sop_name' in c.__dict__) and c.sop_name:
            sop = cvp.sig_inst()
            sop.name = c.sop_name
            sop.width = '1'
            sop.ctrl_val = ['']
            c.siglist.append(sop)
            
        if c.mask_mode:
            mask = cvp.sig_inst()
            mask.name = c.mask_name
            mask.width = str(int(c.data_width) / 8)
            c.siglist.append(mask)
            
        elif c.mask_mode == 'offset_A' or c.mask_mode == 'offset_B':
            mask = cvp.sig_inst()
            mask.name = c.mask_name
            mask.width = str(bin(int(c.data_width) / 8).count('1') - 1)
            c.siglist.append(mask)
            mask_h = cvp.sig_inst()
            mask_h.name = c.mask_name + '_h'
            mask_h.width = str(int(c.data_width) / 8)
            mask_h.ctrl.append('norand')
            mask_h.ctrl_val.append('')
            c.siglist.append(mask_h)
            
            mask_t = cvp.sig_inst()
            mask_t.name = c.mask_name + '_t'
            mask_t.width = str(int(c.data_width) / 8)
            mask_t.self = '1'
            mask_t.ctrl.append('norand')
            mask_t.ctrl_val.append('')
            c.siglist.append(mask_t)
            
        startpos = cvp.sig_inst()
        startpos.name = c.mask_name + '_hbubble'
        startpos.width = str(int(c.data_width) / 8)
        startpos.self = '1'
        c.siglist.append(startpos)
        
        if c.bp_mode == 'bp cycle':
            c.bpcycle = True
            c.bp_mode = 'bp'
        
        if c.bp_mode == 'hs':
            vld = cvp.sig_inst()
            vld.name = c.vld_name
            vld.width = '1'
            vld.ctrl = ['mon must', 'sigonly']
            vld.ctrl_val = ['', '']
            vld.idle_val = '0'
            
            rdy = cvp.sig_inst()
            rdy.name = c.rdy_name
            rdy.width = '1'
            rdy.ctrl = ['drv must', 'mon must', 'sigonly']
            rdy.ctrl_val = ['', '', '']
            
            c.siglist.append(vld)
            c.siglist.append(rdy)
            
        elif c.bp_mode == 'bp':
            vld = cvp.sig_inst()
            vld.name = c.vld_name
            vld.width = '1'
            vld.ctrl = ['mon must', 'sigonly']
            vld.ctrl_val = ['', '']
            vld.idle_val = '0'
            
            bp = cvp.sig_inst()
            bp.name = c.bp_name
            bp.width = '1'
            bp.ctrl = ['drv must', 'sigonly']
            bp.ctrl_val = ['0', '']
            bp.idle_val = '0'
            
            c.siglist.append(vld)
            c.siglist.append(bp)
            
        for s in c.siglist:
            if 'pack' in s.__dict__:
                wd = 0
                for member in re.split(",", s.pack):
                    for si in c.siglist:
                        if si.name == member:
                            wd += int(si.width)
                s.width = wd
                
            if 'self' not in s.__dict__:
                s.cb.append('drv')
                s.cbmode.append('out')
                s.cb.append('mon')
                s.cbmode.append('in')
                
            if c.bp_mode == 'hs':
                if s.name == c.rdy_name:
                    s.cbmode[s.cb.index('drv')] = 'in'
            elif c.bp_mode == 'bp':
                if s.name == c.bp_name:
                    s.cbmode[s.cb.index('drv')] = 'in'
            
            if 'sample_mode' in s.__dict__ and ('@' in s.sample_mode):
                s.at = []
                for member in re.split("\*", s.sample_mode):
                    member = member.strip()
                    if member:
                        s.at.append(member)





class tpl file:
def init (self, fdir, fname, sig csvobj):
self. tplfile open(fdir+fname, "r")
self. fname fname
self. top name sig csvobj. top name
self. csvobj sig csvobj
self.outlines [
self.infile()
self.init cb()
self. filemode()
self. cleanup()
def infile(self):
for line in self. tplfile:
self. outlines append(line)

 for line in self. tplfile:
self. outlines. append(Line)
self.tplfile.close()#}]
def cleanup(self): #{f{
swap en =0
idx=0
tmplines copy. copy(self. outlines)
for l in tmplines:
if ('/' in l) and (l. lstrip()[:2]=='/'):
if ('lcs mark begin' in l):
swap en 1
elif ('lcs mark' in L):
swap_en =0
del self. outlines [idx]
else:
if swap en:
del self. outlines[idx]
else:
idx += 1
if (os. path. splitext(self. fname)[1]=='. sv'):
mtime datetime. now(). strftime("%Y-*m-*d H: M: s")
self.outlines.insert(0,
11*******************************
****************** n
self. outlines. insert(1,'// Generated by genCTL script ver.1.0\n')
self. outlines. insert(2, '/
Author: '+getuser()+'\n')
self.outlines. insert(3, '/
Created Time: '+mtime+'\n')
self. outlines. insert(4,
****************************
*\n)
def out(self,out dir): #{{{
outfile open(out dir+self. fname. replace('xxx', self. top name), "w")
for line in self.outlines:
outfile. write(line. replace('xxx', self. top name). replace('XXX', self. top name.upper()))
outfile. close()#
def ins mark(self,mark,ins_lines):#{{{
total idx =0
for line in self.outlines:
if ('lcs mark' in line) and (mark==re.split("\: *",line)[-1][: -1]):
indent line. count('')
index total idx+1
for ins line in ins lines:
self. outlines. insert(index, ''*indent+ins line+'\n')
index + 1
total idx += 1#}}}
def init cb(self):#{{{
self. cb list =[
for sig in self. csvobj.siglist:
for cbname in sig. cb:
if (cbname+' cb') not in self. cb list:
self. cb list. append(cbname+' cb')
self. dict [cbname+' cb'] =[
self. dict [cbname+'_cb']. append( (sig. name, sig. cbmode[sig. cb.index(cbname)]))#)))
def filemode(self): #{{{
if self. fname =='xxx interface. sv':
self.init intf()
elif self. fname = 'xxx dec. sv':
self. init dec)
elif self. fname =='xxx driver.sv':
self. init driver()
elif self. fname =='xxx rdy driver. sv':
self.init rdy driver()
elif self. fname = 'xxx monitor. sv':
self.init monitor()
elif self. fname =='xxx xaction. sv':
self. init xaction()
elif self. fname =='harness. sv':
self. init harness()#}}}
def init dec(self): #{{{
wd_lines =[
for sig in self. csvobj.siglist:
wd lines. append('parameter '+sig. name. upper()+' WD ='+str(sig. width)+';')
self. ins mark('wd', wd lines); #
def init intf(self): #{{{
c self. csvob
dec lines [
mon link lines [
drv link lines [
mon bp rdy link lines
drv bp rdy link lines [
xz4 lines =[
xz5 lines =[
for sig in self. csvobj.siglist:
if 'celf not in ein dict

 for sig in self. csvobj.siglist:
if 'self' not in sig. dict
dec lines. append('logic ['+sig. name. upper()+' WD-1: 0]'+sig. name+'; '
if c. bp mode=='hs' and sig. name==c. rdy name or c. bp mode=='bp' and sig. name==c. bp name:
drv bp rdy link lines. append(' assign or force bus. '+sig. name+' dut''+sig. name+';')
mon bp rdy link lines. append(' assign or force dut'''+sig. name+' bus.'+sig. name+';'
else
mon link lines. append(' assign or force bus. '+sig. name+' dut''+sig. name+';
drv link lines. append(' assign or force dut'''+sig. name+' bus.'+sig. name+';
if (sig. name = c. vld name) or (sig. name = c. rdy_name) or c. bp_mode ='bp' and sig. name==c. bp name):
xz4_lines. append(''prj assert vld xz(clk, rst n, '+sig. name+')')
else
xz4 lines. append(' 'prj assert sign xz(clk, rst n, '+c. vld name+', '+sig. name+')')
if c. bp mode=='hs' and sig. name!=c. rdy name:
xz5_lines. append(' 'prj_assert_sign_hold(clk, rst_n,'+c.vld_name+', '+c. rdy_name+','+sig.
name+' )')
self. ins mark('dec', dec lines)
self. ins mark('xz4', xz4 lines)
self. ins_mark('xz5', xz5_lines)
self. ins mark('mon link', mon link lines)
self.ins mark('drv link', drv link lines)
self.ins mark('mon bp rdy link', mon bp rdy link lines)
self. ins mark('drv bp _rdy _link', drv bp rdy_link lines)
for cbname in self. cb list:
cb lines [
cb lines. append('clocking '+cbname+' @(posedge clk);')
cb_lines. append(' default input #INPUT_SKEW;')
cb lines. append ( default output #OUTPUT SKEW: '
for sig in self. dict [cbname]: #local_vars[cbname]:
sigline
if 'in' in sig[1]:
sigline sigline+'input
elif 'out' in sig[1]:
sigline sigline+'output'
sigline = sigline+sig[0]+';
cb lines. append(sigline)
cb lines. append('endclocking\n')
self. ins mark('cb', cb lines)
bp cb lines [
bp cb lines. append('clocking drv bp cb @(posedge clk);')
bp cb lines. append(' default input #INPUT SKEW;')
bp_cb_ lines. append(' default output #OUTPUT SKEW; '
bp cb lines. append(' output '+c. bp name+';')
bp cb lines. append('endclocking\n')
self.ins mark('bp cb', bp cb lines)
rdy cb lines [
rdy cb lines. append('clocking drv rdy cb @(posedge clk);')
rdy cb lines. append(' default input #INPUT_SKEW;')
rdy cb Lines. append(' default output #OUTPUT SKEW;')
rdy cb lines. append(' input '+c. vld name+'; '
rdy cb lines. append(' output '+c. rdy name+'; '
rdy cb lines. append('endclocking\n')
self. ins mark('rdy cb', rdy cb lines)
self. ins mark( 'xz1', ['@(posedge clk) disable iff(! rst n) !sisunknown('+c. vld name+'):'])
# self.ins_mark('xz2',['@(posedge clk) disable iff(!rst_n || '+c.vld name+'!=1) !sisunknown(sign);
'])
if c. bp mode=='hs':
self. ins mark( 'xz3', ['@(posedge clk) disable iff(!rst n)'+c. rdy name+'=0 66'+c. vld name+
=== 1=> $stable(sign);'])#}}}
def init driver(self):#{{{
c= self. csvobj
drvsig lines [
drvidle lines [
for sig in self. csvobj.siglist:
if 'drv' in sig.cb:
if 'out' in sig. cbmode[sig. cb.index('drv')]:
if sig.idle val ! None:
drvsig lines. append('this. bus. drv cb. '+sig. name+'<=-'+sig. idle val+';')
drvidle_lines. append('this. bus. drv cb. '+sig. name+'='+sig. idle val+';')
else:
drvsig_lines.append('this.bus.drv_cb.'+sig.name+' <= cyc_q[i].'+sig.name+';')
self. ins mark('drvsig', drvsig lines)
self. ins mark('drvidle', drvidle lines)
if c. bp mode=='bp': #
bpl lines [
bp2 lines [
bp3 lines [
bp4 lines [
bp5 lines [
bp6_lines =[
bp1 lines. append('bit '+c. bp name+' flag:')

 bpl lines. append('bit '+c. bp name+' flag; '
bpl lines. append('int '+c. bp name+' cnt; '
bp2 lines. append('if(this. bus. mon cb. '+c. bp name+'== 1) begin')
if c. ctl mode=='packet':
mline
if 'bpcycle' not in c.dict
mline = 66 this. bus. mon cb. '+c. last name
bp2 lines. append(' if(this. bus. mon cb. '+c. vld name+mline+' == 1)'+c. bp name+' cnt ++;'
elif c. ctl mode=='cycle':
bp2 lines. append(' if(this. bus. mon cb. '+c. vld name+' == 1)'+c. bp name+' cnt ++;'
bp2_lines. append(' if('+c. bp name+' cnt > this. cfg. bp delay) this. '+c. bp name+' flag 1; '
bp2 lines. append('end')
bp2 lines. append('else begin')
bp2_lines.append(' if(this.'+c.bp name+'_cnt >0) this.'+c.bp_name+' cnt --;')
bp2 lines. append(' else this. '+c. bp name+' flag 0; '
bp2_lines. append('end')
bp3 lines.append('if(this.in fifo.is empty == 0 66 this.'+c.bp_name+' _flag == 0) begin')
bp4_lines. append('else if(this. seq item port. has do available = 1 &6 this.'+c. bp name+'flag==
0) begin')
bp5 lines. append( 'this. '+c. bp name+' flag 0; '
bp5 lines. append('this. '+c. bp_name+'cnt =0; '
bp6_lines. append('while(this. cfg.dyn_rst_mode = prj_dec: IMMEDIATE 66 this.'+c. bp_name+'_flag==
1)begin')
bp6_lines. append(' this. drive idle();')
bp6 lines. append(' @(this. bus. drv cb); '
bp6 lines. append('end')
self. ins mark('bp1', bp1 lines)
self. ins mark('bp2', bp2 lines)
self. ins mark('bp3', bp3 lines)
self. ins mark('bp4', bp4 lines)
self. ins mark('bp5', bp5 lines)
self. ins mark('bp6',bp6 lines)#}}]
drvrdy lines [
drvmust [
mline
for sig in self. csvobj.siglist:
if 'drv must' in sig. ctrl:
drvmust. append(sig. name)
if drvmust:
drvrdy lines. append ('while(1) begin')
mline = if('
for s in drvmust:
mline += ('this. bus. drv_cb.'+s+'==1 &&')
drvrdy lines. append (mline[ -4]+') break; '
drvrdy lines. append(' else @(this. bus. drv cb); '
drvrdy lines. append('end')
self. ins mark('drvrdy', drvrdy_lines)
drvmode lines [
drvmode dict ={'DRV_0': '\'0', 'DRV_1': '\'1', 'DRV_RAND': 'surandom', 'DRV_X': '\'hx'}
for m in drvmode dict:
drvmode lines. append('prj_dec:: '+m+': begin')
for sig in self. csvobj.siglist:
if 'drv' in sig.cb:
if 'out' in sig. cbmode[sig. cb. index( 'drv')] and (sig. idle val==None):
if (m =="DRV RAND") and (int(sig. width)>32):
drvmode lines. append(' this. bus. drv_cb. '+sig. name+'= prj_func: get nbits rand('+self.
top name+' dec: '+sig. name.upper()+'WD);')
else:
drvmode_lines. append(' this. bus.drv_cb.'+sig. name+'='+drvmode dict[m]+'; '
drvmode lines. append('end')
self. ins_ mark('drvmode',drvmode_lines)#}}
def init monitor(self): #{{
monmust lines [
monmust [
for sig in self. csvobj.siglist:
if 'mon must' in sig. ctrl:
monmust. append(sig. name)
monmust lines. append('if (this. bus. mon cb. '+self. csvobj. vld name+'== 1) this. is working 1:') monmust lines. append('else if(cyc q. size =0) this. is working 0;')
if monmust:
mline ='if(
for s in monmust:
mline +=('this. bus. mon cb. '+s+'==1 66)
monmust lines. append(mline[: -4]+') begin')
else:
monmust lines. append('if(0) begin')
self. ins mark('mon must', monmust lines)
self. ins mark('mon must end', ['end'])

 self. ins mark('mon must end', ['end
mon sig lines [
for sig in self. csvobj.siglist:
if 'mon' in sig. cb:
if ('in' in sig. cbmode[sig. cb. index('mon')]) and ('sigonly' not in sig. ctrl):
mon sig lines. append('cyc tr. '+sig. name+' this. bus. mon_cb.'+sig.name+';')
self.ins_mark('mon_sig',mon_sig_lines)
for sig in self. csvobj.siglist:
if 'last' in sig.ctrl:
self.ins mark('close', ['if (this. bus. mon cb. '+sig. name+'== 1 this. cfg.xaction mode=
prj dec: CYCLE) begin'])
self. ins mark('close end', ['end'])))
def init xaction(self): #((
c self. csvobj
sigdec lines [
sigrgs lines [
busedsig [
cesig [
ncsig [
lastsig =[
Lenssig cvp. sig inst()
for sig in c.siglist:
if ('self' in sig. dict and ('nocompare' not in sig. dict )
if not c.debug:
self. ins_mark('comp', [''prj_compare('+sig.name+')'])
if 'bus' in sig.ctrl:
busedsig. append(sig)
if 'cycend' in sig. ctrl:
cesig. append(sig. name)
if (('sample mode' in sig. dict and ('nochange' in sig. sample_mode)):
sig. ctrl. append('nochange')
sig. ctrl val. append('')
if ('nochange' in sig. ctrl):
ncsig. append(sig. name)
if 'last' in sig.ctrl:
Lastsig. append(sig. name)
if 'maxlens' in sig. ctrl:
Lenssig sig
if 'sigonly' not in sig.ctrl:
if ('cycend' in sig. ctrl) or ('norand' in sig.ctrl):
sigdec_lines. append('bit [xxx dec: '+sig. name. upper()+'WD -1: 0] '+sig. name+':')
else:
sigdec lines. append( 'rand bit [xxx dec: '+sig. name. upper()+' WD -1: 0] '+sig. name+':')
sigrgs_line =''uvm_field int('+sig. name+', UVM ALL NOCOMPARE)
if c. ctl mode=='packet':
if(sig. name ! c. mask_name+'h' and sig. name ! c. mask name+'t' and sig. name a c. mask name+ hbubble'): if (('nochange' in sig. ctrl) or ('at' in sig. dict ))
self. ins_mark('all_comp',['prj_compare('+sig.name+')'])
elif(sig. name ! c. mask name+'h' and sig. name ! c. mask name+'t' and sig. name c.
mask name+' hbubble'):
self. ins mark('cyc comp', [''prj_compare('+sig. name+')'])
#if ('nocompare' not in sig. dict_) and ('self' not in sig. dict and (('nochange' in
sig. ctrl) or ('at' in sig. dict ))
sigrgs line sigrgs Line[: -15]+')
elif c. ctl mode=='cycle':
if ('nocompare' not in sig. dict_) and ('self' not in sig._dict_):
sigrgs line sigrgs line[: -15]+')
sigrgs lines. append(sigrgs line)
self.ins mark('sigdec', sigdec lines)
self. ins mark('sigrgs', sigrgs lines)
gdec lines [
qrgs_lines [
comp lines [
prnt lines [
bus3 lines =[
bus5 lines [
els lines =[
els2 lines [
elssig [
maskedsig [
for sig in c.siglist:
if ('sigonly' not in sig.ctrl) and ('nochange' not in sig.ctrl) and ('last' not in sig.ctrl) and ('sop' not in sig.ctrl) and ('at' not in sig. dict and ('self' not in sig. dict_) and (sig.mame! =c. mask name):
qrgs Lines. append(' uvm field queue int('+sig. name+'q. UVH ALL ONUV NOCONPARE)")
if ('nocompare' not in sig. ctrl):
if c. ctl mode=='packet':
comp_lines.append(''prj_compare_queue('+sig. name+'_q)')
if 'bus' in sig. ctrl:
maskedsig. append(sig)

 if 'bus' in sig.ctrl:
maskedsig. append(sig)
prnt lines. append( 'printer. print string("'+sig. name+' q", prj func: prj print queue("'+sig.
name+' q",'+sig. name+'g)); '
qdec lines. append('rand bit['+sig. ctrl val[sig. ctrl. index( 'bus')]+'-1: 0] '+sig. name+' q[s]; ' bus3 lines, append('bit [xxx dec: '+sig. name. upper()+' WD -1: 0] vr '+sig. name+';')
bus3 lines. append('bit['+sig. ctrl val[sig. ctrl. index('bus')]+'-1: 0] tmp '+sig. name+'q[s]; ' bus3 lines. append('tmp '+sig. name+' q this. '+sig. name+' q;')
bus5 lines. append('vr cyc. '+sig. name+'= vr '+sig. name+';')
else:
gdec lines. append( 'rand bit[xxx dec: '+sig. name. upper()+'WD -1: 0] '+sig. name+' q[s]: '
els lines. append('this. '+sig. name+' q. push back(cyc q[i]. '+sig. name+'); '
els2_lines.append('vr_cyc. '+sig.name+' = this. '+sig.name+'_q[i];')
elssig. append(sig)
elif ('at' in sig. dict )
mline
mline2 =
for m in sig.at:
mline += 'vr_cyc. '+m+'==1 6'
mline2 += 'cyc_q[i].'+m+'=1 ||
els lines.append('if ('+mline2(: -4]+') this.'+sig.name+' = cyc q(i].'+sig.name+';')
els2 lines. append('vr cyc.'+sig. name+'= ('+mline[: -4]+') this. '+sig. name+' surandom; '
self. ins mark('qdec', qdec Lines)
self. ins mark('grgs', grgs lines)
self. ins mark( 'comp'. comp lines
self. ins mark('prnt', prnt lines)
self. ins mark('els', els lines)
self. ins mark('els2', els2 lines)
self. ins mark('bus3', bus3 lines)
self.ins mark('bus5', bus5 lines)
if c. ctl mode=='packet':
bus2 lines []#{{
if c. direction=='msb':
bus2 lines. append('for (int j=0; j<BUS WD; j++) begin')
else:
bus2_lines. append('for (int j=BUS WD-1; j>=0; j--) begin')
mline ='
if c. mask mode=='both':
mline +='if(cyc q[i]. '+c. mask name+' [BUS WD -1-j] = 1)'
elif c. mask mode=='tail':
mline += ' if((cyc_q[i]. '+c.mask_name+'[BUS_WD -1-j] = 1) || (i!=cyc_q.size-1) ) '
elif c. mask mode=='offset A':
mline += if((i!=cyc_q. size-1)I'
if c. direction=='msb':
mline + 'j<=cyc_q[i]. '+c. mask name+')'
else:
mline + 'j>=(xxx dec: '+c. data name. upper()+' WD/8 -1 -cyc q[i]. '+c. mask name+'))
elif c. mask mode=='offset B':
mline += if((i!=cyc_q. size-1) (cyc_q[i]. '+c. mask name+'==0)
if c. direction=='msb':
mline +='j<cyc q[i]. '+c. mask_name+')
else:
mline + 'j>=(xxx dec: '+c. data name. upper()+' WD/8 -cyc q[i]. '+c. mask name+'))
mline + 'this. '+c. data name+'q. push back(cyc q[i]. '+c. data name+' [xx dec: '+c. data name.
upper()+'_WD -1 -8*j -:8]);'
bus2 lines. append(mline)
bus2 lines. append('end')
self. ins mark( 'bus2', bus2 lines))
if c. ctl mode=='packet':
bus4 lines =[
if c. direction=='msb':
bus4 lines. append('for(int j=BUS WD-1; j>=0; j--) begin')
else:
bus4_lines. append('for(int j=0; j<BUS_WD; j++) begin')
if c. mask mode=='offset A':
mline 'if ((i!=this. cyc num-1)
if c. direction=='nsb':
mline +='j>=xxx dec: '+c. data name. upper()+' WD/8 -1 -vr cyc.'+c.mask name
else:
mline + 'js=vr cyc. '+c.mask name
bus4 lines. append(mline+') begin')
elif c. mask mode='offset B':
mline 'if ((i!=this. cyc num-1)(vr_cyc. '+c. mask name+'==0)
if c.direction=='msb':
mline + 'j>=xxx dec: '+c. data name. upper()+'WD/8 -vr_cyc. '+c.mask_name
else:
mline + 'jsvr cyc. '+c. mask name
bus4 lines. append(mline+') begin')
else:
bus4 lines. append(' if (vr cyc. '+c. mask name+'[j]==1) begin')
bus4 lines. append(' if(tmp '+c. data name+' q. size==0) begin' uvn error(get type mame().
spsprintf("tmp data q is empty while unpack tr, i=0d, j=0d", i, j))end')
bus4 lines.append(' else vr_'+c.data name+'[8*j +:8] = tmp '+c.data name+' q.pop front();')
bus4 lines. append(' end')
bus4 lines. append(' else vr_'+c. data name+'[8*j + 8] surandom:')
wed linee)

 bus4 lines. append(' else vr '+c. data name+'[8*j + 8] surandom;')
bus4 lines. append('end')
bus4 lines. append('vr cyc. '+c. data name+' vr '+c. data name+'; '
self. ins mark('bus4', bus4 Lines)
consl lines = []#{{{
cons2 lines [
packl lines [
pack2_lines =[
for s in c.siglist:
if 'sigonly' not in s.ctrl:
cons1 lines. append('extern constraint '+s. name+' cons:')
cons2 lines, append('constraint xxx xaction: '+s. name+' cons {'
if c. ctl mode=='packet' and c. mask mode=='both' and s. name==c. mask name b:
cons2 lines. append(' this. '+s. name+' BUS WD;')
elif s. name==c. data name and c. ctl mode=='packet':
cons2 lines. append(' this. '+s. name+' q. size lens;')
elif s in elssig and c. ctl mode=='packet':
cons2_lines. append(' this. '+s. name+'q. size this. cyc num; '
if 'pack' in s. dict
pline ="
mline 'this. '+s. name+' =
for member in re. split(",*",s.pack):
pline + "this. "+member+'
mline + "this."+member+',
mline mline[: -2]+"};"
if c. ctl mode==' cycle':
pline pline[: -2]+") this. "+s. name+";"
else:
pline pline[: -2]+"} cyc q[0]. "+s. name+":"
pack2 _lines. append(mline)
packl lines. append(pline)
if 'force val' in s. dict
cons2 lines. append(' this. '+s. name+'=='+s. force val+':')
cons2 lines. append('}')
if c. ctl mode=='packet':
cons1 lines. append('extern constraint lens cons;')
cons1 lines. append('extern constraint cyc num_cons; '
cons2 lines. append('constraint xxx xaction: lens cons ('
cons2_lines. append(' this. Lens inside {[1: '+lenssig. ctrl val[Lenssig. ctrL.index( 'maxtens')]+']):
')
cons2 lines. append('}')
cons2 lines. append('constraint xxx xaction: cyc num cons
if c. mask mode=='both':
bub ='+this. '+c. mask name b+')'
else:
bub = ')'
if 'bus' in lenssig, ctrl:
cons2 lines. append(' (this. Lens'+bub+'BUS WD 0 - this. cyc num ==(this. Lens'+bub+'/BUS WD
')
cons2 lines. append(' (this. lens'+bub+'BUS WD ! 0 - this. cyc num==(this. lens'+bub+'/
BUS WD +1;')
cons2 Lines. append('solve this. lens before this. cyc num;')
if c. mask mode=='both':
cons2 lines. append( 'solve this. '+c.mask name b+' before this. cyc num;')
cons2 lines. append('}')
self. ins mark('cons2', cons2 lines)
self. ins mark('cons1', consl lines)
self. ins mark('pack2', pack2 lines)
self. ins mark('packl', packl lines)#
maskl lines =[]#({
mask2 lines [
mask3 lines [
mask4 lines [
mask5 lines [
mask6 lines [
mask7 lines [
if c.ctl mode=='packet':
if c. mask mode=='both':
self. ins mark('post', this. '+c. mask name h+' cyc q[e]. '+c. mask name+':', 'this.'+c.
mask name t+' = cyc q[$]. '+c.mask name+'; '])
maskl lines. append('if (i==0) begin')
mask2 lines. append('vr cyc. '+c. mask name+'=\'1;')
mask3 lines. append( 'if (i==0) vr cvc. +c. mask name+'= this. +c. mask:
mask3_lines. append('if(i==this.cyc num-1) vr_cyc.'+c.mask name+'= this. '+c.mask mame t+';')
mask4 lines. append('int vr lens = this.lens + this. '+c.mask name b+';')
mask5 lines. append('this.'+c.mask mame h+'= 0:')
nask6 lines. append('this. '+c. mask name t+'=\'1:'
mask6 lines. append('if(vr lensBUs ho = beoin')
if c.direction='msb':
askl lines annendt'
forlint i=BUs w -1: 1>0: 1--beoin'
 f c. direction=='msb':
mask1 lines. append(' for(int j=BUS WD -1; j>=0; j--)begin')
mask5_lines.append('for(int i=0; i<BUS_WD this.'+c. mask_name_b+';i++) this.'+c.mask_name_h+
[i]=1;')
mask6 lines.append(' for(int i=0; i<BUS WD - vr_lensBUS WD; i++) this.'+c.mask_name_t+'[il
=0;') else:
maskl lines. append(' for(int j=0; j<BUS WD; j++)begin')
mask5 lines. append('for(int i=this. '+c. mask name_b+'; i<BUS WD; i++) this.'+c. mask name h+'[i]
1;')
mask6_lines. append(' for(int i=vr_lens*%BUS _WD; i<BUS WD; i++) this. '+c. mask name_t+'[i] =0;
')
mask1 lines. append('
if(cyc q[i]. '+c. mask name+'[j] = 0) this. '+c. mask _name_b+'++;')
mask1 Lines. append('
else break; '
mask1 lines. append('end')
mask1 lines. append('end')
mask6 Lines. append('end')
mask7_lines. append('if(this. cyc_num == 1) begin')
mask7_lines. append(' this. '+c. mask name t+' this. '+c. mask name_h+' this.'+c. mask_name_t+';
')
mask7 lines. append(' this. '+c. mask name h+' this. '+c. mask name_t+';')
mask7 lines. append('end')
elif c. mask mode=='tail':
maskl lines. append 'this. '+c. mask name+' =(i==cyc q. size-1) cyc q[i]. '+c. mask name+' \'1;')
mask2_lines.append('vr_cyc. '+c. mask name+'= (i==this. cyc num-1)? this. '+c. mask_name+' \'1;')
mask4 lines. append( 'this. '+c. mask name+'=\'1;')
mask4 lines. append('if(this. lensBUS WD !=0) begin')
if c.direction=='msb':
mask4_lines.append(' for(int i=0; i<BUS WD -this. lensBUS WD; i++) this. '+c. mask name+'[i]
0;')
else:
mask4_lines. append(' for(int i=this. lens*BUS WD; i<BUS WD; i++) this.'+c. mask name+'[i] 0;
')
mask4 lines. append('end')
elif c. mask mode=='offset A':
mask2_lines. append('vr_cyc. '+c. mask name+' (i==this. cyc num-1)? this.'+c. mask_name+':
surandom;')
mask4 lines. append ('this. '+c. mask name+'=\'1;')
mask4 lines. append ('if(this. WD !=0) begin')
mask4 lines. append(' this. '+c. mask name+' this. lens*%BUS_WD -1;')
mask4 lines. append('end')
elif c. mask mode=='offset B':
mask2_lines. append('vr_cyc. '+c. mask name+'= (i==this. cyc_num-1)? this.'+c. mask_name+':
surandom;')
mask4 lines. append( 'this. '+c. mask name+' this. lensBUS WD;')
self. ins mark('maskl', maskl lines)
self. ins mark('mask2', mask2 lines)
self. ins mark('mask3', mask3 lines)
self. ins mark('mask4',mask4 lines)
self. ins mark('mask5', mask5 lines)
self. ins mark('mask6', mask6 lines)
self.ins_mark('mask7',mask7_lines)#}}}
self. ins mark('post', [ this. Lens this. '+c. data name+'q.size; ']
for s in busedsig:
self. ins mark('buswd', ['parameter BUS _WD xxx dec: '+s. name.upper()+'WD/'+s. ctrl val[s. ctrl.
index('bus')]+';'])
nc1 lines [
nc2 lines [
nc3 lines [
for sname in ncsig:
ncl lines. append('this. '+sname+' cyc q[0]. '+sname+'; '
nc2 Lines. append('if(cyc q[i]. '+sname+' ! this. '+sname+') prj error(spsprintf("'+sname+'has
changed from 0d(cyc0) to 0d(cyc %0d)",this.'+sname+', cyc_q[i].'+sname+', i))')
nc3 lines. append('vr cyc. '+sname+' this.'+sname+';')
self. ins mark('nc1', ncl lines)
self. ins mark('nc2', nc2 lines)
self. ins _mark('nc3', nc3 lines)
lastl lines [
if c.ctl mode=='packet':
lastl lines. append('vr cyc. '+c. last name+'= (i = this. cyc num -1); '
if ('sop name' in c. dict and (c. sop name):
Lastl lines. append('vr_cyc. '+c. sop _name+'=(i = 0);')
self. ins mark('last1', Last1 lines)
#
def init harness(self): #{{{
c self. csvobj
bpx1 lines [
bpx2_lines [
 px2_lines [
if c. bp mode=='bp':
bpx1 lines. append('assign bus. '+c. bp name+'= 1;')
bpx2 lines. append( 'assign bus. '+c. bp name+' 0;')
elif c. bp mode=='hs':
bpx1 lines. append('assign bus. '+c. rdy name+'= 1; '
bpx2_lines. append( 'assign bus. '+c. rdy _name+'= 0; '
self. ins mark('bpx1', bpx1 lines)
self. ins mark('bpx2',bpx2_lines)#}]
def init rdy driver(self): #{{{
c self. csvobj
drvmode lines [
drvmode dict {'DRV_0': '\'0', 'DRV_1': '\'1', 'DRV_RAND': 'surandom', 'DRV_.X': '\'hx'} for m in drvmode dict:
drvmode lines. append('prj dec:: '+m+': begin')
drvmode_lines. append(' this. bus.drv_rdy_cb. '+c. rdy name+'<='+drvmode_dict[m]+'; '
drvmode lines. append('end')
self. ins mark('drvmode', drvmode lines)
wvalid lines [
wvalid lines. append('if(this. bus. '+c. vld name+') break; '
self. ins mark('wvalid', wvalid lines)
dready0_lines ['this. bus.drv_rdy cb. '+c. rdy name+'<= rdy_tr.rdy; '
dreadyl lines ['this. bus. drv_rdy_cb. '+c. rdy name+'<= 0; '
self. ins mark('dready0', dready0_lines)
self. ins mark('dready1', dready1_lines)
#}}
