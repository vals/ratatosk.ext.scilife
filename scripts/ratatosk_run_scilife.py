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
from ratatosk import backend
from ratatosk.config import setup_config
from ratatosk.handler import setup_global_handlers
from ratatosk.utils import opt_to_dict, dict_to_opt
import ratatosk.lib.align.bwa
import ratatosk.lib.tools.gatk
import ratatosk.lib.tools.samtools
import ratatosk.lib.tools.picard
import ratatosk.lib.annotation.annovar
import ratatosk.lib.utils.cutadapt
from ratatosk.pipeline.haloplex import HaloPlex, HaloPlexSummary
from ratatosk.pipeline.seqcap import SeqCap, SeqCapSummary
from ratatosk.pipeline.align import Align, AlignSummary
from ratatosk.ext.scilife.config import config_dict

if __name__ == "__main__":
    task_cls = None
    opt_dict = {}
    if len(sys.argv) > 1:
        task = sys.argv[1]
        opt_dict = opt_to_dict(sys.argv[1:])
        if task in config_dict.keys():
            opt_dict['--config-file'] = config_dict[task]['config']
            task_cls = config_dict[task]['cls']
    else:
        task = None

    setup_config(config_file=opt_dict.get("--config-file"), custom_config_file=opt_dict.get("--custom-config"))
    setup_global_handlers()

    if task_cls:
        task_args = dict_to_opt(opt_dict)
        luigi.run(task_args, main_task_cls=task_cls)
    # Whatever other task/config the user wants to run
    else:
        luigi.run()
