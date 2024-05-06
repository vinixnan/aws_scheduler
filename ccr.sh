#!/bin/bash
bw=$1
s=$2
file=$3
c=$4
o=$5 
cd /home/pysimgrid/
basepath="/code/"
python3 -m pysimgrid.tools.scale_ccr -b $bw -s $s -c $c -o $basepath$o $basepath$file
echo "python3 -m pysimgrid.tools.scale_ccr -b $bw -s $s -c $c -o $basepath$o $basepath$file"
cd /code/
