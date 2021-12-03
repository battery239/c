
#! /usr/bin/env perl

use Cwd;
my @ctls = `ls`;

for my $ctl(@ctls) {
  chomp($ctl);
  next if(!($ctl =~ /(\w+)_utils/));
  $ctl_name=$1;

  open(FD,"<$ctl/src/${ctl_name}_dec.sv") or die "";
  @dec_lines =<FD>;
  open(FD,"<$ctl/src/${ctl_name}_interface.sv") or die ""; 
  @lines= <FD>;
  open(FD,">$ctl/src/${ctl_name}_covergroup.sv") or die ""; 
  print FD "covergroup ${ctl_name}_covergroup with function sample(${ctl_name}_xaction tr);\n";
  print FD " option.per_instance = 1;\n";
  for($i=0;$i<=$#lines;$i++) {
    if($lines[$i] =~ /logic *\[.+\] *(\w+)/) {
      $signal = $1;
      for $dec_line(@dec_Lines) {
        if($dec_line =~ / \U${signal}\E_WD *= (\d+)/) {
          $signal_wd = $1;
          print "aaa ${signal} aa$1bb $dec_line\n";
          last;
        }
      }
      print FD " ${signal}_cp: coverpoint tr.${signal} {\n";
      if($signal_wd < 8) {
        print FD"    bins b[] = {[0:'1]};\n";
      }
      else {
        print FD"    bins min[] = {0};\n";
        print FD"    bins max[] = {'1};\n";
        print FD"    `PRJ_TOGGLE_BINS_$signal_wd\n";
      }
      print FD"   }\n";
    }
  }
  print FD "endgroup\n";
}
