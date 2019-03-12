import argparse

import pytest

import parsl
from parsl.app.app import python_app, bash_app
from parsl.tests.configs.local_threads_htex import config

parsl.clear()
parsl.load(config)

import logging
logger = logging.getLogger(__name__)


@python_app(executors=['local_threads'])
def python_app_2():
    import os
    import threading
    import time
    time.sleep(0.1)
    return "Hello from PID[{}] TID[{}]".format(os.getpid(), threading.current_thread())


@python_app(executors=['local_htex'])
def python_app_1():
    import os
    import threading
    import time
    time.sleep(0.1)
    return "Hello from PID[{}] TID[{}]".format(os.getpid(), threading.current_thread())


@bash_app
def bash_app(stdout=None, stderr=None):
    return 'echo "Hello from $(uname -a)" ; sleep 0.1'


@pytest.mark.local
def test_python(N=2):
    """Testing basic python functionality."""

    r1 = {}
    r2 = {}
    for i in range(0, N):
        r1[i] = python_app_1()
        r2[i] = python_app_2()
    print("Waiting ....")

    for x in r1:
        print("python_app_1 : ", r1[x].result())
    for x in r2:
        print("python_app_2 : ", r2[x].result())

    return


@pytest.mark.local
def test_bash():
    """Testing basic bash functionality."""

    import os
    fname = os.path.basename(__file__)

    x = bash_app(stdout="{0}.out".format(fname))
    print("Waiting ....")
    print(x.result())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num", default=10,
                        help="Count of apps to launch")
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Count of apps to launch")
    parser.add_argument("-c", "--config", default='local',
                        help="Path to configuration file to run")
    args = parser.parse_args()
    parsl.load(args.config)
    if args.debug:
        parsl.set_stream_logger()

    test_python()
    test_bash()