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
import logging

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

def _save_job_id(jobid, idfile="JOBID", **job_args):
    """Save jobid to file in working directory"""
    JOBIDFILE = os.path.join(job_args['workingDirectory'], idfile)
    with open(JOBIDFILE, "w") as fh:
        logging.info("Saving jobid {} to file {}".format(self._meta.jobid, JOBIDFILE))
        fh.write(jobid)

def monitor(self, work_dir, idfile="JOBID"):
    """Check for existing job"""
    return self._monitor_job(idfile, **{'workingDirectory':work_dir})

def _monitor_job(idfile="JOBID", **job_args):
    """Check if job is currently being run or in queue. For now,
    the user will manually have to terminate job before proceeding"""
    JOBIDFILE = os.path.join(job_args['workingDirectory'], idfile)
    if not os.path.exists(JOBIDFILE):
        return 
    logging.debug("Will read {} for jobid".format(JOBIDFILE))
    with open(JOBIDFILE) as fh:
        jobid = fh.read()
    ## http://code.google.com/p/drmaa-python/wiki/Tutorial
    decodestatus = {
        drmaa.JobState.UNDETERMINED: 'process status cannot be determined',
        drmaa.JobState.QUEUED_ACTIVE: 'job is queued and active',
        drmaa.JobState.SYSTEM_ON_HOLD: 'job is queued and in system hold',
        drmaa.JobState.USER_ON_HOLD: 'job is queued and in user hold',
        drmaa.JobState.USER_SYSTEM_ON_HOLD: 'job is queued and in user and system hold',
        drmaa.JobState.RUNNING: 'job is running',
        drmaa.JobState.SYSTEM_SUSPENDED: 'job is system suspended',
        drmaa.JobState.USER_SUSPENDED: 'job is user suspended',
        drmaa.JobState.DONE: 'job finished normally',
        drmaa.JobState.FAILED: 'job finished, but failed',
        }
    s = drmaa.Session()
    s.initialize()
    try:
        status = s.jobStatus(str(jobid))
        logging.debug("Getting status for jobid {}".format(jobid))
        logging.info("{}".format(decodestatus[status]))
        if status in [drmaa.JobState.QUEUED_ACTIVE, drmaa.JobState.RUNNING, drmaa.JobState.UNDETERMINED]:
            logging.warn("{}; please terminate job before proceeding".format(decodestatus[status]))
            return True
    except drmaa.errors.InternalException:
        logging.warn("No such jobid {}".format(jobid))
        pass
    s.exit()
    return

def drmaa(cmd_args, pargs, capture=True, ignore_error=False, cwd=None, **kw):
    if kw.get('platform_args', None):
        platform_args = opt_to_dict(kw['platform_args'])
    else:
        platform_args = opt_to_dict([])
    kw.update(**vars(pargs))
    job_args = make_job_template_args(platform_args, **kw)
    if not _check_args(**kw):
        logging.warn("missing argument; cannot proceed with drmaa command. Make sure you provide time, account, partition, and jobname")
        return

    if kw.get('monitorJob', False):
        if _monitor_job(**job_args):
            loging.info("exiting from {}".format(__name__) )
            return

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
        if kw.get('saveJobId', False):
            _save_job_id(**job_args)
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
    job_args['jobname'] = kw.get('jobname', None) or opt_d.get('-J', None) or  opt_d.get('--job-name', None)
    job_args['time'] = kw.get('time', None) or opt_d.get('-t', None) or  opt_d.get('--time', None)
    job_args['time'] = convert_to_drmaa_time(job_args['time'])
    job_args['partition'] = kw.get('partition', None) or opt_d.get('-p', None) or  opt_d.get('--partition', None)
    job_args['account'] = kw.get('account', None) or opt_d.get('-A', None) or  opt_d.get('--account', None)
    job_args['outputPath'] = kw.get('outputPath', None) or opt_d.get('--output', None) or opt_d.get('-o', os.curdir)
    job_args['errorPath'] = kw.get('errorPath', None) or opt_d.get('--error', None) or opt_d.get('-e', os.curdir)
    job_args['workingDirectory'] = kw.get('workingDirectory', None) or opt_d.get('-D', os.curdir) 
    job_args['email'] = kw.get('email', None) or opt_d.get('--mail-user', None) 
    invalid_keys = ["--mail-user", "--mail-type", "-o", "--output", "-D", "--workdir", "-J", "--job-name", "-p", "--partition", "-t", "--time", "-A", "--account", "-e", "--error"]
    extra_keys = [x for x in opt_d.keys() if x not in invalid_keys]
    extra_args = ["{}={}".format(x, opt_d[x]) if x.startswith("--") else "{} {}".format(x, opt_d[x]) for x in extra_keys]
    job_args['extra'] = kw.get('extra_args', None) or extra_args
    job_args['extra'] = " ".join(job_args['extra'])
    return job_args


if __name__ == "__main__":
    # if not os.getenv("DRMAA_LIBRARY_PATH"):
    #     logging.warn("No environment variable $DRMAA_LIBRARY_PATH: loading {} failed".format(__name__))
    #     sys.exit()
    # if not has_drmaa:
    #     logging.warn("No 'drmaa' module: please install drmaa before proceeding.".format(__name__))
    #     sys.exit()

    pass
