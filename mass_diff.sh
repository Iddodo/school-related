#!/bin/bash

folder="$HOME/mtm/ex0/part1"
file_to_compile="part1.c"
executable="mtm_tot"
test_output="tmpout"
diff_output="tmpdiff"
number_of_tests=4

touch $folder/$test_output
touch $folder/$diff_output

test_in_format() { 
    echo "test$1.in"
}
test_out_format() {
     echo "test$1.out"
}

echo

if [[ ! -f "$folder/$file_to_compile" ]]; then
    echo "File \"$folder/$file_to_compile\" is missing, exiting..."
    exit
fi

gcc -std=c99 -Wall -pedantic-errors -Werror -DNDEBUG $folder/$file_to_compile -o $folder/$executable

for itr in $(seq 1 $number_of_tests)
do
    test_in=$(test_in_format $itr)
    test_out=$(test_out_format $itr)

    if [[ ! -f $folder/$test_in ]]; then
        echo "Test \"$folder/$test_in\" is missing, skipping..."
        continue
    fi

    $folder/$executable < $folder/$test_in > $folder/$test_output
    if diff -y --width=100 "$folder/$test_out" "$folder/$test_output" > $folder/$diff_output; then
    echo "------------------------------  TEST ($itr) PASS -----------------------------"
    else
    echo "----------(EXPECTED)----------  TEST ($itr) FAIL -----------(YOURS)-----------"
    cat $folder/$diff_output
    echo
    fi
done

echo
echo

rm $folder/$executable
rm $folder/$test_output
rm $folder/$diff_output