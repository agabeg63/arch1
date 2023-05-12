test=0
success=0

# fibo
echo "test fibo..."
test=$((test+1))
python3 main.py -n 35000 -d 1000  sample_input/fibo.o > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/fibo.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test fibo failed"
else
  echo "\t test fibo passed"
  success=$((success+1))
fi
rm result


# fibo_rec
echo "test fibo_rec..."
test=$((test+1))
python3 main.py -n 110000 -d 10000  sample_input/fibo_rec.o  > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/fibo_rec.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test fibo_rec failed"
else
  echo "\t test fibo_rec passed"
  success=$((success+1))
fi
rm result


# seq_rw
echo "test seq_rw..."
test=$((test+1))
python3 main.py -n 7000 -d 1000  sample_input/seq_rw.o > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/seq_rw.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test seq_rw failed"
else
  echo "\t test seq_rw passed"
  success=$((success+1))
fi
rm result


# seq_rw_512
echo "test seq_rw_512..."
test=$((test+1))
python3 main.py -n 60000 -d 1000  sample_input/seq_rw_512.o > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/seq_rw_512.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test seq_rw_512 failed"
else
  echo "\t test seq_rw_512 passed"
  success=$((success+1))
fi
rm result


# seq_rw_4k
echo "test seq_rw_4k...."
test=$((test+1))
python3 main.py -n 500000 -d 10000  sample_input/seq_rw_4k.o  > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/seq_rw_4k.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test seq_rw_4k. failed"
else
  echo "\t test seq_rw_4k. passed"
  success=$((success+1))
fi
rm result

NUM_DIFF=0
# rand_rw
echo "test rand_rw..."
test=$((test+1))
python3 main.py -n 11000 -d 1000  sample_input/rand_rw.o > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/rand_rw.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test rand_rw failed"
else
  echo "\t test rand_rw passed"
  success=$((success+1))
fi
rm result


# rand_rw_512
echo "test rand_rw_512..."
test=$((test+1))
python3 main.py -n 90000 -d 10000  sample_input/rand_rw_512.o > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/rand_rw_512.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test rand_rw failed"
else
  echo "\t test rand_rw passed"
  success=$((success+1))
fi
rm result


# rand_rw_4k
echo "test rand_rw_4k..."
test=$((test+1))
python3 main.py -n 700000 -d 10000  sample_input/rand_rw_4k.o > result
NUM_DIFF=`diff -y --suppress-common-lines sample_output/rand_rw_4k.output result | wc -l`
if [ $NUM_DIFF -ne 0 ]
then
  echo "\t test rand_rw_4k failed"
else
  echo "\t test rand_rw_4k passed"
  success=$((success+1))
fi
rm result


echo "Total $success/$test tests passed"





