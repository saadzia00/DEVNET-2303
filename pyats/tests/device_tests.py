#!/bin/env python
"""
Tests for IOS XE and NX-OS Always On Sandboxes.
"""

# To get a logger for the script
import logging
import json

# To build the table at the end
from tabulate import tabulate

# Needed for aetest script
from ats import aetest
from ats.log.utils import banner

# Genie Imports
from genie.conf import Genie
from genie.abstract import Lookup

# import the genie libs
from genie.libs import ops  # noqa

# import API libriries
from ncclient import manager
import requests
import xmltodict
import time
from netmiko import ConnectHandler



# Get your logger for your script
log = logging.getLogger(__name__)

MAX_RETRIES = 3

###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################


class common_setup(aetest.CommonSetup):
    """ Common Setup section """

    # CommonSetup have subsection.
    # You can have 1 to as many subsection as wanted

    @aetest.subsection
    def misc(self):
        requests.packages.urllib3.disable_warnings()

    # Connect to each device in the testbed
    @aetest.subsection
    def get_devices(self, testbed):
        genie_testbed = Genie.init(testbed)
        self.parent.parameters["testbed"] = genie_testbed
        device_list = []

        # Attempt to establish connection with each device
        # Limit to IOS and NX devices.
        for device in genie_testbed.devices.values():
            if device.os in ["iosxe", "nxos"]:
            # if device.os in ["nxos"]:
                log.info(banner("Connect to device '{d}'".format(d=device.name)))
                device_list.append(device)

        # Pass list of devices the to testcases
        self.parent.parameters.update(dev=device_list)

        # Setup a global notificaiton Message to send
        # Append to list any new lines to send in case of issues
        message = ["### {} Always On Sandbox Issues".format(genie_testbed.name)]


###################################################################
#                     TESTCASES SECTION                           #
###################################################################


class Connectivity_Verify(aetest.Testcase):
    """ Test if Device is reachable through all connections is functioning properly """

    @aetest.test
    def test_telnet(self):
        """ Verify device reachable through TELNET """

        for dev in self.parent.parameters["dev"]:
            log.info(
                banner("Testing TELNET Access to {}".format(dev.name))
            )

            # Retry loop, number of tries controlled by variable.
            for _ in range(MAX_RETRIES):
                try:
                    dev.connect(learn_hostname=True)
                except Exception as e:
                    log.error("Attempt number {} to connect with TELNET failed.".format(_ + 1))
                    log.error(e)
                    time.sleep(5)
                else:
                    break
            # If unable to connect, fail test
            else:
                self.failed(
                    "Failed to establish TELNET connection to `{} - {}`".format(
                        self.parent.parameters["testbed"].name,
                        dev.name
                    )
                )


class Baseline_Config_Verify(aetest.Testcase):
    """ Test if required baseline config is correct.
        Currnetly only testing for hostname matches expectation.
        If needed in future, add additional test cases.
    """

    @aetest.test
    def test_hostname(self):
        """ Verify device reachable through SSH """

        for dev in self.parent.parameters["dev"]:
            log.info(
                banner("Verifying hostname on {} is correct.".format(dev.name))
            )

            if dev.hostname != dev.name:
                log.error(
                    banner("Hostname doesn't match. Should be {} is {}.".format(dev.name, dev.hostname))
                )

    @aetest.test
    def test_configure_loopback(self):
        """Test loopback interface configuration"""
        for dev in self.parent.parameters["dev"]:
            try:
                # Configure loopback interface
                config_cmds = [
                    'interface loopback100',
                    'ip address 192.168.100.1 255.255.255.255',
                    'description PyATS Test Loopback'
                ]

                if dev.platform == 'nxos':
                    config_cmds.insert(1, 'no shutdown')

                dev.configure(config_cmds)

                # Verify configuration
                if dev.platform == 'nxos':
                    output = dev.execute('show interface loopback100')
                else:
                    output = dev.execute('show ip interface brief | include Loopback100')

                if '192.168.100.1' not in output:
                    self.failed(f"Loopback configuration failed on {dev.name}")
                    log.error(
                        banner("Loopback configuration failed on {}".format(dev.name))
                    )
                else:
                    log.info(
                        banner("Verifying loopback on {} is correct.".format(dev.name))
                    )
                # Cleanup
                dev.configure(['no interface loopback100'])

            except Exception as e:
                self.failed(f"Loopback configuration error on {dev.name}: {str(e)}")
                log.error(
                    banner("Loopback configuration failed on {}".format(dev.name))
                )

    @aetest.test
    def test_vlan_configuration(self):
        """Test VLAN creation and configuration"""
        for dev in self.parent.parameters["dev"]:
            # Skip VLAN tests for Cat8000v as it's primarily a router
            if dev.platform == 'iosxe':
                #self.skipped(f"VLAN tests not applicable for {dev.name} (Cat8000v)")
                log.info(
                    banner("Skipped VLAN test for {}({}).".format(dev.name,dev.platform))
                )
                continue

            try:
                # Verify VLAN creation
                output = dev.execute('show vlan brief')
                if ('prod' not in output) or ('security' not in output):
                    self.failed(f"VLAN failed on {dev.name}")
                    log.error(
                        banner("VLAN 'Prod' or 'Security' doesn't exist on {}".format(dev.name))
                    )
                log.info(
                    banner("Verification for vlans 'Prod' or 'Security' is correct for {}.".format(dev.name))
                )

            except Exception as e:
                self.failed(f"VLAN configuration failed on {dev.name}: {str(e)}")
                log.error(
                    banner(" VLAN 'Prod' or 'Security' doesn't exist on {}".format(dev.name))
                )

    @aetest.test
    def test_TACACS_configuration(self):
        """Test TACACS creation and configuration"""
        for dev in self.parent.parameters["dev"]:
            # Skip TACACS tests for NXOS as it's primarily a router
            if dev.platform == 'nxos':
                #self.skipped(f"TACACS tests not applicable for {dev.name} {dev.platform}")
                log.info(
                    banner("TACACS tests not applicable for {}({}).".format(dev.name,dev.platform))
                )
                continue

            try:
                # Verify TACACS creation
                output = dev.execute('show tacacs public')
                if ('sbxtacacs' and '10.17.248.43') not in output:
                    self.failed(f"TACACS failed on {dev.name}")
                    log.error(
                        banner("TACACS failed on {}".format(dev.name))
                    )
                log.info(
                    banner("Verification for TACACS server 'sbxtacacs' and IP '10.17.248.43' is correct for {}.".format(dev.name))
                )
            except Exception as e:
                self.failed(f"TACACS configuration failed on {dev.name}: {str(e)}")
                log.error(
                    banner("TACACS failed on {}".format(dev.name))
                )


# #####################################################################
# ####                       COMMON CLEANUP SECTION                 ###
# #####################################################################


# This is how to create a CommonCleanup
# You can have 0 , or 1 CommonCleanup.
# CommonCleanup can be named whatever you want :)
class common_cleanup(aetest.CommonCleanup):
    """ Common Cleanup for Sample Test """

    # CommonCleanup follow exactly the same rule as CommonSetup regarding
    # subsection
    # You can have 1 to as many subsections as wanted
    # here is an example of 1 subsection

    @aetest.subsection
    def clean_everything(self):
        """ Common Cleanup Subsection """
        log.info("Aetest Common Cleanup ")


if __name__ == "__main__":  # pragma: no cover
    aetest.main()

