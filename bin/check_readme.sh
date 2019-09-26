#!/bin/bash
#-*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl


## Checks that README has no RsT-syntactic errors.
# Since it is used by `setup.py`'s `description` if it has any errors, 
# PyPi would fail parsing them, ending up with an ugly landing page,
# when uploaded.

set +x  # Set -x for debugging script.

my_dir=`dirname "$0"`
my_name=`basename "$0"`
my_dir="$(dirname "$0")"
if [ -f "$my_dir/../setup.py" ]; then
        cd "$my_dir/.."
else
        my_dir="$PWD"
fi

tmp_dir=$(mktemp -d -t wltp-$my_name-XXXXXXXXXX)

rm -rf "build/*" "dist/*"
python setup.py -q bdist_wheel --dist-dir $tmp_dir && \
twine check $tmp_dir/*.whl 

exc=$?
rm -rf $tmp_dir
exit $exc
