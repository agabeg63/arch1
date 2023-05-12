#!/bin/bash

example_list='1 2 3 4 5 6 7'
for i in $example_list
do
    python /Users/ago/uni20192007/assignment1/assembler.py /Users/ago/uni20192007/assignment1/sample_input/example$i.s
    NUM_DIFF=`diff -y --suppress-common-lines assignment1/sample_output/example$i.o assignment1/sample_input/example$i.o | wc -l`
    
    if [ $NUM_DIFF -ge 10 ]
    then
        SCORE=0
    else
        SCORE=`expr 10 - $NUM_DIFF`
    fi

    echo "Test for example$i: $SCORE/10"
    echo
done
