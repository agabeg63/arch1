#!/bin/bash

example_list='example01 example02 example03 example04 example05 example06 example07' 

for i in $example_list
do
    python3 assignment2/main.py -m -n 10000 assignment2/sample_input/$i.o > result
    
    NUM_DIFF=`diff -y --suppress-common-lines assignment2/sample_output/$i result | wc -l`
    NUM_REF=`wc -l < assignment2/sample_output/$i`

    if [ $NUM_DIFF -ge 10 ]
    then
        SCORE=0
    else
        SCORE=`expr 10 - $NUM_DIFF`
    fi

    echo "Test for $i: $SCORE/10"
    echo

    rm result

done
