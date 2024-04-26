#!/bin/bash
pop=100
gen=500

problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot Epigenomics_24.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 
algs="NSGA2 AGEMOEA"
heur="HEFT PEFT HSIP"
qtdExp=1
algs="NSGA2"
pop=50
gen=250
idexec=0
while [ $idexec -lt $qtdExp ]
do
    for h in $heur
    do
        for a in $algs
        do
            for problem in $problems
            do
                python app/main.py --idexec $idexec -p $problem -a $a -h $h --pop $pop --gen $gen
            done
        done
    done
    let idexec=$idexec+1;
done