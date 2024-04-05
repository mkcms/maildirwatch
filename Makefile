update-copyright-years:
	year=`date +%Y`;                                                      \
	sed -i *.rst *.py -r                                                  \
	  -e 's/Copyright \(C\) ([0-9]+)(-[0-9]+)?/Copyright (C) \1-'$$year'/'
