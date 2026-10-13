#!/usr/bin/env python3
# coding: utf-8
# vi: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import json
import base64
import argparse
import requests
import re
import sys
import time
import logging
import os
from pathlib import Path
#Create empty dictionary to store list of scan reports
scan_confs_list = {}

# Define logging levels and their corresponding formats 
LEVELS = {
    "error": "%(asctime)s %(module)s - %(levelname)-8s - %(message)s (func:%(funcName)s line:%(lineno)d)",
    "critical": "%(asctime)s %(module)s - %(levelname)-8s - %(message)s (func:%(funcName)s line:%(lineno)d)",
    "info": "%(asctime)s %(module)s - %(levelname)-8s - %(message)s",
    "debug": "%(asctime)s %(module)s - %(levelname)-8s - %(message)s",
    "warning": "%(message)s",
}
# Set up our logging function to log when we say and how we define each LEVELS log line
class CustomLogger(logging.Logger):
    def __init__(self, name, level, quiet=False, verbose=False):
        super().__init__(name)
        self.setLevel(level)
        self.quiet = quiet
        self.verbose = verbose

    def warning(self, message, *args, **kwargs): # Only print warning if quiet is True
        #if self.quiet:  #commented out in this particular script to always print warning no matter what
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(LEVELS["warning"]))
            self.addHandler(handler)
            super().warning(message, *args, stacklevel=2, **kwargs)
            self.removeHandler(handler)

    def error(self, message, *args, **kwargs):  # Always prints
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LEVELS["error"], "%Y-%m-%d %H:%M:%S"))
        self.addHandler(handler)
        super().error(message, *args, stacklevel=2, **kwargs)
        self.removeHandler(handler)

    def critical(self, message, *args, **kwargs):  # Always prints
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LEVELS["critical"], "%Y-%m-%d %H:%M:%S"))
        self.addHandler(handler)
        super().critical(message, *args, stacklevel=2, **kwargs)
        self.removeHandler(handler)

    def info(self, message, *args, **kwargs): # Only prints if quiet is False
        if not self.quiet:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(LEVELS["info"], "%Y-%m-%d %H:%M:%S"))
            self.addHandler(handler)
            super().info(message, *args, stacklevel=2, **kwargs)
            self.removeHandler(handler)

    def debug(self, message, *args, **kwargs): # Only prints if verbose is True and quiet is False
        if self.verbose and not self.quiet:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(LEVELS["debug"], "%Y-%m-%d %H:%M:%S"))
            self.addHandler(handler)
            super().debug(message, *args, stacklevel=2, **kwargs)
            self.removeHandler(handler)

def testUUID(token):
    return re.match("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", token)

def testConfName(name):
    return re.match (r"^[a-zA-Z0-9_\-]+$", name)

def testFileName (filename):
    return re.match (r"^[a-zA-Z0-9\s_\-\/\.]{5,256}$", filename)

def enforce_https(url):
    if url.startswith("http://"):
        url = "https://" + url[7:]  # Replace "http://" with "https://"
    elif not url.startswith("https://"):
        url = "https://" + url
    return url

# Generate a default scan V2 config
def gen_default_config(token: str, name: str, aid: str):
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanConfigurations/default"
    headers = {"accept": "application/json", "X-API-KEY": token}

    payload = {"name": name, "reference": True}
    response = requests.post(url, data=json.dumps(payload), headers=headers) 

    if response.status_code != 200:
        logger.info(f"Error: unable to create default scan configuration {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)

# We need to use this call to retrieve a scan conf name from its API UUID.
def retrieve_config_names (token: str, aid: str):
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanConfigurations"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Error: unable to retrieve scan lists {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)
    else:
        for c in response.json()['list']:
            scan_conf_name = c['configuration']['name']
            scan_conf_id = c['configuration']['id']
            scan_confs_list.update ({scan_conf_name:scan_conf_id})

# We need to use this call to retrieve a default scan SQG status from its API UUID.
def retrieve_SQG(token: str, aid: str) -> dict:
    url = f"{PLATFORM}/api/v2/apis/{aid}/branches/main?readScan=true"
    headers = {"accept": "application/json", "X-API-KEY": token}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        return {
            "pass": False,
            "error": True,
            "message": f"HTTP {response.status_code} {response.reason}",
            "raw": response.text
        }

    data = response.json()
    scan = data.get("scan") or {}
    result = {
        "pass": scan.get("sqgPass"),
        "error": False,
        "api_id": data.get("id", aid),
        "api_type": data.get("apiType"),
        "branch": data.get("name", "main"),
        "state": scan.get("state"),
        "exit_code": scan.get("exitCode"),
        "is_complete": scan.get("isComplete"),
        "is_processed": scan.get("isProcessed"),
        "scan_id": scan.get("scanId"),
        "scan_version": scan.get("scanVersion"),
        "last_scan": scan.get("last"),
        "request_done": scan.get("requestDone"),
        "issues": {
            "critical": scan.get("numCriticals", 0),
            "high": scan.get("numHighs", 0),
            "medium": scan.get("numMediums", 0),
            "low": scan.get("numLows", 0),
            "info": scan.get("numInfos", 0),
            "total": scan.get("totalIssues", 0),
        },
        "reasons": [],
        "blocking_rules": [],
        "blocking_sqg_ids": [],
    }

    if result["pass"] is None:
        result["pass"] = False
        result["reasons"].append("SQG status unavailable (sqgPass missing from response)")
        return result

    if result["pass"] is False:
        if result["state"] and result["state"] != "success":
            result["reasons"].append(f"Scan state is '{result['state']}' not 'success'")
        if result["exit_code"] not in (0, None):
            result["reasons"].append(f"Non-zero exit code ({result['exit_code']})")
        if result["issues"]["total"] == 1000 or result["state"] == "issuesLimitReached":
            result["reasons"].append("Issue limit reached — results truncated at 1000")
        if result["is_processed"] is False:
            result["reasons"].append("Scan has not been processed yet")
        if result["is_complete"] is False:
            result["reasons"].append("Scan has not completed yet")
        if (result["issues"]["critical"] or result["issues"]["high"] or result["issues"]["medium"]):
            result["reasons"].append(
                "Severity findings present "
                f"(C={result['issues']['critical']} "
                f"H={result['issues']['high']} "
                f"M={result['issues']['medium']} "
                f"L={result['issues']['low']})"
            )
        scan_id = result["scan_id"]
        if scan_id:
            compliance = retrieve_sqg_blocking_rules(token, scan_id)
            if compliance["ok"]:
                result["blocking_rules"] = compliance["blocking_rules"]
                result["blocking_sqg_ids"] = compliance["blocking_sqg_ids"]
                if compliance.get("acceptance") == "no":
                    result["reasons"].append("Compliance acceptance is 'no'")
            else:
                result["reasons"].append(
                    f"Could not fetch compliance blocking rules: {compliance.get('message')}"
                )
    return result

def retrieve_sqg_blocking_rules(token: str, scan_id: str) -> dict:
    url = f"{PLATFORM}/api/v2/sqgs/reportComplianceStatus"
    headers = {"accept": "application/json", "X-API-KEY": token}
    params = {"taskId": scan_id, "reportType": "scan"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except requests.RequestException as e:
        return {
            "ok": False,
            "blocking_rules": [],
            "blocking_sqg_ids": [],
            "acceptance": "unknown",
            "message": f"Compliance status request failed: {e}",
        }

    if resp.status_code != 200:
        return {
            "ok": False,
            "blocking_rules": [],
            "blocking_sqg_ids": [],
            "acceptance": "unknown",
            "message": f"Compliance status HTTP {resp.status_code} {resp.reason}",
            "raw": resp.text,
        }

    payload = resp.json()

    rules = []
    sqg_ids = []
    for pd in payload.get("processingDetails") or []:
        sqg_id = pd.get("blockingSqgId")
        if sqg_id:
            sqg_ids.append(sqg_id)
        for r in (pd.get("blockingRules") or []):
            rules.append(r)

    # de-dupe but keep order
    def dedupe(seq):
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return {
        "ok": True,
        "blocking_rules": dedupe(rules),
        "blocking_sqg_ids": dedupe(sqg_ids),
        "acceptance": payload.get("acceptance", "unknown"),
    }

# We use this call to retrieve the list of scan ids from the scan conf name.
def retrieve_config_id(token: str, name: str, aid: str, token_default: bool = False):
    scan_conf_id = ""
    scan_conf_id_count = 0
    found_config_id = False
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanConfigurations"
    headers = {"accept": "application/json", "X-API-KEY": token}

    while not found_config_id:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.info(f"Error: unable to retrieve scan lists {response.status_code} : {response.reason} - {response.text}")
            sys.exit(1)
        else:
            scan_conf_id_count += 1
            logger.debug(f"Config retrieval attempt #{scan_conf_id_count}")
            
            for c in response.json()['list']:
                logger.debug(f"Config Response: {c['configuration']['name']} is {c['configuration']['id']}")
                if c['configuration']['name'] == name:
                    scan_conf_id = c['configuration']['id']
                    found_config_id = True
                    break

            # After iterating through the list, check if attempts reached 20
            if scan_conf_id_count == 20:
                if token_default:
                    logger.debug(f"Did not find an existing scan config for {name}.  Since --default is enabled, stop search and generate a new config")
                    scan_conf_id = "none"
                    found_config_id = True
                else:
                    logger.error(f"Error: unable to find a scan configuration for name {name} after 20 attempts. Exiting")
                    sys.exit(1)
        time.sleep(1)
    return scan_conf_id

# This will retrieve a config for an existing scan and save it to a file
def retrieve_config (token: str, name: str, sid: str):
    url =  f"{PLATFORM}/api/v2/scanConfigurations/{sid}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers) 

    if response.status_code != 200:
        logger.info(f"Error: unable to retrieve config {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)
    else: 
        config = response.json()['file']
        token = response.json()['token']
        # This is a base64 object - Let's decode it
        contents = json.loads(base64.decodebytes(config.encode("utf-8")))
        
        filename = f"scanconf_{name}.json"
        try:
            with open (filename, 'w') as outfile:
                json.dump (contents, outfile, indent=2)
            logger.info(f"Saved default scan configuration as: {filename}")
            logger.info(f"Use this scan token to run the scan: {token}")
            if token_file:
                write_token(token)
            logger.warning(f"{token},{filename}")
        finally:
            outfile.close()

# This will delete an existing scan config
def delete_config (token: str, sid: str):
    url =  f"{PLATFORM}/api/v2/scanConfigurations/{sid}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.delete(url, headers=headers) 

    if response.status_code != 200:
        logger.info(f"Error: unable to delete config {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)
    else: 
        logger.info("Scan config deleted successfully")

# This will update a named scan configuration
def update_config(token: str, name: str, aid: str, scanconf_filename: str):
    #Initialize scan token value
    scan_token = None

    #Load file and base64 encode it.  File will be closed() after the with statement is executed, even if there's an exception.
    try:
        if os.path.exists(scanconf_filename):
            logger.debug(f"Attempting to open {scanconf_filename}")
            with open(scanconf_filename, 'r') as contents:
                b64encoded_scanconf = base64.b64encode(contents.read().encode('utf-8')).decode('utf-8')
        else:
            logger.error(f"The file {scanconf_filename} does not exist.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred while processing the file: {e}")
        sys.exit(1)

    url =  f"{PLATFORM}/api/v2/apis/{aid}/branches/main/scanConfigurations"
    headers = {"accept": "application/json", "X-API-KEY": token}
    payload = {"name": name, "file": b64encoded_scanconf }
    response = requests.post(url, data=json.dumps(payload), headers=headers) 

    if response.status_code != 200:
        logger.error(f"Error: unable to update scan configuration {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)
    else:
        # Let's retrieve the configuration and make sure its valid.
        taskId = response.json()['id']

        logger.info("Verifying Scan Configuration...")
        conf_id = retrieve_config_id (token, name, aid)
        url =  f"{PLATFORM}/api/v2/scanConfigurations/{conf_id}"
        headers = {"accept": "application/json", "X-API-KEY": token}

        # local variables
        found_config = False
        # Initialize loop
        loop_counter = 0
        while not found_config:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Error: unable to retrieve scan configuration details - Error Code: {response.status_code} : {response.reason} - {response.text}")
                sys.exit(1)
            else:
                loop_counter+=1
                logger.debug(f"TaskID retrieval attempt #{loop_counter}")
                if response.json()['taskId'] == taskId:
                    found_config = True
                    break
                if loop_counter == 20:
                    logger.error(f"Error: unable to find new configuration information after 20 attempts.  Exiting")
                    sys.exit(1)
            time.sleep(1)

        # If we get here, the conf report is for the conf we just updated.
        is_config_valid = response.json()['valid']
        scan_token = response.json()['token']
        if is_config_valid:
            logger.info("Configuration is valid and can be used")
            logger.info(f"Scan token for the updated scan config is {scan_token}")
            if token_file:
                write_token(scan_token)
            logger.warning(f"{scan_token}")
            return conf_id
        else:
            logger.error("Configuration is not valid - Saving report")
            #Load report and base64 decode it.
            report_filename = f"scanconf_analysis_report_{name}.json"
            report = response.json()['reportFile']
            contents = json.loads(base64.decodebytes(report.encode("utf-8")))
            try:
                with open (report_filename, 'w') as outfile:
                    json.dump (contents, outfile, indent=2)
                logger.error(f"Saved scan configuration analysis report as: {report_filename}.  THE CONFIG HAS NOT BEEN UPDATED!")
                logger.warning(f"{report_filename}")
                sys.exit(1)
            finally:
                outfile.close()

def retrieve_token (token: str, sid: str):
    url =  f"{PLATFORM}/api/v2/scanConfigurations/{sid}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers) 

    if response.status_code != 200:
        logger.info(f"Error: unable to retrieve scan config {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)
    else: 
        token = response.json()['token']
        return token

# This call list all scan reports available for this API. You can use the task ID to retrieve the report and 
# the scan conf ID to match conf that was used, should you have several ones.
def list_reports(token: str, aid: str):
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanReports"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.info(f"Error: unable to list scan reports {response.status_code} : {response.reason} - {response.text}")
    else:
        # print all the TaskID / scanConfId pairs.
        if len(response.json()['list']) == 0: 
            logger.info(f"[*] No reports found for API {aid}")
        else:
            if quiet: logger.warning("taskID,scanConfID,scanConfName")
        for c in response.json()['list']:
            if c['configuration'] == None:
                taskId = c['report']['taskId']
                scan_conf_name = c['report']['name']
                logger.info(f"Report with ID: {taskId} is available for SaaS Scan V1 with name {scan_conf_name}")
                if quiet: logger.warning(f"{taskId},None,{scan_conf_name}")
            else:
                taskId = c['report']['taskId']
                scan_conf_name = c['configuration']['name']
                scan_conf_id = scan_confs_list.get(scan_conf_name)
                if  scan_conf_name == "legacy":
                    logger.info(f"Report with ID: {taskId} is available for Scan V1 and name {scan_conf_name}")
                    if quiet: logger.warning(f"{taskId},{scan_conf_id},{scan_conf_name}")
                else: 
                    logger.info(f"Report with ID: {taskId} is available for Scan V2 conf with ID {scan_conf_id} and name {scan_conf_name}")
                    if quiet: logger.warning(f"{taskId},{scan_conf_id},{scan_conf_name}")

def retrieveReport(token: str, aid: str, name: str):
    # This call retrieves a report via its name
    url =  f"{PLATFORM}/api/v2/apis/{aid}/scanReports"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.info(f"Error: unable to list scan reports {response.status_code} : {response.reason} - {response.text}")
    else:
        # print all the TaskID / scanConfId pairs.
        if len(response.json()['list']) == 0: 
            logger.error(f"No reports found for API {aid}.  Exiting...")
            sys.exit(1)
    
    found_match = False
    for c in response.json()['list']:
        if c['configuration'] is None:
            logger.debug("Found Saas report, skipping...")
            continue  # Skip to the next iteration if configuration is None

        if 'name' in c['configuration'] and c['configuration']['name'] == name:
            found_match = True
            taskId = c['report']['taskId']
            scan_conf_id = scan_confs_list.get(name)
            logger.info(f"Found Scan Report with ID: {taskId} for Scan V2 conf with ID {scan_conf_id} and name {name}")
            logger.warning("taskID,scanConfID,scanConfName"), logger.warning(f"{taskId},{scan_conf_id},{name}")
            break  # Exit the loop early since you found a match

        logger.debug(f"Scan V2 report for config {name} is not the droid we're looking for...")

    if not found_match:
        logger.error(f"Did not find a scan report for the config '{name}'... Exiting")
        sys.exit(1)

    url =  f"{PLATFORM}/api/v2/scanReports/{taskId}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers) 

    if response.status_code != 200:
        logger.error(f"Error: unable to retrieve scan report {response.status_code} : {response.reason} - {response.text}")
    else:
        report_b64 = response.json()['file']
        log_b64 = response.json()['logFile']
        report_json = json.loads(base64.decodebytes(report_b64.encode("utf-8")))
        log_asbytes = base64.decodebytes(log_b64.encode("utf-8"))
        log_text = log_asbytes.decode ('utf-8')
        logger.info(f"Saving report and log as files for scan config {name}")

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
            logger.warning("report_filename,log_filename"), logger.warning(f"{report_filename},{log_filename}")

def write_token(token: str):
    logger.info(f"Writing token to {token_file}")
    output_data = {"scan_token": token}
    with open(token_file, "w") as json_file:
        json.dump(output_data, json_file)

# set a scan v2 config to be the reference for SQGs
def set_reference(token: str, aid: str, conf_id: str):
    url =  f"{PLATFORM}/api/v2/apis/{aid}/branches/main/scanConfigurations/changeReference"
    headers = {"accept": "application/json", "X-API-KEY": token}
    payload = {"newReference": conf_id}
    response = requests.post(url, data=json.dumps(payload), headers=headers) 

    if response.status_code != 200:
        logger.info(f"Error: unable to set the reference to scan {name} with UUID {conf_id} - {response.status_code} : {response.reason} - {response.text}")
        sys.exit(1)
    else:
        # good to go
        logger.info(f"Successfully changed the reference to be scan configuration \"{name}\"")

def load_v2v1compat_payload(config_json_path: str) -> str:
    """
    Accepts a path to a JSON file. The file may be in one of three forms:
      1) Raw config object to be encoded:
         {"host": "...", "security": {...}, ...}
      2) {"config": "<base64-encoded-string>"}
      3) {"config": { ...raw config object... }}
    Returns the JSON-encoded payload string to send to the /compatibility endpoint,
    i.e. '{"config": "<base64>"}'.
    """
    if not os.path.isfile(config_json_path):
        logger.error(f"File not found: {config_json_path}")
        sys.exit(1)

    try:
        data = json.loads(Path(config_json_path).read_text())
    except Exception as e:
        logger.error(f"Failed to read/parse JSON from {config_json_path}: {e}")
        sys.exit(1)

    if isinstance(data, dict) and "config" in data:
        cfg = data["config"]
        if isinstance(cfg, str):
            # Already base64-encoded
            try:
                base64.b64decode(cfg.encode("utf-8"))
            except Exception as e:
                logger.error(f'Provided "config" string is not valid base64: {e}')
                sys.exit(1)
            payload = {"config": cfg}
        else:
            # Nested raw object
            try:
                encoded = base64.b64encode(json.dumps(cfg).encode("utf-8")).decode("utf-8")
            except Exception as e:
                logger.error(f'Unable to encode "config" object from {config_json_path}: {e}')
                sys.exit(1)
            payload = {"config": encoded}
    else:
        try:
            encoded = base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")
        except Exception as e:
            logger.error(f"Unable to encode raw config object from {config_json_path}: {e}")
            sys.exit(1)
        payload = {"config": encoded}

    return json.dumps(payload)

def v2platformscan(token: str, api_uuid: str, config_json_path: str, force: bool = False) -> str:
    """
    Create/update the unique 'v2 in v1 compatibility mode' scan configuration
    from a file payload, then start a SaaS scan.

    Unique v2inv1 config name on platform: 'scanConfigurationV2CompatibleV1'
    """
    compat_name = "scanConfigurationV2CompatibleV1"

    # 1) Locate existing compatibility config and optionally delete if forcing
    retrieve_config_names(token, api_uuid)
    scan_config_id = None
    create_new = True

    for confname, conf_id in scan_confs_list.items():
        if confname == compat_name:
            scan_config_id = conf_id
            logger.info(f"Found existing {compat_name} id {scan_config_id}")
            if force:
                logger.debug("Force enabled; deleting the existing compatibility config before recreating it...")
                delete_config(token, scan_config_id)
                scan_config_id = None
                create_new = True
            else:
                logger.info("Using existing v2-in-v1 scan config as-is (not forcing recreation).")
                create_new = False
            break

    # 2) (Re)create via /compatibility if needed, using the file-provided payload
    if create_new:
        payload = load_v2v1compat_payload(config_json_path)
        url = f"{PLATFORM}/api/v2/apis/{api_uuid}/branches/main/scanConfigurations/compatibility"
        headers = {"accept": "application/json", "content-type": "application/json", "X-API-KEY": token}
        resp = requests.post(url, data=payload, headers=headers)
        if resp.status_code != 200:
            logger.error(f"Compatibility config creation failed: {resp.status_code} {resp.reason} - {resp.text}")
            sys.exit(1)

        body = resp.json() if resp.text else {}
        success = body.get("success")
        scan_config_id = body.get("id")
        if not success or not scan_config_id:
            logger.error(f"Platform returned non-success creating compatibility config: {resp.status_code} body={resp.text}")
            sys.exit(1)

        # Verify it becomes visible (async platform delay is possible)
        verify_url = f"{PLATFORM}/api/v2/scanConfigurations/{scan_config_id}"
        attempts = 0
        while attempts < 10:
            check = requests.get(verify_url, headers={"accept": "application/json", "X-API-KEY": token})
            if check.status_code == 200:
                logger.debug("Compatibility scan configuration is now available.")
                break
            elif check.status_code == 403:
                logger.debug(f"Waiting for compatibility config to be generated (attempt {attempts+1}/10)...")
            else:
                logger.error(f"Error verifying compatibility config {scan_config_id}: {check.status_code} {check.reason} - {check.text}")
                sys.exit(1)
            attempts += 1
            time.sleep(1)
        else:
            logger.error(f"Timeout verifying compatibility config {scan_config_id} (still not visible after 10s).")
            sys.exit(1)

    # 3) Kick off the SaaS scan
    run_url = f"{PLATFORM}/api/v2/scanConfigurations/{scan_config_id}/scan"
    run_headers = {"accept": "application/json", "X-API-KEY": token}
    run_resp = requests.post(run_url, headers=run_headers)
    if run_resp.status_code != 200:
        logger.error(f"Scan submission failed: {run_resp.status_code} {run_resp.reason} - {run_resp.text}")
        sys.exit(1)

    run_body = run_resp.json() if run_resp.text else {}
    success = run_body.get("success")
    scan_id = run_body.get("id")
    if not success or not scan_id:
        logger.error(f"Platform returned non-success after scan submission: {run_resp.status_code} body={run_resp.text}")
        sys.exit(1)

    logger.info(f"Started 'v2-in-v1 compatibility' SaaS scan. config_id={scan_config_id} scan_id={scan_id}")
    return scan_id

def wait_for_scan_completion(token: str, api_uuid: str, expected_scan_id: str | None = None, timeout: int = 1800, interval: int = 10):
    """
    Polls:
      GET {PLATFORM}/api/v2/apis/{api_uuid}/branches/main/scanReports
    until a report appears whose report.taskId == expected_scan_id.
    Returns the matched item: {"configuration": {...} | null, "report": {...}}.
    """
    url = f"{PLATFORM}/api/v2/apis/{api_uuid}/branches/main/scanReports"
    headers = {"accept": "application/json", "X-API-KEY": token}
    deadline = time.time() + timeout

    while time.time() < deadline:
        resp = requests.get(url, headers=headers)
        if resp.status_code in (403, 404):
            logger.debug(f"{resp.status_code} from scanReports; retrying in {interval}s")
            time.sleep(interval)
            continue
        if resp.status_code != 200:
            logger.error(f"Failed to poll scanReports: {resp.status_code} {resp.reason} {resp.text}")
            sys.exit(1)

        data = resp.json() or {}
        for item in data.get("list", []) or []:
            rep = (item or {}).get("report") or {}
            if rep.get("taskId") == scan_id:
                raw_sqg = rep.get("sqgPass")
                sqg_pass = raw_sqg if isinstance(raw_sqg, bool) else str(raw_sqg).strip().lower() in ("true","1","yes")
                logger.debug("sqgPass (raw)=%r", raw_sqg)
                return sqg_pass

        logger.debug(f"scanId {expected_scan_id} not present yet; sleeping {interval}s")
        time.sleep(interval)

    logger.error(f"Timeout waiting for report with taskId {expected_scan_id} after {timeout} seconds")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='42Crunch Conformance Scan v2 Configuration')
    subparsers = parser.add_subparsers(description="Options for --action (required)")
    parser.add_argument('-q', "--quiet", default=False, action="store_true", help="Quiet output - only minimal is shown")
    parser.add_argument('-v', '--verbose', default=False, action="store_true", help="Enable verbose")
    parser.add_argument("-c", "--credentials", required=True, help="API key")  
    parser.add_argument('-p', '--platform',  required=False, default='https://us.42crunch.cloud', help="Default is https://us.42crunch.cloud", type=enforce_https)
    parser.add_argument("-a", "--api_uuid", required=True, help="API UUID")
    parser.add_argument('-n', "--config_name", required=False, default="Defaultv2Config", help="Scan configuration friendly name")
    parser.add_argument('-cf', "--config_filename", required=False, help="Scan configuration filename", default="scanconf_Defaultv2Config.json")
    parser.add_argument('-vf', "--v2inv1_config", required=False, help='Path to JSON payload for v2-in-v1 compatibility mode (raw object or {"config": ...})')
    parser.add_argument("-t", "--token_file", help="filename to output the scan token - ie token.json - used with create_conf, upload_conf, or get_token")
    parser.add_argument("-r", "--reference", default=False, action="store_true", help="During create_conf, upload_conf, regen_conf, and get_token - set the named scan config to be the reference")
    parser.add_argument("-d", "--default", required=False, default=False, action="store_true", help="During get_token, if a config does not exist, create a default one")
    parser.add_argument("-f", "--force", required=False, default=False, action="store_true", help="During v2platformscan, if a config already exists, overwrite it")
    parser.add_argument("--wait", action="store_true", help="Wait for the SaaS scan to finish and exit depending on scan result")
    parser.add_argument("--action", required=True, help="Action to perform:")
    subparsers.add_parser("list_reports", help="List all scan reports available for an API")
    subparsers.add_parser("get_report", help="Get associated scan report for -n/--config_name")
    subparsers.add_parser("get_sqg", help="Get the SQG Status of the associated API UUID")
    subparsers.add_parser("get_token", help="Get the scan token for -n/--config_name.  Optionally provide -d/--default")
    subparsers.add_parser("create_conf", help="Create a new scan configuration - if named config already exists, it will be overwritten with a DEFAULT scan config. This is good for refreshing your scan config if your OAS has been modified.")
    subparsers.add_parser("delete_conf", help="Delete scan config -n/--config_name")
    subparsers.add_parser("v2platformscan", help="Run a v2-in-v1 compatibility SaaS/Platform scan using a config from JSON file")
    subparsers.add_parser("download_conf", help="Download the JSON scan configuration file for config -n/--config_name")
    subparsers.add_parser("upload_conf", help="Upload a scan config for config -n/--config_name.  Requires -f/--config_filename")
    subparsers.add_parser("set_reference", help="Set the reference scan config for SQG evaluation")
    args = parser.parse_args()

    global PLATFORM, token_file
    quiet = args.quiet
    verbose = args.verbose
    apitoken = args.credentials
    aid = args.api_uuid
    name = args.config_name
    filename = args.config_filename
    v2inv1_config = args.v2inv1_config
    reference = args.reference
    token_default = args.default
    token_file = args.token_file
    PLATFORM = args.platform
    action = args.action
    force = args.force
    wait = args.wait

    if sys.argv.count("--action") > 1:
        parser.error("--action may only be specified once")
        
    logger = CustomLogger(__name__, logging.DEBUG, quiet=quiet, verbose=verbose)
    logger.info(f"Using Platform {PLATFORM}")
    
    if not testUUID(aid):
        logger.error("Error, API ID must be in UUID format.")
        sys.exit(1)

    if not testConfName(name):
        logger.error("Error, wrong conf name - Only lowercase, uppercase, numbers, _ and - are accepted.")
        sys.exit(1)

    if not testFileName (filename):
        logger.error("Error, invalid filename - Only lowercase, uppercase, numbers, _,.,- and spaces are accepted.")
        sys.exit(1)

    if action == "create_conf":
        logger.info("Generating Scan Configuration")
        gen_default_config (apitoken, name, aid)
        scan_conf_id = retrieve_config_id (apitoken, name, aid)
        if not testUUID(scan_conf_id):
            logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
            sys.exit(1)
        else:
            if reference:
                logger.info(f"Setting this config to be the reference...")
                set_reference(apitoken, aid, scan_conf_id)
        logger.info(f"Retrieving configuration with id: {scan_conf_id}")
        retrieve_config (apitoken, name, scan_conf_id)
    elif action == "delete_conf":
        logger.info(f"Deleting Scan Configuration \"{name}\"")
        scan_conf_id = retrieve_config_id (apitoken, name, aid)
        if not testUUID(scan_conf_id):
            logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
            sys.exit(1)
        logger.debug(f"Deleting configuration with id: {scan_conf_id}")
        delete_config (apitoken, scan_conf_id)
    elif action == "download_conf":
        logger.info("Downloading Scan Configuration")
        scan_conf_id = retrieve_config_id (apitoken, name, aid)
        if not testUUID(scan_conf_id):
            logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
            sys.exit(1)
        logger.debug(f"Retrieving configuration with id: {scan_conf_id}")
        retrieve_config (apitoken, name, scan_conf_id)
    elif action == "get_token": 
        logger.info(f"Retrieving scan token for scan configuration: {name}")
        scan_conf_id = retrieve_config_id (apitoken, name, aid, token_default)
        if not testUUID(scan_conf_id) or scan_conf_id == "none":
            if token_default:
                logger.info("Generating scan configuration as one is not present")
                gen_default_config (apitoken, name, aid)
                scan_conf_id = retrieve_config_id (apitoken, name, aid)
                if not testUUID(scan_conf_id):
                    logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
                    sys.exit(1)
                logger.info(f"Retrieving configuration with id: {scan_conf_id}")
                retrieve_config (apitoken, name, scan_conf_id)
            else:
                logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
                sys.exit(1)
        else:
            logger.info(f"Retrieving token for scan config id: {scan_conf_id}")
            token = retrieve_token (apitoken, scan_conf_id)
            if not retrieve_token:
                logger.error(f"Unable to retrieve a token - {token}. Exiting...")
                sys.exit(1)
            else:
                logger.info(f"Token is {token}")
                if token_file:
                    write_token(token)
                logger.warning(f"{token}")
            if reference:
                logger.info(f"Setting this config to be the reference...")
                set_reference(apitoken, aid, scan_conf_id)
    elif action == "v2platformscan":
        if not v2inv1_config:
            logger.error("v2platformscan requires -vf/--v2inv1_config (v2-in-v1 compatibility config payload).")
            sys.exit(1)
        scan_id = v2platformscan(
            apitoken,
            aid,
            v2inv1_config,  # NOT -cf/--config_filename; this file is a different format
            force,
        )
        logger.info(f"SaaS scan ID is: {scan_id}")
        if wait:
            logger.info("Waiting for scan to complete...")
            sqg_status = wait_for_scan_completion(apitoken, aid, scan_id)
            if sqg_status is True:
                logger.info("SQG marked as Passed, exiting 0...")
                sys.exit(0)
            elif sqg_status is False:
                logger.info("SQG marked as Failed, exiting 1...")
                sys.exit(1)
            else:
                logger.error("SQG status not found in final report, exiting 1...")
                sys.exit(1)
        else:
            logger.info("Not waiting for scan completion; Exiting...")
            sys.exit(0)
    elif action == "list_reports":
        # Fill the config names dict.
        logger.info("Retrieving scan configurations list...")
        retrieve_config_names(apitoken, aid)
        logger.info(f"Retrieving scan reports...")
        list_reports (apitoken, aid)
    elif action == "get_report":
        # Fill the config names dict.
        logger.info("Retrieving scan configurations list...")
        retrieve_config_names(apitoken, aid)
        logger.info(f"Retrieving report for scan {name}...")
        retrieveReport (apitoken, aid, name)
    elif action == "get_sqg":
        logger.info("Retrieving SQG Results...")
        sqg_res = retrieve_SQG(apitoken, aid)
        if sqg_res["error"]:
            logger.error("Failed to retrieve SQG: %s", sqg_res["message"])
            sys.exit(1)
        logger.info(
            "SQG RESULT: %s | SQG rule(s): %s | state=%s | totalIssues=%s | scanId=%s",
            "PASS" if sqg_res["pass"] else "FAIL",
            sqg_res["blocking_rules"],
            sqg_res["state"],
            sqg_res["issues"]["total"],
            sqg_res["scan_id"]
        )
        if sqg_res["pass"]:
            sys.exit(0)
        # failure output
        logger.info("SQG FAILED for API %s", sqg_res["api_id"])
        for r in sqg_res["reasons"]:
            logger.debug("  - %s", r)
        logger.debug(
            "Issue counts: Crit=%s High=%s Med=%s Low=%s Info=%s",
            sqg_res["issues"]["critical"],
            sqg_res["issues"]["high"],
            sqg_res["issues"]["medium"],
            sqg_res["issues"]["low"],
            sqg_res["issues"]["info"]
        )
        sys.exit(1)
    elif action =="upload_conf":
        logger.info(f"Uploading {filename} into API {aid} for scan config {name}")
        scan_conf_id = update_config (apitoken, name, aid, filename)
        if not testUUID(scan_conf_id):
            logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
            sys.exit(1)
        else:
            if reference:
                logger.info(f"Setting this config to be the reference...")
                set_reference(apitoken, aid, scan_conf_id)
    elif action == "set_reference":
        logger.info(f"Updating reference scan configuration... to {name}")
        scan_conf_id = retrieve_config_id (apitoken, name, aid)
        if not testUUID(scan_conf_id):
            logger.error(f"Scan Configuration ID is not a valid UUID - {scan_conf_id}.  Exiting...")
            sys.exit(1)
        else:
            logger.info(f"Setting this config to be the reference...")
            set_reference(apitoken, aid, scan_conf_id)
    else:
        parser.error(f"Unknown action {action}")