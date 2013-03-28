#!/usr/bin/env python
#
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
import luigi
import os
import sys
import ratatosk.lib.align.bwa
import ratatosk.lib.tools.gatk
import ratatosk.lib.tools.samtools
import ratatosk.lib.tools.picard
import ratatosk.lib.annotation.annovar
from ratatosk.pipeline.haloplex import HaloPlex
from ratatosk.pipeline.align import AlignSeqcap
from ratatosk.ext.scilife.config import config_dict

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        task = None
    if task == "HaloPlex":
        args = sys.argv[2:] + ['--config-file', config_dict['haloplex']]
        luigi.run(args, main_task_cls=ratatosk.pipeline.haloplex.HaloPlex)
    elif task == "AlignSeqcap":
        args = sys.argv[2:] + ['--config-file', config_dict['seqcap']]
        luigi.run(args, main_task_cls=ratatosk.pipeline.align.AlignSeqcap)
    # Whatever other task/config the user wants to run
    else:
        luigi.run()
