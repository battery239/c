!/usr/bin/env python
coding=utf-8
from submodules import csvparser_sig
from submodules import top init
import os
import sys
import getopt
class genCTL_top_pkg():
def
init_(self):
self.csvpath=''
self.template_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]+'/../../utils/'
self.output_dir = os.path.split(os.path.abspath(sys.argv[0]) )[0]+'/. ./. ./utils/'
def main(self):
if not self.csvpath:
print 'ERROR: config file not found!'
sys.exit()
csv = csvparser_sig.sig_csvobj(self.csvpath)
self.output_dir += csv.top_name+'_utils'
if not self.output_dir:
print 'ERROR: output dir not specified!'
sys.exit()
#csv.debug = True
if csv.ctl_mode=='packet' and csv.bp_mode=='hs' :
self.template _dir += 'pkt_rdy_template'
elif csv.ctl_mode=='packet' and 'bp' in csv.bp_mode:
self.template_dir += 'pkt_bp_template'
elif csv.ctl_mode=='cycle' and csv.bp_mode=='hs' :
self.template_dir += 'cycle_rdy_template'
elif csv.ctl_mode=='cycle' and 'bp' in csv.bp_mode:
self.template_dir += 'cycle_bp_template'
top_init.gen(csv, self.template_dir, self.output_dir)
if
name
main
run_pkg = genCTL_top_pkg()
try:
opts,args = getopt.getopt(sys.argv[1: ], 'f:o: ')
for opt,arg in opts:
if opt=='-f' :
run_pkg.csvpath = str(arg)
elif opt=='-o':
run_pkg.output_dir = str(arg)+'/'
except getopt.GetoptError:
print "Argument error, program terminated"
sys.exit()
run_pkg.main()
os.popen('mv '+run_pkg.csvpath+' '+run_pkg.output_dir)
print "program finished, output dir: "+run_pkg.output_dir
