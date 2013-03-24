# Copyright (c) 2013 Per Unneberg
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
import os
import unittest
import logging
from ratatosk.ext.scilife.sample import *
import ngstestdata as ntd

ngsloadmsg = "No ngstestdata module; skipping test. Do a 'git clone https://github.com/percyfal/ngs.test.data' followed by 'python setup.py develop'"
has_data = False
try:
    import ngstestdata as ntd
    has_data = True
except:
    logging.warn(ngsloadmsg)
    time.sleep(1)

@unittest.skipIf(not has_data, ngsloadmsg)
class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.project = os.path.relpath(os.path.join(ntd.__path__[0], os.pardir, "data", "projects", "J.Doe_00_01"))
        self.sample = 'P001_101_index3'
        self.flowcell = '120924_AC003CCCXX'

    def test_tg_all(self):
        """Test getting all sample runs from a project"""
        tl = target_generator(indir=self.project)
        self.assertEqual(sorted([x[0] for x in tl]), ['P001_101_index3', 'P001_101_index3', 'P001_102_index6'])
        self.assertEqual(list(set([x[0] for x in tl])), ['P001_101_index3', 'P001_102_index6'])

    def test_tg_subset_sample(self):
        """Test getting a subset of samples"""
        tl = target_generator(indir=self.project, sample=[self.sample])
        self.assertEqual(sorted([x[0] for x in tl]), ['P001_101_index3', 'P001_101_index3'])

    def test_tg_subset_flowcell(self):
        """Test getting samples subsetted by flowcell"""
        tl = target_generator(indir=self.project, flowcell=[self.flowcell])
        self.assertNotIn("121015_BB002BBBXX",  sorted([os.path.basename(os.path.dirname(x[2])) for x in tl]))

    def test_tg_subset_sample_flowcell(self):
        """Test getting samples subsetted by flowcell and sample"""
        tl = target_generator(indir=self.project, flowcell=[self.flowcell], sample=[self.sample])
        self.assertEqual(sorted([os.path.basename(os.path.dirname(x[2])) for x in tl]), ['120924_AC003CCCXX'])
        self.assertEqual(sorted([os.path.basename(x[0]) for x in tl]), ['P001_101_index3'])


        
