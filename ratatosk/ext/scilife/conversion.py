""" Tasks for file conversions using scripts from the scilifelab repository.
"""
import os
import luigi
import ratatosk.lib.files.external
from ratatosk.job import InputJobTask, JobTask, JobWrapperTask
from ratatosk.jobrunner import DefaultShellJobRunner
from ratatosk.utils import rreplace, fullclassname


class Xls2PedJobRunner(DefaultShellJobRunner):
    pass


class InputXlsFile(InputJobTask):
    _config_section = "xls2ped"
    _config_subsection = "InputXlsFile"
    parent_task = luigi.Parameter(default="ratatosk.lib.files.external.XlsFile")
    suffix = luigi.Parameter(default=(".xls"), is_list=True)


class Xls2PedJobTask(JobTask):
    _config_section = "xls2ped"
    executable = ""

    def job_runner(self):
        return Xls2PedJobRunner()

    def exe(self):
        return self.sub_executable

    def main(self):
        return None


class Xls2Ped(Xls2PedJobTask):
    _config_subsection = "xls2ped"
    sub_executable = luigi.Parameter(default="xls2ped.py")
    parent_task = luigi.Parameter(default="ratatosk.ext.scilife.conversion.InputXlsFile")
    suffix = luigi.Parameter(default="_ped.txt")
