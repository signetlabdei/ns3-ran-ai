#!/bin/bash

# Copyright (c) 2020, University of Padova, Dep. of Information Engineering, SIGNET lab
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
#  Plot the traces generated by three-gpp-vehicular-channel-condition-model-example
#

cat >aa <<EOL
set terminal gif animate delay 100
set output 'map.gif'
set view map
set style fill transparent solid 0.5
unset key
set style fill  transparent solid 0.35 noborder
set style circle radius 5

do for [i=0:90] {
  set zrange [i-1:i]
  set xrange [11.31:11.32]
  set yrange [44.48:44.5]
  set xlabel 'X [m]'
  set ylabel 'Y [m]'
  set xtics
  set ytics
  splot 'node-0.gnuplot' u 2:3:1 with circles lc rgb "blue"
  set object 101 rect from -25,-25 to 1400,1000 fc rgb "white"
}
EOL
gnuplot aa
rm aa
# rm out.txt
