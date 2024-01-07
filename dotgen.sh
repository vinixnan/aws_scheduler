#!/bin/bash 
problems="CyberShake_100.xml Epigenomics_100.xml Inspiral_100.xml Montage_100.xml Sipht_100.xml CyberShake_1000.xml Epigenomics_24.xml Inspiral_1000.xml Montage_1000.xml Sipht_1000.xml CyberShake_30.xml Epigenomics_46.xml Inspiral_30.xml Montage_25.xml Sipht_30.xml CyberShake_50.xml Epigenomics_997.xml Inspiral_50.xml Montage_50.xml Sipht_60.xml" 
cd /home/pysimgrid/
for input in $problems
do
    input="/code/datasets/"$input
    output="${input/xml/"dot"}"
    echo $input" to "$output
    python3 -m pysimgrid.tools.dax_to_dot $input $output
done