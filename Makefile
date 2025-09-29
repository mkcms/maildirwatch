PYTHON ?= python3

black:
	${PYTHON} -m black maildirwatch.py

black-check:
	${PYTHON} -m black --check maildirwatch.py

isort:
	${PYTHON} -m isort maildirwatch.py

isort-check:
	${PYTHON} -m isort --check maildirwatch.py

format: black isort

checkformat: black-check isort-check

update-copyright-years:
	year=`date +%Y`;                                                      \
	sed -i *.rst *.py -r                                                  \
	  -e 's/Copyright \(C\) ([0-9]+)(-[0-9]+)?/Copyright (C) \1-'$$year'/'
