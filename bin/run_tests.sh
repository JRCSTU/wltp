#!/bin/bash
#
# Always invoke code-tests, but skip doctests and coverage on Python!=3.7.


my_dir=`dirname "$0"`
cd $my_dir/..

declare -A fails

# Pytest fails sometimes with old cache from git.
rm -rf build/* docs/_build/*

if  python -c 'import sys; print(sys.version_info[0:2])'| grep -q '(3, 7)'; then
    echo "Python-3: Running ALL tests (code-tests, doctests, coverage)."

    pytest --doctest-glob=README.rst --doctest-modules \
        --cov=wltp.experiment --cov=wltp.model --cov=wltp.cycles --cov=wltp.utils \
        || fails['pytest'] 

    ./bin/check_readme.sh || fails['README']=$?
    
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
    else:
        echo "ALL OK"
    fi
else
    echo "Python-2: Running ONLY code-tests."
    pytest
fi

