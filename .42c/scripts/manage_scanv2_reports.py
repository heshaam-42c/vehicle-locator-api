#!/usr/bin/env python3

import json
import base64
import argparse
import requests
import re
import sys

#Create empty dictionary to store list of scan reports
scan_confs_list = {}

def testUUID(token):
    return re.match("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", token)

# This call list all scan reports available for this API. You can use the task ID to retrieve the report and 
# the scan conf ID to match conf that was used, should you have several ones.
def list_reports(token: str, aid: str):
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanReports"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: unable to list scan reports {response.status_code}")
    else:
        # print all the TaskID / scanConfId pairs.
        if not quiet and len(response.json()['list']) == 0: print(f"[*] No reports found for API {aid}")
        if len(response.json()['list']) != 0:
            if quiet: print("taskID,scanConfID,scanConfName")
        for c in response.json()['list']:
                if c['configuration'] == None:
                    taskId = c['report']['taskId']
                    scan_conf_name = c['report']['name']
                    if not quiet: print(f"[*] Report with ID: {taskId} is available for SaaS scan V1 with name {scan_conf_name}")
                    if quiet: print(f"{taskId},{scan_conf_name}")
                else:
                    taskId = c['report']['taskId']
                    scan_conf_name = c['configuration']['name']
                    scan_conf_id = scan_confs_list.get(scan_conf_name)
                    if not quiet: print(f"[*] Report with ID: {taskId} is available for scan conf with ID {scan_conf_id} and name {scan_conf_name}")
                    if quiet: print(f"{taskId},{scan_conf_id},{scan_conf_name}")

def retrieveReport(token: str, taskId: str):
    # This call retrieves a report via its taskID
    url =  f"{PLATFORM}/api/v2/scanReports/{taskId}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers) 

    if response.status_code != 200:
        print(f"Error: unable to retrieve scan report {response.status_code}")
    else:
        report_b64 = response.json()['file']
        log_b64 = response.json()['logFile']
        report_json = json.loads(base64.decodebytes(report_b64.encode("utf-8")))
        log_asbytes = base64.decodebytes(log_b64.encode("utf-8"))
        log_text = log_asbytes.decode ('utf-8')
        if not quiet: print("Saving report and log as files identified by taskID")

        report_filename = f"scanreport_{taskId}.json"
        log_filename = f"scanlog_{taskId}.json"
        try:
            with open (report_filename, 'w') as outfile_report:
                json.dump (report_json, outfile_report, indent=2)
            with open (log_filename, 'w') as outfile_log:
                outfile_log.write (log_text)
        finally:
            outfile_report.close()
            outfile_log.close()
            if quiet: print(f"{report_filename},{log_filename}")

def retrieve_config_names (token: str, aid: str):
    # We need to use this call to retrieve a scan conf name from its ID.
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanConfigurations"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: unable to retrieve scan lists {response.status_code}")
        return None
    else:
        for c in response.json()['list']:
            scan_conf_name = c['configuration']['name']
            scan_conf_id = c['configuration']['id']
            scan_confs_list.update ({scan_conf_name:scan_conf_id})

def main():
    parser = argparse.ArgumentParser(
        description='42Crunch Manage Scan Configuration'
    )
    parser.add_argument('APITOKEN',
                        help="42Crunch API token")
    parser.add_argument('API_UUID',
                        help="UUID of API to scan")
    parser.add_argument('-o', "--options",
                       action='store',
                       choices=['list', 'retrieve'],
                       help="Use *list* to get available reports and *retrieve* to get a specific one via taskID",
                       default="list",
                       required=True)
    parser.add_argument('-p', '--platform', 
                        required=False, 
                        default='https://platform.42crunch.com', 
                        help="Default is https://platform.42crunch.com",
                        type=str)
    parser.add_argument('-q', "--quiet",
                        default=False,
                        action="store_true",
                        help="Quiet output - only report names/filename shown")
    parser.add_argument('-t', "--taskId",
                       help="taskId - REQUIRED to retrieve a report")                   
    parser.add_argument('-d', '--debug',
                        default=False,
                        action="store_true",
                        help="debug level")
    parsed_cli = parser.parse_args()

    global quiet, debug, PLATFORM
    quiet = parsed_cli.quiet
    debug = parsed_cli.debug
    apitoken = parsed_cli.APITOKEN
    aid = parsed_cli.API_UUID
    action = parsed_cli.options
    PLATFORM = parsed_cli.platform

    if not testUUID(aid):
        print("Error, API ID must be in UUID format. Exiting...")
        sys.exit(1)

    # Fill the config names dict.
    if not quiet: print("[*] Retrieving scan configurations list...")
    retrieve_config_names(apitoken, aid)
    if action == "list":
        if not quiet: print("[*] Listing existing reports...")
        list_reports (apitoken, aid)
    else:
        # action is retrieve
        taskid = parsed_cli.taskId  
        if not taskid:
            print("Error, TaskId must be passed when option is retrieve.")
            sys.exit(1)
        if not quiet: print("[*] Retrieving report...")
        retrieveReport (apitoken, taskid)
    
    if not quiet: print("[*] Done!")

# -------------- Main Section ----------------------
if __name__ == '__main__':
    main()
