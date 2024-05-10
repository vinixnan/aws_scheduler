#!/bin/bash
pop=50
gen=700

problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot Epigenomics_24.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 
algs="NSGA2 AGEMOEA"
heur="HEFT PEFT HSIP"
qtdExp=12
idexec=8
echo "Go"

while [ $idexec -lt $qtdExp ]
do
    for h in $heur
    do
        for a in $algs
        do
            for problem in $problems
            do
                out_filename="out"$a"_"$h"_"$idexec"_"$problem
                err_filename="err"$a"_"$h"_"$idexec"_"$problem
                python3 app/main.py --idexec $idexec -p $problem -a $a -h $h --pop $pop --gen $gen
            done
        done
    done
    let idexec=$idexec+1;
done