#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
:created: 5 Jan 2014
'''

import wltp.experiment as ex
from ..experiment import downscaleCycle
from ..model import wltc_data
import logging
import numpy as np
import numpy.testing as npt
import unittest


class experimentFuncs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def testDownscaling(self):
        wclasses = wltc_data()['classes']
        test_data = [(np.array(wclass['cycle']), wclass['downscale']['phases'], f_downscale)
                    for wclass in wclasses.values()
                    for f_downscale in np.linspace(0.1, 1, 10)]

        for (V, phases, f_downscale) in test_data:
            downscaleCycle(V, f_downscale, phases)


    def testNparray2Bytes(self):
        arr = np.array([-1, 0, 9, 10, 36, 255-ex._escape_char])

        self.assertEqual(ex.np2bytes(arr), b'\x7f\x80\x89\x8a\xa4\xff')
        self.assertRaisesRegex(AssertionError, 'Outside byte-range', ex.np2bytes, (arr + 1))
        self.assertRaisesRegex(AssertionError, 'Outside byte-range', ex.np2bytes, (arr - 1))

        npt.assert_array_equal(ex.bytes2np(ex.np2bytes(arr)), arr)


    def testRegex2bytes(self):
        regex = '\g1\g0\g24\g66\g127'

        self.assertEqual(ex.gearsregex(regex).pattern,  b'\x81\x80\x98\xc2\xff')

        regex = '\g1\g0|\g24\g66\g127'

        self.assertEqual(ex.gearsregex(regex).pattern,  b'\x81\x80|\x98\xc2\xff')


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, argv=sys.argv)
