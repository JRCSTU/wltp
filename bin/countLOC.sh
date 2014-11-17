files=`find . -name '*.py' -o -name '*.txt' -o -name '*.sh' -o -name '*.rst' |grep -v /build/ |grep -v /wltc.egg |grep -v /tmp`
wc $files
