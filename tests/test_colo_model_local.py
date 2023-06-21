# BSD 2-Clause License
#
# Copyright (c) 2021-2023, Hewlett Packard Enterprise
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import pdb

import sys
import warnings

import pytest

from smartsim import Experiment, status

if sys.platform == "darwin":
    supported_dbs = ["tcp", "deprecated"]
else:
    supported_dbs = ["uds", "tcp", "deprecated"]

def _setup_test_colo(fileutils, db_type, exp_name, db_args, launcher="local"):
    """Setup things needed for setting up the colo pinning tests"""

    exp = Experiment(exp_name, launcher=launcher)

    # get test setup
    test_dir = fileutils.make_test_dir()
    sr_test_script = fileutils.get_test_conf_path("send_data_local_smartredis.py")

    # Create an app with a colo_db which uses 1 db_cpu
    colo_settings = exp.create_run_settings(exe=sys.executable, exe_args=sr_test_script)
    colo_model = exp.create_model(f"colocated_model", colo_settings)
    colo_model.set_path(test_dir)

    if db_type in ['tcp', "deprecated"]:
        db_args["port"] = 6780
        db_args["ifname"] = "lo"

    colocate_fun = {
        "tcp": colo_model.colocate_db_tcp,
        "deprecated": colo_model.colocate_db,
        "uds":colo_model.colocate_db_uds
    }
    colocate_fun[db_type](**db_args)

    # assert model will launch with colocated db
    assert colo_model.colocated
    # Check to make sure that limit_db_cpus made it into the colo settings
    return exp, colo_model

@pytest.mark.parametrize("db_type", supported_dbs)
def test_launch_colocated_model_defaults(fileutils, db_type, launcher="local"):
    """Test the launch of a model with a colocated database and local launcher"""

    db_args = { }

    exp, colo_model = _setup_test_colo(
        fileutils,
        db_type,
        "colocated_model_with_restart",
        db_args,
        launcher
    )

    exp.start(colo_model, block=True)
    statuses = exp.get_status(colo_model)
    assert all([stat == status.STATUS_COMPLETED for stat in statuses])

    # test restarting the colocated model
    exp.start(colo_model, block=True)
    statuses = exp.get_status(colo_model)
    assert all([stat == status.STATUS_COMPLETED for stat in statuses])

@pytest.mark.parametrize("db_type", supported_dbs)
def test_colocated_model_pinning_auto_1cpu(fileutils, db_type, launcher="local"):

    db_args = {
        "limit_db_cpus": True,
        "db_cpus": 1,
    }

    # Check to make sure that the CPU mask was correctly generated
    exp, colo_model = _setup_test_colo(
        fileutils,
        db_type,
        "colocated_model_pinning_auto_1cpu",
        db_args,
        launcher
    )
    assert colo_model.run_settings.colocated_db_settings["db_cpu_list"] == "0"
    assert colo_model.run_settings.colocated_db_settings["limit_db_cpus"]
    exp.start(colo_model)

@pytest.mark.parametrize("db_type", supported_dbs)
def test_colocated_model_pinning_auto_2cpu(fileutils, db_type, launcher="local"):

    db_args = {
        "limit_db_cpus": True,
        "db_cpus": 2,
    }

    # Check to make sure that the CPU mask was correctly generated
    exp, colo_model = _setup_test_colo(
        fileutils,
        db_type,
        "colocated_model_pinning_auto_2cpu",
        db_args,
        launcher
    )
    assert colo_model.run_settings.colocated_db_settings["db_cpu_list"] == "0-1"
    assert colo_model.run_settings.colocated_db_settings["limit_db_cpus"]
    exp.start(colo_model)

@pytest.mark.parametrize("db_type", supported_dbs)
def test_colocated_model_pinning_manual(fileutils, db_type, launcher="local"):
    # Check to make sure that the CPU mask was correctly generated

    db_args = {
        "limit_db_cpus": True,
        "db_cpus": 2,
        "db_cpu_list": "0,2"
    }

    exp, colo_model = _setup_test_colo(
        fileutils,
        db_type,
        "colocated_model_pinning_manual",
        db_args,
        launcher
    )
    assert colo_model.run_settings.colocated_db_settings["db_cpu_list"] == "0,2"
    assert colo_model.run_settings.colocated_db_settings["limit_db_cpus"]
    exp.start(colo_model)