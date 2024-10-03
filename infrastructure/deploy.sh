#!/bin/bash

echo ""
echo "=== Tofu Version ==="
tofu --version

echo ""
echo "=== Environment test ==="
echo $TEST_VARIABLE

echo ""
echo "=== Directory content ==="
ls -la

echo ""
echo "=== Writing to a file ==="
echo "Hello, world!" > hello.txt
echo $(date) >> hello.txt
echo " " >> hello.txt

echo ""
echo "=== File content ==="
cat hello.txt

echo ""