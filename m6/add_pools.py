#!/usr/bin/env python


"""
Author: Nick Russo
Purpose: Using RESTCONF with IOS-XE specific YANG models to manage DHCP
server pools on a Cisco IOS-XE router via the always-on Cisco DevNet sandbox.
"""

import requests
import yaml


def main():
    """
    Execution begins here.
    """

    # The IOS-XE sandbox uses a self-signed cert at present, so let's
    # ignore any obvious security warnings for now.
    requests.packages.urllib3.disable_warnings()

    # The API path below is what the DevNet sandbox uses for API testing,
    # which may change in the future. Be sure to check the IP address as
    # I suspect this changes frequently. See here for more details:
    # https://developer.cisco.com/site/ios-xe
    api_path = "https://ios-xe-mgmt.cisco.com:9443/restconf"

    # Create 2-tuple for "basic" authentication using Cisco DevNet credentials.
    # No fancy tokens needed to get basic RESTCONF working on Cisco IOS-XE.
    auth = ("root", "D_Vay!_10&")

    # Read YAML declarative state with list of DHCP pools to add
    with open("config_state.yml", "r") as handle:
        config_state = yaml.safe_load(handle)

    # Create JSON structure to add a new pool along with the HTTP POST
    # headers needed to add it.
    add_pools = {"Cisco-IOS-XE-dhcp:pool": config_state}
    post_headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json, application/yang-data.errors+json",
    }

    # Issue HTTP POST request to a similar URL used for the GET request,
    # except carrying the new DHCP pool in the HTTP body. Also, we don't need
    # to specify "/pool" since the dictionary key in the body carries it.
    post_dhcp_response = requests.post(
        f"{api_path}/data/Cisco-IOS-XE-native:native/ip/dhcp",
        headers=post_headers,
        auth=auth,
        json=add_pools,
        verify=False,
    )

    # Uncomment the line below to see the JSON response; great for learning
    # import json; print(json.dumps(post_dhcp_response.json(), indent=2))

    # HTTP 201 means "created", implying a new resource was added. The
    # response will tell us the URL of the newly-created resource, simplifying
    # future removal.
    if post_dhcp_response.status_code == 201:
        print(f"Added DHCP pool at: {post_dhcp_response.headers['Location']}")
        # import json; print(json.dumps(add_pool, indent=2))

        # Save configuration whenever the DHCP pool is added. This ensures
        # the configuration will persist across reboots.
        post_save_response = requests.post(
            f"{api_path}/operations/cisco-ia:save-config",
            headers=post_headers,
            auth=auth,
            verify=False,
        )
        if post_save_response.ok:
            print("Saved configuration")


if __name__ == "__main__":
    main()