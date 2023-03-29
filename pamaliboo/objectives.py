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
import logging
import numpy as np


class ObjectiveFunction(ABC):
  def __init__(self):
    self.logger = logging.getLogger(__name__)

  @abstractmethod
  def execution_command(self, x: np.ndarray) -> list[str]:
    pass

  @abstractmethod
  def parse_and_evaluate(self, output_file: str) -> float:
    pass


class DummyObjective(ObjectiveFunction):
  def __init__(self):
    super().__init__()

  def execution_command(self, x: np.ndarray) -> list[str]:
    return ['./dummy.sh', str(x[0]), str(x[1])]

  def parse_and_evaluate(self, output_file: str) -> float:
    with open(output_file, 'r') as f:
      output = f.read().strip()
    return float(output)


class LigenDummyObjectiveFunction(ObjectiveFunction):
  def __init__(self):
    super().__init__()

  def execution_command(self, x: np.ndarray) -> list[str]:
    return ['./ligen.sh'] + [str(_) for _ in x]

  def parse_and_evaluate(self, output_file: str) -> float:
    with open(output_file, 'r') as f:
      output_list = f.read().strip().split(',')
    exe_time = float(output_list[11])
    rmsd_list = [float(_) for _ in output_list[14].split('/')]
    rmsd = np.quantile(rmsd_list, 0.75)
    objective_value = -rmsd ** 3 * exe_time
    return objective_value
