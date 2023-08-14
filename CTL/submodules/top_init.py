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


import os
import re
from datetime import datetime
from getpass import getuser

class tpl_file:
    def __init__(self, fdir, fname, sig_csvobj):
        self.tplfile = open(fdir + fname, "r")
        self.fname = fname
        self.topname = sig_csvobj.topname
        self.csvobj = sig_csvobj
        self.outlines = []
        self.infile()
        self.init_cb()
        self.filemode()
        self.cleanup()
        self.tplfile.close()

    def infile(self):
        for line in self.tplfile:
            self.outlines.append(line)

    def cleanup(self):
        swap_en = 0
        idx = 0
        tmplines = self.outlines.copy()
        for l in tmplines:
            if '/' in l and l.lstrip()[:2] == '/':
                if 'lcs mark begin' in l:
                    swap_en = 1
                elif 'lcs mark' in l:
                    swap_en = 0
                    del self.outlines[idx]
                else:
                    if swap_en:
                        del self.outlines[idx]
                    else:
                        idx += 1

        if os.path.splitext(self.fname)[1] == '.sv':
            mtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.outlines.insert(0, '//' + '*' * 79 + '\n')
            self.outlines.insert(1, '// Generated by genCTL script ver.1.0\n')
            self.outlines.insert(2, '// Author: ' + getuser() + '\n')
            self.outlines.insert(3, '// Created Time: ' + mtime + '\n')
            self.outlines.insert(4, '//' + '*' * 79 + '\n')

    def out(self, outdir):
        outfile = open(outdir + self.fname.replace('xxx', self.topname), "w")
        for line in self.outlines:
            outfile.write(line.replace('xxx', self.topname).replace('XXX', self.topname.upper()))
        outfile.close()

    def ins_mark(self, mark, ins_lines):
        total_idx = 0
        for line in self.outlines:
            if 'lcs mark' in line and mark == re.split(":", line)[-1][:-1]:
                indent = line.count('')
                index = total_idx + 1
                for ins_line in ins_lines:
                    self.outlines.insert(index, ' ' * indent + ins_line + '\n')
                    index += 1
                total_idx += 1

    def init_cb(self):
        self.cb_list = []
        self.cb_dict = {}
        for sig in self.csvobj.siglist:
            for cbname in sig.cb:
                if (cbname + ' cb') not in self.cb_list:
                    self.cb_list.append(cbname + ' cb')
                    self.cb_dict[cbname + ' cb'] = []
                self.cb_dict[cbname + ' cb'].append((sig.name, sig.cbmode[sig.cb.index(cbname)]))

    def filemode(self):
        if self.fname == 'xxx interface.sv':
            self.init_intf()
        elif self.fname == 'xxx dec.sv':
            self.init_dec()
        elif self.fname == 'xxx driver.sv':
            self.init_driver()
        elif self.fname == 'xxx rdy driver.sv':
            self.init_rdy_driver()
        elif self.fname == 'xxx monitor.sv':
            self.init_monitor()
        elif self.fname == 'xxx xaction.sv':
            self.init_xaction()
        elif self.fname == 'harness.sv':
            self.init_harness()

    def init_dec(self):
        wd_lines = []
        for sig in self.csvobj.siglist:
            wd_lines.append('parameter ' + sig.name.upper() + '_WD =' + str(sig.width) + ';')
        self.ins_mark('wd', wd_lines)

    def init_intf(self):
        # Implement init_intf() if needed
        pass

    def init_driver(self):
        # Implement init_driver() if needed
        pass

    def init_rdy_driver(self):
        # Implement init_rdy_driver() if needed
        pass

    def init_monitor(self):
        # Implement init_monitor() if needed
        pass

    def init_xaction(self):
        # Implement init_xaction() if needed
        pass

    def init_harness(self):
        # Implement init_harness() if needed
        pass


    def init_intf(self): #{{{
        c = self.csvobj
        dec_lines = []
        mon_link_lines = []
        drv_link_lines = []
        mon_bp_rdy_link_lines = []
        drv_bp_rdy_link_lines = []
        xz4_lines = []
        xz5_lines = []
    
        for sig in c.siglist:
            if 'celf' not in sig.dict:
                dec_lines.append('logic [' + sig.name.upper() + '_WD-1:0]' + sig.name + ';')
    
            if c.bp_mode == 'hs' and sig.name == c.rdy_name or \
               c.bp_mode == 'bp' and sig.name == c.bp_name:
                drv_bp_rdy_link_lines.append('assign or force bus.' + sig.name + ' = dut.' + sig.name + ';')
                mon_bp_rdy_link_lines.append('assign or force dut.' + sig.name + ' = bus.' + sig.name + ';')
            else:
                mon_link_lines.append('assign or force bus.' + sig.name + ' = dut.' + sig.name + ';')
                drv_link_lines.append('assign or force dut.' + sig.name + ' = bus.' + sig.name + ';')
    
            if (sig.name == c.vld_name) or \
               (sig.name == c.rdy_name) or \
               (c.bp_mode == 'bp' and sig.name == c.bp_name):
                xz4_lines.append("prj assert vld xz(clk, rst_n, " + sig.name + ")")
            else:
                xz4_lines.append("prj assert sign xz(clk, rst_n, " + c.vld_name + ", " + sig.name + ")")
    
            if c.bp_mode == 'hs' and sig.name != c.rdy_name:
                xz5_lines.append("prj_assert_sign_hold(clk, rst_n, " + c.vld_name + ", " + c.rdy_name + ", " + sig.name + ")")
    
        self.ins_mark('dec', dec_lines)
        self.ins_mark('xz4', xz4_lines)
        self.ins_mark('xz5', xz5_lines)
        self.ins_mark('mon link', mon_link_lines)
        self.ins_mark('drv link', drv_link_lines)
        self.ins_mark('mon bp rdy link', mon_bp_rdy_link_lines)
        self.ins_mark('drv bp rdy link', drv_bp_rdy_link_lines)
    
        for cbname in self.cb_list:
            cb_lines = []
            cb_lines.append('clocking ' + cbname + ' @(posedge clk);')
            cb_lines.append('    default input #INPUT_SKEW;')
            cb_lines.append('    default output #OUTPUT_SKEW;')
            for sig in self.cb_dict[cbname]:
                sigline = ''
                if 'in' in sig[1]:
                    sigline = sigline + 'input'
                elif 'out' in sig[1]:
                    sigline = sigline + 'output'
                sigline = sigline + ' ' + sig[0] + ';'
                cb_lines.append('    ' + sigline)
            cb_lines.append('endclocking')
            self.ins_mark('cb', cb_lines)
    
        bp_cb_lines = []
        bp_cb_lines.append('clocking drv_bp_cb @(posedge clk);')
        bp_cb_lines.append('    default input #INPUT_SKEW;')
        bp_cb_lines.append('    default output #OUTPUT_SKEW;')
        bp_cb_lines.append('    output ' + c.bp_name + ';')
        bp_cb_lines.append('endclocking')
        self.ins_mark('bp cb', bp_cb_lines)
    
        rdy_cb_lines = []
        rdy_cb_lines.append('clocking drv_rdy_cb @(posedge clk);')
        rdy_cb_lines.append('    default input #INPUT_SKEW;')
        rdy_cb_lines.append('    default output #OUTPUT_SKEW;')
        rdy_cb_lines.append('    input ' + c.vld_name + ';')
        rdy_cb_lines.append('    output ' + c.rdy_name + ';')
        rdy_cb_lines.append('endclocking')
        self.ins_mark('rdy cb', rdy_cb_lines)
    
        self.ins_mark('xz1', ['@(posedge clk) disable iff(!rst_n) !sisunknown(' + c.vld_name + ');'])
        
        if c.bp_mode == 'hs':
            self.ins_mark('xz3', ['@(posedge clk) disable iff(!rst_n) ' + c.rdy_name + ' <= 0.66' + c.vld_name + ' == 1 => $stable(sign);'])
    #}}}


    def init_driver(self): #{{{
        c = self.csvobj
        drvsig_lines = []
        drvidle_lines = []
    
        for sig in c.siglist:
            if 'drv' in sig.cb and 'out' in sig.cbmode[sig.cb.index('drv')]:
                if sig.idle_val is not None:
                    drvsig_lines.append('this.bus.drv_cb.' + sig.name + ' <= -' + sig.idle_val + ';')
                    drvidle_lines.append('this.bus.drv_cb.' + sig.name + ' = ' + sig.idle_val + ';')
                else:
                    drvsig_lines.append('this.bus.drv_cb.' + sig.name + ' <= cyc_q[i].' + sig.name + ';')
    
        self.ins_mark('drvsig', drvsig_lines)
        self.ins_mark('drvidle', drvidle_lines)
    
        if c.bp_mode == 'bp':
            bpl_lines = []
            bp2_lines = []
            bp3_lines = []
            bp4_lines = []
            bp5_lines = []
            bp6_lines = []
    
            bpl_lines.append('bit ' + c.bp_name + '_flag;')
            bpl_lines.append('int ' + c.bp_name + '_cnt;')
    
            bp2_lines.append('if (this.bus.mon_cb.' + c.bp_name + ' == 1) begin')
            mline = ''
            if c.ctl_mode == 'packet':
                mline = 'this.bus.mon_cb.' + c.last_name
            bp2_lines.append('    if (this.bus.mon_cb.' + c.vld_name + mline + ' == 1)')
            if c.ctl_mode == 'cycle':
                bp2_lines.append('    if (this.bus.mon_cb.' + c.vld_name + ' == 1)')
            bp2_lines.append('        ' + c.bp_name + '_cnt++;')
            bp2_lines.append('    if (' + c.bp_name + '_cnt > this.cfg.bp_delay)')
            bp2_lines.append('        this.' + c.bp_name + '_flag = 1;')
            bp2_lines.append('end')
            bp2_lines.append('else begin')
            bp2_lines.append('    if (this.' + c.bp_name + '_cnt > 0)')
            bp2_lines.append('        this.' + c.bp_name + '_cnt--;')
            bp2_lines.append('    else')
            bp2_lines.append('        this.' + c.bp_name + '_flag = 0;')
            bp2_lines.append('end')
    
            bp3_lines.append('if (this.in_fifo.is_empty == 0 && this.' + c.bp_name + '_flag == 0) begin')
    
            bp4_lines.append('else if (this.seq_item_port.has_do_available == 1 && this.' + c.bp_name + '_flag == 0) begin')
    
            bp5_lines.append('this.' + c.bp_name + '_flag = 0;')
            bp5_lines.append('this.' + c.bp_name + '_cnt = 0;')
    
            bp6_lines.append('while (this.cfg.dyn_rst_mode == prj_dec::IMMEDIATE && this.' + c.bp_name + '_flag == 1) begin')
            bp6_lines.append('    this.drive_idle();')
            bp6_lines.append('    @(this.bus.drv_cb);')
            bp6_lines.append('end')
    
            self.ins_mark('bpl', bpl_lines)
            self.ins_mark('bp2', bp2_lines)
            self.ins_mark('bp3', bp3_lines)
            self.ins_mark('bp4', bp4_lines)
            self.ins_mark('bp5', bp5_lines)
            self.ins_mark('bp6', bp6_lines)
    
        drvrdy_lines = []
    
        drvmust = []
        for sig in c.siglist:
            if 'drv must' in sig.ctrl:
                drvmust.append(sig.name)
    
        if drvmust:
            drvrdy_lines.append('while (1) begin')
            mline = ''
            for s in drvmust:
                mline += 'this.bus.drv_cb.' + s + ' == 1 && '
            drvrdy_lines.append('    ' + mline[:-4] + ') break;')
            drvrdy_lines.append('    else @(this.bus.drv_cb);')
            drvrdy_lines.append('end')
    
        self.ins_mark('drvrdy', drvrdy_lines)
    
        drvmode_lines = []
        drvmode_dict = {'DRV_0': '\'0', 'DRV_1': '\'1', 'DRV_RAND': 'surandom', 'DRV_X': '\'hx'}
    
        for m in drvmode_dict:
            drvmode_lines.append('prj_dec::' + m + ': begin')
            for sig in c.siglist:
                if 'drv' in sig.cb and 'out' in sig.cbmode[sig.cb.index('drv')] and sig.idle_val is None:
                    if (m == 'DRV_RAND') and (int(sig.width) > 32):
                        drvmode_lines.append('    this.bus.drv_cb.' + sig.name + ' = prj_func::get_nbits_rand(' +
                                             self.topname + '_dec::' + sig.name.upper() + '_WD);')
                    else:
                        drvmode_lines.append('    this.bus.drv_cb.' + sig.name + ' = ' + drvmode_dict[m] + ';')
            drvmode_lines.append('end')
    
        self.ins_mark('drvmode', drvmode_lines)
    #}}}


    def init_monitor(self): #{{{
        monmust_lines = []
        monsig_lines = []
    
        for sig in self.csvobj.siglist:
            if 'mon must' in sig.ctrl:
                monmust_lines.append(sig.name)
    
        monmust_lines.append('if (this.bus.mon_cb.' + self.csvobj.vld_name + ' == 1) this.is_working = 1:')
        monmust_lines.append('else if (cyc_q.size == 0) this.is_working = 0;')
    
        if monmust_lines:
            mline = 'if ('
            for s in monmust_lines:
                mline += 'this.bus.mon_cb.' + s + '==1 && '
            monmust_lines.append(mline[:-4] + ') begin')
        else:
            monmust_lines.append('if (0) begin')
    
        self.ins_mark('mon_must', monmust_lines)
        self.ins_mark('mon_must_end', ['end'])
    
        for sig in self.csvobj.siglist:
            if 'mon' in sig.cb and 'in' in sig.cbmode[sig.cb.index('mon')] and 'sigonly' not in sig.ctrl:
                monsig_lines.append('cyc_tr.' + sig.name + ' <= this.bus.mon_cb.' + sig.name + ';')
    
        self.ins_mark('mon_sig', monsig_lines)
    
        for sig in self.csvobj.siglist:
            if 'last' in sig.ctrl:
                self.ins_mark('close', ['if (this.bus.mon_cb.' + sig.name + ' == 1 && this.cfg.xaction_mode == prj_dec::CYCLE) begin'])
                self.ins_mark('close_end', ['end'])
    #}}}


    def init_xaction(self):
        c = self.csvobj
        sigdec_lines = []
        sigrgs_lines = []
        busedsig = []
        cesig = []
        ncsig = []
        lastsig = []
        Lenssig = []
        
        for sig in c.siglist:
            if 'self' in sig.dict and 'nocompare' not in sig.dict:
                if not c.debug:
                    self.ins_mark('comp', ["prj_compare(" + sig.name + ")"])
                if 'bus' in sig.ctrl:
                    busedsig.append(sig)
                if 'cycend' in sig.ctrl:
                    cesig.append(sig.name)
                if 'sample mode' in sig.dict and 'nochange' in sig.sample_mode:
                    sig.ctrl.append('nochange')
                    sig.ctrl_val.append('')
                if 'nochange' in sig.ctrl:
                    ncsig.append(sig.name)
                if 'last' in sig.ctrl:
                    lastsig.append(sig.name)
                if 'maxlens' in sig.ctrl:
                    Lenssig = sig
                    
                if 'sigonly' not in sig.ctrl:
                    if 'cycend' in sig.ctrl or 'norand' in sig.ctrl:
                        sigdec_lines.append(f'bit [xxx dec: {sig.name.upper()} WD -1: 0] {sig.name}:')
                    else:
                        sigdec_lines.append(f'rand bit [xxx dec: {sig.name.upper()} WD -1: 0] {sig.name}:')
                    
                sigrgs_line = f'uvm_field int {sig.name}, UVM_ALL NOCOMPARE'
                
                if c.ctl_mode == 'packet':
                    if sig.name != c.mask_name + 'h' and sig.name != c.mask_name + 't' and sig.name != c.mask_name + 'hbubble':
                        if 'nochange' in sig.ctrl or 'at' in sig.dict:
                            self.ins_mark('all_comp', ["prj_compare(" + sig.name + ")"])
                    elif sig.name != c.mask_name + 'h' and sig.name != c.mask_name + 't' and sig.name != c.mask_name + 'hbubble':
                        self.ins_mark('cyc_comp', ["prj_compare(" + sig.name + ")"])
                
                elif c.ctl_mode == 'cycle':
                    if 'nocompare' not in sig.dict and 'self' not in sig.dict:
                        sigrgs_line = sigrgs_line[:-15] + "')"
                
                sigrgs_lines.append(sigrgs_line)
                
        self.ins_mark('sigdec', sigdec_lines)
        self.ins_mark('sigrgs', sigrgs_lines)
        gdec_lines = []
        qrgs_lines = []
        comp_lines = []
        prnt_lines = []
        bus3_lines = []
        bus5_lines = []
        els_lines = []
        els2_lines = []
        elssig = []
        maskedsig = []
        
        for sig in c.siglist:
            if 'sigonly' not in sig.ctrl and 'nochange' not in sig.ctrl and 'last' not in sig.ctrl and 'sop' not in sig.ctrl and 'at' not in sig.dict and 'self' not in sig.dict:
                if sig.name != c.mask_name:
                    qrgs_lines.append(f'uvm_field queue {sig.name}_q, UVM_ALL ONUVM NOCOMPARE')
                    
                if 'nocompare' not in sig.ctrl:
                    if c.ctl_mode == 'packet':
                        comp_lines.append(f"prj_compare_queue({sig.name}_q)")
                    
                    if 'bus' in sig.ctrl:
                        maskedsig.append(sig)
                    
                    if 'bus' in sig.ctrl:
                        maskedsig.append(sig)
                    
                    prnt_lines.append(f'printer.print_string("{sig.name} q", prj.func: prj.print_queue("{sig.name} q", {sig.name}_g));')
                    
                    gdec_lines.append(f'rand bit[{sig.ctrl_val[sig.ctrl.index("bus")]} - 1: 0] {sig.name}_q[s];')
                    
                    bus3_lines.append(f'bit [xxx dec: {sig.name.upper()} WD -1: 0] vr_{sig.name};')
                    bus3_lines.append(f'bit[{sig.ctrl_val[sig.ctrl.index("bus")]} - 1: 0] tmp_{sig.name}_q[s];')
                    bus3_lines.append(f'tmp_{sig.name}_q this.{sig.name}_q;')
                    
                    bus5_lines.append(f'vr cyc.{sig.name} = vr_{sig.name};')
                    
                    gdec_lines.append(f'rand bit[xxx dec: {sig.name.upper()} WD -1: 0] {sig.name}_q[s]:')
                    
                    els_lines.append(f'this.{sig.name}_q.push_back(cyc_q[i].{sig.name});')
                    els2_lines.append(f'vr_cyc.{sig.name} = this.{sig.name}_q[i];')
                    elssig.append(sig)
                    
                elif 'at' in sig.dict:
                    mline = ""
                    mline2 = ""
                    for m in sig.at:
                        mline += f'vr_cyc.{m}==1 && '
                        mline2 += f'cyc_q[i].{m}=1 || '
                    
                    els_lines.append(f'if ({mline2[:-4]}) this.{sig.name} = cyc_q[i].{sig.name};')
                    els2_lines.append(f'vr_cyc.{sig.name} = ({mline[:-4]}) this.{sig.name} surandom;')
        
        self.ins_mark('qdec', qdec_lines)
        self.ins_mark('grgs', gdec_lines)
        self.ins_mark('comp', comp_lines)
        self.ins_mark('prnt', prnt_lines)
        self.ins_mark('els', els_lines)
        self.ins_mark('els2', els2_lines)
        self.ins_mark('bus3', bus3_lines)
        self.ins_mark('bus5', bus5_lines)
        # Continue with other sections...


        if c.ctl_mode == 'packet':
            bus2_lines = []  # {{
            if c.direction == 'msb':
                bus2_lines.append('for (int j = 0; j < BUS_WD; j++) begin')
            else:
                bus2_lines.append('for (int j = BUS_WD - 1; j >= 0; j--) begin')
            mline = ''
            
            if c.mask_mode == 'both':
                mline += f'if (cyc_q[i].{c.mask_name}[BUS_WD - 1 - j] == 1)'
            elif c.mask_mode == 'tail':
                mline += f'if ((cyc_q[i].{c.mask_name}[BUS_WD - 1 - j] == 1) || (i != cyc_q.size - 1))'
            elif c.mask_mode == 'offset A':
                mline += f'if ((i != cyc_q.size - 1) && (j <= cyc_q[i].{c.mask_name}))'
                
            if c.direction == 'msb':
                mline += f'j <= cyc_q[i].{c.mask_name}'
            else:
                mline += f'j >= (xxx_dec: {c.data_name.upper()}_WD/8 - 1 - cyc_q[i].{c.mask_name})'
                
            elif c.mask_mode == 'offset B':
                mline += f'if ((i != cyc_q.size - 1) && (cyc_q[i].{c.mask_name} == 0))'
                if c.direction == 'msb':
                    mline += f'j < cyc_q[i].{c.mask_name}'
                else:
                    mline += f'j >= (xxx_dec: {c.data_name.upper()}_WD/8 - cyc_q[i].{c.mask_name})'
            mline += f'this.{c.data_name}_q.push_back(cyc_q[i].{c.data_name}[xxx_dec: {c.data_name.upper()}_WD - 1 - 8*j -:8]);'
            bus2_lines.append(mline)
            bus2_lines.append('end')
            self.ins_mark('bus2', bus2_lines)
    
        if c.ctl_mode == 'packet':
            bus4_lines = []
            if c.direction == 'msb':
                bus4_lines.append('for (int j = BUS_WD - 1; j >= 0; j--) begin')
            else:
                bus4_lines.append('for (int j = 0; j < BUS_WD; j++) begin')
                
            if c.mask_mode == 'offset A':
                mline = f'if ((i != this.cyc_num - 1)'
                if c.direction == 'nsb':
                    mline += f' && (j >= xxx_dec: {c.data_name.upper()}_WD/8 - 1 - vr_cyc.{c.mask_name})'
                else:
                    mline += f' && (j <= vr_cyc.{c.mask_name})'
                bus4_lines.append(mline + ') begin')
                
            elif c.mask_mode == 'offset B':
                mline = f'if ((i != this.cyc_num - 1) && (vr_cyc.{c.mask_name} == 0)'
                if c.direction == 'msb':
                    mline += f' && (j >= xxx_dec: {c.data_name.upper()}_WD/8 - vr_cyc.{c.mask_name})'
                else:
                    mline += f' && (j <= vr_cyc.{c.mask_name})'
                bus4_lines.append(mline + ') begin')
                
            else:
                bus4_lines.append('if (vr_cyc.{}[j] == 1) begin'.format(c.mask_name))
                
            bus4_lines.append(' if (tmp_{}_q.size() == 0) begin'.format(c.data_name))
            bus4_lines.append('    uvm_error(get_type_name(), $spsprintf("tmp data q is empty while unpacking, i=%0d, j=%0d", i, j));')
            bus4_lines.append(' end')
            bus4_lines.append(' else')
            bus4_lines.append('    vr_{}[8*j +: 8] = tmp_{}_q.pop_front();'.format(c.data_name, c.data_name))
            bus4_lines.append(' end')
            bus4_lines.append(' else')
            bus4_lines.append('    vr_{}[8*j +: 8] = $urandom;'.format(c.data_name))
            bus4_lines.append('end')
            bus4_lines.append('vr_cyc.{} = vr_{};'.format(c.data_name, c.data_name))
            
            self.ins_mark('bus4', bus4_lines)

        cons1_lines = []
        cons2_lines = []
        packl_lines = []
        pack2_lines = []

        for s in c.siglist:
            if 'sigonly' not in s.ctrl:
                cons1_lines.append('extern constraint {}_cons;'.format(s.name))
                cons2_lines.append('constraint xxx xaction: {}_cons {{'.format(s.name))
                
                if c.ctl_mode == 'packet' and c.mask_mode == 'both' and s.name == c.mask_name:
                    cons2_lines.append('    this.{}[BUS_WD];'.format(s.name))
                elif s.name == c.data_name and c.ctl_mode == 'packet':
                    cons2_lines.append('    this.{}q.size() == lens;'.format(s.name))
                elif s in elssig and c.ctl_mode == 'packet':
                    cons2_lines.append('    this.{}q.size() == this.cyc_num;'.format(s.name))
                    
                if 'pack' in s.dict:
                    pline = '    this.{} = '.format(s.name)
                    for member in re.split(",*", s.pack):
                        pline += 'this.{} + '.format(member)
                    pline = pline[:-2] + ';'
                    
                    if c.ctl_mode == 'cycle':
                        pline = pline[:-1] + ';'
                    else:
                        pline = pline[:-1] + '; cyc_q[0].{} = '.format(s.name)
                    
                    pack2_lines.append(pline)
                    packl_lines.append(pline)
                    
                if 'force_val' in s.dict:
                    cons2_lines.append('    this.{} == {};'.format(s.name, s.force_val))
                
                cons2_lines.append('}')

        if c.ctl_mode == 'packet':
            cons1_lines.append('extern constraint lens_cons;')
            cons1_lines.append('extern constraint cyc_num_cons;')
            
            cons2_lines.append('constraint xxx xaction: lens_cons {')
            cons2_lines.append('    this.Lens inside {[1:{}]: 0};'.format(lenssig.ctrl_val[lenssig.ctrl.index('maxtens')]))
            cons2_lines.append('}')
            
            cons2_lines.append('constraint xxx xaction: cyc_num_cons {')
            if c.mask_mode == 'both':
                bub = ' + this.{}[BUS_WD]'.format(c.mask_name)
            else:
                bub = ''
            
            if 'bus' in lenssig.ctrl:
                cons2_lines.append('    (this.Lens{}[BUS_WD:0] == 0) inside {[0:this.cyc_num]} + 1;'.format(bub))
            cons2_lines.append('    solve this.Lens before this.cyc_num;')
            
            if c.mask_mode == 'both':
                cons2_lines.append('    solve this.{} before this.cyc_num;'.format(c.mask_name))
            
            cons2_lines.append('}')
        
        self.ins_mark('cons2', cons2_lines)
        self.ins_mark('cons1', cons1_lines)
        self.ins_mark('pack2', pack2_lines)
        self.ins_mark('packl', packl_lines)

        mask1_lines =[]#({
        mask2_lines =[]
        mask3_lines =[]
        mask4_lines =[]
        mask5_lines =[]
        mask6_lines =[]
        mask7_lines =[]

        if c.ctl_mode == 'packet':
            if c.mask_mode == 'both':
                self.ins_mark('post', 'this.' + c.mask_name + '_h = cyc_q[e].' + c.mask_name + ';', 'this.' + c.mask_name + '_t = cyc_q[$].' + c.mask_name + ';')
            mask1_lines.append('if (i == 0) begin')
            mask2_lines.append('vr_cyc.' + c.mask_name + ' = 1;')
            mask3_lines.append('if (i == 0) vr_cyc.' + c.mask_name + ' = this.' + c.mask_name + ';')
            mask3_lines.append('if (i == this.cyc_num - 1) vr_cyc.' + c.mask_name + ' = this.' + c.mask_name + '_t;')
            mask4_lines.append('int vr_lens = this.lens + this.' + c.mask_name + '_h;')
            mask5_lines.append('this.' + c.mask_name + '_h = 0;')
            mask6_lines.append('this.' + c.mask_name + '_t = 1;')
            mask6_lines.append('if (vr_lens >= BUS_WD) begin')
            if c.direction == 'msb':
                mask1_lines.append('for (int j = BUS_WD - 1; j >= 0; j--) begin')
                mask5_lines.append('for (int i = 0; i < BUS_WD; i++) this.' + c.mask_name + '_h[i] = 1;')
            else:
                mask1_lines.append('for (int j = 0; j < BUS_WD; j++) begin')
                mask5_lines.append('for (int i = this.' + c.mask_name + '_h; i < BUS_WD; i++) this.' + c.mask_name + '_h[i] = 1;')
            mask1_lines.append('if (cyc_q[i].' + c.mask_name + '[j] == 0) this.' + c.mask_name + '_h++;')
            mask1_lines.append('else break;')
            mask1_lines.append('end')
            mask1_lines.append('end')
            mask6_lines.append('end')
            mask7_lines.append('if (this.cyc_num == 1) begin')
            mask7_lines.append('    this.' + c.mask_name + '_t = this.' + c.mask_name + '_h;')
            mask7_lines.append('end')
        elif c.mask_mode == 'tail':
            mask1_lines.append('this.' + c.mask_name + ' = (i == cyc_q.size - 1) ? cyc_q[i].' + c.mask_name + ' : 1;')
            mask2_lines.append('vr_cyc.' + c.mask_name + ' = (i == this.cyc_num - 1) ? this.' + c.mask_name + ' : surandom;')
            mask4_lines.append('this.' + c.mask_name + ' = 1;')
            mask4_lines.append('if (this.lens > 0) begin')
            if c.direction == 'msb':
                mask4_lines.append('    for (int i = 0; i < BUS_WD - this.lens; i++) this.' + c.mask_name + '[i] = 0;')
            else:
                mask4_lines.append('    for (int i = this.lens; i < BUS_WD; i++) this.' + c.mask_name + '[i] = 0;')
            mask4_lines.append('end')
        elif c.mask_mode == 'offset A':
            mask2_lines.append('vr_cyc.' + c.mask_name + ' = (i == this.cyc_num - 1) ? this.' + c.mask_name + ' : surandom;')
            mask4_lines.append('this.' + c.mask_name + ' = 1;')
            mask4_lines.append('if (this.lens > 0) begin')
            mask4_lines.append('    this.' + c.mask_name + ' = this.lens * BUS_WD - 1;')
            mask4_lines.append('end')
        elif c.mask_mode == 'offset B':
            mask2_lines.append('vr_cyc.' + c.mask_name + ' = (i == this.cyc_num - 1) ? this.' + c.mask_name + ' : surandom;')
            mask4_lines.append('this.' + c.mask_name + ' = this.lens * BUS_WD;')
        
        self.ins_mark('maskl', mask1_lines)
        self.ins_mark('mask2', mask2_lines)
        self.ins_mark('mask3', mask3_lines)
        self.ins_mark('mask4', mask4_lines)
        self.ins_mark('mask5', mask5_lines)
        self.ins_mark('mask6', mask6_lines)
        self.ins_mark('mask7', mask7_lines)

        self.ins_mark('post', ['this.Lens = this.' + c.data_name + 'q.size;'])
        for s in busedsig:
            self.ins_mark('buswd', ['parameter BUS_WD = xxx dec: ' + s.name.upper() + 'WD/' + s.ctrl_val[s.ctrl.index('bus')] + ';'])
        
        nc1_lines = []
        nc2_lines = []
        nc3_lines = []
        
        for sname in ncsig:
            nc1_lines.append('this.' + sname + ' = cyc_q[0].' + sname + ';')
            nc2_lines.append('if (cyc_q[i].' + sname + ' != this.' + sname + ') prj_error(spsprintf("' + sname + ' has changed from %0d (cyc0) to %0d (cyc %0d)", this.' + sname + ', cyc_q[i].' + sname + ', i));')
            nc3_lines.append('vr_cyc.' + sname + ' = this.' + sname + ';')
        
        self.ins_mark('nc1', nc1_lines)
        self.ins_mark('nc2', nc2_lines)
        self.ins_mark('nc3', nc3_lines)
        
        lastl_lines = []
        
        if c.ctl_mode == 'packet':
            lastl_lines.append('vr_cyc.' + c.last_name + ' = (i == this.cyc_num - 1);')
        if 'sop_name' in c.dict and c.sop_name:
            lastl_lines.append('vr_cyc.' + c.sop_name + ' = (i == 0);')
        
        self.ins_mark('last1', lastl_lines)

    # Initialize harness
    def init_harness(self): #{{{
        c = self.csvobj
        bpx1_lines = []
        bpx2_lines = []
        
        if c.bp_mode == 'bp':
            bpx1_lines.append('assign bus.' + c.bp_name + ' = 1;')
            bpx2_lines.append('assign bus.' + c.bp_name + ' = 0;')
        elif c.bp_mode == 'hs':
            bpx1_lines.append('assign bus.' + c.rdy_name + ' = 1;')
            bpx2_lines.append('assign bus.' + c.rdy_name + ' = 0;')
        
        self.ins_mark('bpx1', bpx1_lines)
        self.ins_mark('bpx2', bpx2_lines)
    #}}
    
    # Initialize ready driver
    def init_rdy_driver(self): #{{{
        c = self.csvobj
        drvmode_lines = []
        drvmode_dict = {'DRV_0': '\'0', 'DRV_1': '\'1', 'DRV_RAND': 'surandom', 'DRV_.X': '\'hx'}
        
        for m in drvmode_dict:
            drvmode_lines.append('prj dec:: ' + m + ': begin')
            drvmode_lines.append('    this.bus.drv_rdy_cb.' + c.rdy_name + ' <= ' + drvmode_dict[m] + ';')
            drvmode_lines.append('end')
        
        wvalid_lines = []
        wvalid_lines.append('if (this.bus.' + c.vld_name + ') break;')
        
        dready0_lines = ['this.bus.drv_rdy_cb.' + c.rdy_name + ' <= rdy_tr.rdy;']
        dready1_lines = ['this.bus.drv_rdy_cb.' + c.rdy_name + ' <= 0;']
        
        self.ins_mark('drvmode', drvmode_lines)
        self.ins_mark('wvalid', wvalid_lines)
        self.ins_mark('dready0', dready0_lines)
        self.ins_mark('dready1', dready1_lines)
    #}}



