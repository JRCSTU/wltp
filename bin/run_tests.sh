#!/bin/bash
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl


## Always invokes  code-tests, but skip doctests and coverage on Python-2.


my_dir=`dirname "$0"`
cd $my_dir/..

declare -A fails
if  python -c 'import sys; print(sys.version_info[0])'| grep -q '3'; then
    echo "Python-3: Running ALL tests (code-tests, doctests, coverage)."
    python setup.py doctest_docs    || fails['doctest_docs'] 
    python setup.py doctest_code    || fails['doctest_code']=$?
    python setup.py test_code       || fails['test_code']=$?
    
    rst="`which rst2html.py`"
    if [ -n "`which cygpath`" ]; then 
        rst="`cygpath -w $rst`"
    fi
    python setup.py --long-description | python "$rst"  --halt=warning > /dev/null || fails['README']=$?
    
    python setup.py build_sphinx    || fails["build_sphinx"]=$?
    
    ## Print results
    #
    if [ ${#fails[@]} -gt 0 ]; then
        echo -n "TEST FAILURES:  "
        for fail in "${!fails[@]}"; do 
            echo -n "${fail}(${fails[$fail]})"
        done
        echo
        
        exit 1
    fi
else
    echo "Python-2: Running ONLY code-tests."
    python setup.py test_code
fi

