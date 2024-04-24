#!/bin/bash


problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot CyberShake_1000.dot Epigenomics_24.dot Inspiral_1000.dot Montage_1000.dot Sipht_1000.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Epigenomics_997.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 

problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot Epigenomics_24.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 

algs="NSGA2 SMSEMOA AGEMOEA"
algs="NSGA2 AGEMOEA"
heur="HEFT PEFT HSIP"
heur="HEFT HSIP"
problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot"
problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot Epigenomics_24.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 

#problems="CyberShake_100.dot"
algs="NSGA2 AGEMOEA"
heur="HEFT PEFT HSIP"
pop=100
gen=500
qtdExp=1
#for a in $algs
#do
    for h in $heur
    do
        for a in $algs
        do
            for problem in $problems
            do
                idexec=0
                while [ $idexec -lt $qtdExp ]
                do
                    python app/main.py --idexec $idexec -p $problem -a $a -h $h --pop $pop --gen $gen
                    let idexec=$idexec+1;
                done
            done
        done
    done
#done