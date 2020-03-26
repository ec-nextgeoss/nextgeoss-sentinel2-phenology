for test in $( ls tests.d/* )
do
  /bin/bash ${test}
done

