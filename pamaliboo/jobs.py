"""
Copyright 2023 Bruno Guindani
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from abc import ABC, abstractmethod
from enum import Enum
import json
import logging
import os
import subprocess
import warnings


class JobStatus(Enum):
  OTHER = 0
  CANCELED = 1
  FAILED = 2
  FINISHED = 3
  RUNNING = 4
  WAITING = 5


class JobSubmitter(ABC):
  """
  Object that submits jobs to a scheduler or similar programs.

  The output of such jobs will be saved to text files in the folder given to
  the class constructor.
  """
  def __init__(self, output_folder: str):
    self.logger = logging.getLogger(__name__)
    self.output_folder = output_folder
    self.logger.debug("Initializing %s", self.__class__.__name__)
    if os.path.exists(self.output_folder):
      self.logger.debug("Output folder %s already exists", self.output_folder)
    else:
      os.makedirs(self.output_folder)
      self.logger.debug("Created output folder %s", self.output_folder)

  @abstractmethod
  def submit(self, cmd: list[str], output_file: str) -> int:
    """
    Submit a job containing the given command.

    All output from the job will be stored in the given `output_file`. This
    function returns the identifier (ID) of the submitted job.
    """
    pass

  @abstractmethod
  def get_job_status(self, job_id: int) -> JobStatus:
    """Get status of job with the given identifier (ID)"""
    pass



class HyperqueueJobSubmitter(JobSubmitter):
  """Job submitter for the Hyperqueue library.

  Hyperqueue is a single executable file, whose path is indicated in the
  `hq_exec` member.
  """
  hq_exec = 'lib/hq'

  def submit(self, cmd: list[str], output_file: str) -> int:
    """
    Submit a job containing the given command.

    All output from the job will be stored in the given `output_file`. This
    function returns the identifier (ID) of the submitted job.
    """
    file_path = os.path.join(self.output_folder, output_file)
    hq_cmd = [self.hq_exec, 'submit', '--output-mode', 'json',
              '--stdout', file_path, '--stderr', file_path] + cmd
    self.logger.info("Submitting %s", hq_cmd)
    self.logger.debug("Output file will be %s", output_file)
    sub = subprocess.run(hq_cmd, capture_output=True)
    output = json.loads(sub.stdout.decode())
    if 'id' in output:
      return output['id']
    else:
      raise RuntimeError("submit() received unexpected output by Hyperqueue:\n"
                        f"{output}")


  def get_job_status(self, job_id: int) -> JobStatus:
    """Get status of job with the given identifier (ID)"""
    self.logger.debug("Requesting status of job %d", job_id)
    cmd = [self.hq_exec, 'job', 'list', '--all', '--output-mode', 'json']
    sub = subprocess.run(cmd, capture_output=True)
    # Parse Hyperqueue output to get job status
    output = json.loads(sub.stdout.decode())
    for job in output:
      if job['id'] == job_id:
        job_stats = job['task_stats']
        if job_stats['canceled'] == 1:
          status = JobStatus.CANCELED
        elif job_stats['failed'] == 1:
          status = JobStatus.FAILED
        elif job_stats['finished'] == 1:
          status = JobStatus.FINISHED
        elif job_stats['running'] == 1:
          status = JobStatus.RUNNING
        elif job_stats['waiting'] == 1:
          status = JobStatus.WAITING
        else:
          status = JobStatus.OTHER
        self.logger.debug("Status is %s", status)
        return status

    raise RuntimeError("get_job_status() received unexpected output by "
                      f"Hyperqueue while checking status of job {job_id}:\n"
                      f"{output}")
