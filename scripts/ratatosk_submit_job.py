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

import re
import os
import sys
import argparse
import itertools
import logging
from ratatosk.ext.scilife.sample import target_generator, make_fastq_links

logging.basicConfig(level=logging.INFO)

has_drmaa=False
try:
    import drmaa
    has_drmaa=True
except:
    pass


## yes or no: http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
def query_yes_no(question, default="yes", force=False):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user). The force option simply
    sets the answer to default.
    
    The "answer" return value is one of "yes" or "no".
    
    :param question: the displayed question
    :param default: the default answer
    :param force: set answer to default
    :returns: yes or no
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        if not force:
            choice = raw_input().lower()
        else:
            choice = "yes"
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                                 "(or 'y' or 'n').\n")

def dry(message, func, dry_run=True, *args, **kw):
    """Wrapper that runs a function (runpipe) if flag dry_run isn't set, otherwise returns function call as string
    
    :param message: message describing function call
    :param func: function to call
    :param *args: positional arguments to pass to function
    :param **kw: keyword arguments to pass to function
    """
    if dry_run:
        logging.debug("(DRY_RUN): " + str(message) + "\n")
        return "(DRY_RUN): " + str(message) + "\n"
    return func(*args, **kw)

def drmaa(cmd_args, pargs, capture=True, ignore_error=False, cwd=None):
    kw = vars(pargs)
    job_args = make_job_template_args(opt_to_dict(pargs.extra), **kw)
    command = " ".join(cmd_args)
    def runpipe():
        s = drmaa.Session()
        s.initialize()
        jt = s.createJobTemplate()
        jt.remoteCommand = cmd_args[0]
        jt.args = cmd_args[1:]
        jt.jobName = job_args['jobname']
        if os.path.isdir(job_args['outputPath']):
            jt.outputPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['outputPath'], os.getenv("HOME")), jt.jobName + "-drmaa.log")
        else:
            jt.outputPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['outputPath'], os.getenv("HOME")))
        if os.path.isdir(job_args['errorPath']):
            jt.errorPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['errorPath'], os.getenv("HOME")), jt.jobName + "-drmaa.err")
        else:
            jt.errorPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['errorPath'], os.getenv("HOME")))

        jt.workingDirectory = drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.relpath(job_args['workingDirectory'], os.getenv("HOME"))
        jt.nativeSpecification = "-t {time} -p {partition} -A {account} {extra}".format(**job_args)
        if kw.get('email', None):
            jt.email=[kw.get('email')]
        logging.info("Submitting job with native specification {}".format(jt.nativeSpecification))
        logging.info("Working directory: {}".format(jt.workingDirectory))
        logging.info("Output logging: {}".format(jt.outputPath))
        logging.info("Error logging: {}".format(jt.errorPath))
        jobid = s.runJob(jt)
        logging.info('Your job has been submitted with id ' + jobid)
        s.deleteJobTemplate(jt)
        s.exit()
    dry(command, runpipe)

def opt_to_dict(opts):
    """Transform option list to a dictionary.

    :param opts: option list
    
    :returns: option dictionary
    """
    if isinstance(opts, dict):
        return
    if isinstance(opts, str):
        opts = opts.split(" ")
    args = list(itertools.chain.from_iterable([x.split("=") for x in opts]))
    opt_d = {k: True if v.startswith('-') else v
             for k,v in zip(args, args[1:]+["--"]) if k.startswith('-')}
    return opt_d

def convert_to_drmaa_time(t):
    """Convert time assignment to format understood by drmaa.

    In particular transforms days to hours if provided format is
    d-hh:mm:ss. Also transforms mm:ss to 00:mm:ss.

    :param t: time string

    :returns: converted time string formatted as hh:mm:ss or None if
    time string is malformatted
    """
    if not t:
        return None
    m = re.search("(^[0-9]+\-)?([0-9]+:)?([0-9]+):([0-9]+)", t)
    if not m:
        return None
    days = None
    if m.group(1):
        days = m.group(1).rstrip("-")
    hours = None
    if m.group(2):
        hours = m.group(2).rstrip(":")
    minutes = m.group(3)
    seconds = m.group(4)
    if days:
        hours = 24 * int(days) + int(hours)
    else:
        if not hours:
            hours = "00"
        if len(str(hours)) == 1:
            hours = "0" + hours
        if len(str(minutes)) == 1:
            minutes = "0" + minutes
    t_new = "{}:{}:{}".format(hours, minutes, seconds)
    return t_new

def make_job_template_args(opt_d, **kw):
    """Given a dictionary of arguments, update with kw dict that holds arguments passed to argv.

    :param opt_d: dictionary of option key/value pairs
    :param kw: dictionary of program arguments

    :returns: dictionary of job arguments
    """
    job_args = {}
    job_args['jobname'] = kw.get('jobname')
    job_args['time'] = kw.get('time')
    job_args['time'] = convert_to_drmaa_time(job_args['time'])
    job_args['partition'] = kw.get('partition')
    job_args['account'] = kw.get('account', None)
    job_args['outputPath'] = kw.get('outputPath')
    job_args['errorPath'] = kw.get('errorPath')
    job_args['workingDirectory'] = kw.get('workingDirectory')
    job_args['email'] = kw.get('email', None)

    invalid_keys = ["--mail-user", "--mail-type", "-o", "--output", "-D", "--workdir", "-J", "--job-name", "-p", "--partition", "-t", "--time", "-A", "--account", "-e", "--error"]
    extra_keys = [x for x in opt_d.keys() if x not in invalid_keys]
    extra_args = ["{}={}".format(x, opt_d[x]) if x.startswith("--") else "{} {}".format(x, opt_d[x]) for x in extra_keys]
    job_args['extra'] = " ".join(extra_args)

    return job_args


if __name__ == "__main__":
    # if not os.getenv("DRMAA_LIBRARY_PATH"):
    #     logging.warn("No environment variable $DRMAA_LIBRARY_PATH: loading {} failed".format(__name__))
    #     sys.exit()
    # if not has_drmaa:
    #     logging.warn("No 'drmaa' module: please install drmaa before proceeding.".format(__name__))
    #     sys.exit()
    parser = argparse.ArgumentParser(description='ratatosk submit job arguments.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Drmaa parser group
    group = parser.add_argument_group("Drmaa options")
    group.add_argument('-A', '--account', type=str, required=True,
                        help='UPPMAX project account id')
    group.add_argument('-p', '--partition', type=str, default="node",
                        help='partition type.', choices=["node", "core", "mem72GB", "fat"])
    group.add_argument('-t', '--time', type=str, default="10:00:00",
                        help='run time')
    group.add_argument('-J', '--jobname', type=str, default="ratatosk",
                        help='job name')
    group.add_argument('-D', '--workingDirectory', type=str, default=os.curdir,
                        help='working directory')
    group.add_argument('-o', '--outputPath', type=str, default=os.curdir,
                        help='output path for stdout')
    group.add_argument('-e', '--errorPath', type=str, default=os.curdir,
                        help='output path for stderr')
    group.add_argument('--email', type=str, default=None,
                        help='email address to send job information to')
    group.add_argument('--extra', type=str, default=None,
                        help='extra args to submit via drmaa, provided as string')

    # Sample parser group
    sample_group = parser.add_argument_group("Sample options")
    sample_group.add_argument('indir', type=str,
                              help='Input directory. Assumes that data in input directory is organized by sample/flowcell/sequences.fastq.gz')
    sample_group.add_argument('-O', '--output_dir', type=str, default='input directory',
                              help='Output directory. ')
    sample_group.add_argument('--sample', type=str, default=None, nargs="*",
                              help='samples to process')
    sample_group.add_argument('--sample_file', type=str, default=None,
                              help='file containing samples to process, one per line')
    sample_group.add_argument('--lane', type=int, choices=xrange(1,9), default=None,
                              help='lanes to process')
    sample_group.add_argument('--flowcell', type=str, default=None, nargs="*",
                              help='email address to send job information to')
    sample_group.add_argument('-N', '--batch_size', type=int, default=4,
                              help='number of samples to process per node')

    # Ratatosk parser group
    # These arguments are directly passed to ratatosk
    ratatosk_group = parser.add_argument_group("Ratatosk options. These arguments are passed directly to ratatosk_run_scilife.py")
    ratatosk_group.add_argument('--config-file', type=str,
                                help='configuration file')
    ratatosk_group.add_argument('--custom-config', type=str, default=None,
                                help='custom configuration file')
    ratatosk_group.add_argument('--workers', type=int, default=4,
                                help='number of workers to use')

    # Parse arguments
    pargs = parser.parse_args()

    # Collect information about what samples to run, and on how many
    # nodes. This is somewhat convoluted since ratatosk_run_scilife
    # also collects sample information, but this step is necessary as
    # we need to wrap ratatosk_run_scilife.py in drmaa
    targets = target_generator(indir=pargs.indir, sample=pargs.sample,
                               flowcell=pargs.flowcell, lane=pargs.lane)
    # After getting run list, if output directory is different to
    # input directory, link raw data files to output directory and
    # remember to use this directory for ratatosk tasks. In this way
    # we actually can run on subsets of sample runs or flowcells
    if pargs.output_dir != pargs.indir:
        newtargets = make_fastq_links(targets, pargs.indir, pargs.output_dir)

    # Group samples in groups
    # sample_run_groups = partition(sample_run_list)
    # query_yes_no("Going to run ... jobs")
    # for srg in sample_run_groups:
    # drmaa(srg)
