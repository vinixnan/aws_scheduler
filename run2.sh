#!/bin/bash

problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot CyberShake_1000.dot Epigenomics_24.dot Inspiral_1000.dot Montage_1000.dot Sipht_1000.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Epigenomics_997.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 

problems="CyberShake_100.dot Epigenomics_100.dot Inspiral_100.dot Montage_100.dot Sipht_100.dot Epigenomics_24.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Inspiral_50.dot Montage_50.dot Sipht_60.dot" 


problems="CyberShake_100.dot Epigenomics_100.dot"
problems="Epigenomics_24.dot CyberShake_30.dot Epigenomics_46.dot Inspiral_30.dot Montage_25.dot Sipht_30.dot CyberShake_50.dot Inspiral_50.dot Montage_50.dot Inspiral_100.dot Montage_100.dot Sipht_60.dot Sipht_100.dot" 



alg="NSGA2"
heur="HEFT DLS HCPT PEFT"
heur="HEFT DLS PEFT"
pop=100
gen=100
idexec=1
qtdExp=20
qtdExp=10
for problem in $problems
do
    for h in $heur
    do
        idexec=0
        while [ $idexec -lt $qtdExp ]
        do
            python app/metaheuristic.py $problem $alg $h $idexec $pop $gen
            let idexec=$idexec+1;
        done
    done
done