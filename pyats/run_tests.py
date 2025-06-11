# To run the job:
# easypy run_tests.py -testbed_file alwayson_testbed.yaml
# Description: This job file
import os
from ats.easypy import run


# All run() must be inside a main function
def main():
    # Find the location of the script in relation to the job file
    tests = os.path.join('./tests/device_tests.py')
    # Execute the testscript
    # run(testscript=testscript)
    run(testscript=tests)