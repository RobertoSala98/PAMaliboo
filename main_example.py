import logging
import numpy as np
import os
from shutil import copyfile
import sys

from pamaliboo.acquisitions import UpperConfidenceBound, ExpectedImprovement
from pamaliboo.gaussian_process import DatabaseGaussianProcessRegressor as DGPR
from pamaliboo.jobs import HyperqueueJobSubmitter
from pamaliboo.objectives import DummyObjective
from pamaliboo.optimizer import Optimizer


output_folder = 'outputs'
database = 'dummy.local.csv'
np.random.seed(42)
debug = True if '-d' in sys.argv or '--debug' in sys.argv else False

# Temporary code to take initialization values and remove temp files
os.makedirs(output_folder, exist_ok=True)
database_path = os.path.join(output_folder, database)
if not os.path.exists(database_path):
  copyfile('resources/dummy_initial.csv', database_path)

# Set logging level
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

# Initialize library objects
acq = UpperConfidenceBound(maximize_n_warmup=10, maximize_n_iter=100)
bounds = {'x1': (-5, 5), 'x2': (-5, 5)}
gp = DGPR(database_path, feature_names=['f1', 'f2'])
gp.fit()
job_submitter = HyperqueueJobSubmitter(output_folder)
obj = DummyObjective()
optimizer = Optimizer(acq, bounds, gp, job_submitter, obj, output_folder)
optimizer.maximize(n_iter=40, parallelism_level=2, timeout=3)
