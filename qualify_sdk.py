#!/usr/bin/python -u
# pylint: disable=line-too-long
# pylint: disable=too-many-locals
"""
# Copyright (c) 2023 Nutanix Inc. All rights reserved.
#
# Author: raeesul.asad@nutanix.com
#
# This script can be used to qualify sdk versions in Nutanix V4 SDK namespaces.
#
#
#   Sample command to execute this script :-
#     python qualify_sdk.py  \
#          --job_profile "DP_SDK_QUAL_JOBPROFILE_MASTER"
#          --name_space "dataprotection"
#          --v4_version "v4.0.a5"
#          --pc_branch "master"
#          --git_username "githubusersdk"
#          --git_token "whp_Mq0k9NrdwwC1pprF2iqOp6o1hzIyLP07eyuq"
#          --jita_username "jita_user"
#          --jita_password "jita_pass"
#
#
#
#  Each parameter is explained below:-
#   *Parameters:-
#  1: --job_profile : name of job profile setup with tests to qualify sdk .
#  2: --name_space : name of namespace need to be qualified
#       (Eg:- dataprotection or  storage or networking, etc).
#  3: --v4_version : v4 version to be qualified in namespace given
#       (Eg:- v4.0.a3 or v4.0.a4 or v4.0.a5, etc )
#  4: --pc_branch : PC branch name where sdk need to be qualified
#       (Eg:- master or fraser-2023.3-stable-pc-0, etc)
#  5 & 6: --git_username and --git_token of user who runs this script and publish
#     it in github portal. Use https://github.com/settings/personal-access-tokens/new to
#     generate git_token if you don't have one .
#  7 & 8:  --jita_username & --jita_password of user who wants to run job profile
#  to qualify sdks .
#
#
#
# Qualification results will be captured here :
#  https://github.com/raeesulgit/ntnx_v4_sdk_qualification/tree/main/qualified_sdks
#
# More info about this script is available at : https://github.com/raeesulasaad/ntnx_v4_sdk_qualification/blob/main/README.md
#
#
"""
from datetime import datetime
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import time
import argparse
from requests.auth import HTTPBasicAuth
import urllib3
import requests
from git import Repo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Expand below mapping if needed for new namespaces
NAMESPACE_TO_SDK_NAME_MAPPING = {
  "dataprotection": "ntnx-dataprotection-py-client",
  "storage": "ntnx-storage-py-client",
  "iam" : "ntnx-iam-py-client",
  "files" : "ntnx-files-py-client",
  "lcm" : "ntnx-lcm-py-client",
  "licensing": "ntnx-licensing-py-client",
  "microseg": "ntnx-microseg-py-client",
  "monitoring": "ntnx-monitoring-py-client",
  "networking":"ntnx-networking-py-client",
  "prism": "ntnx-prism-py-client",
  "releasemgmt": "ntnx-releasemgmt-py-client",
  "security": "ntnx-security-py-client",
  "vmm": "ntnx-vmm-py-client",
  "aiops": "ntnx-aiops-py-client",
  "cloud": "ntnx-cloud-py-client",
  "clustermgmt":"ntnx-clustermgmt-py-client"
}

DEFAULT_WAIT_TIME_AFTER_ONE_RUN = 3600
DEFAULT_JITA_TASK_POLL_TIME = 600
DEFAULT_MAX_LIMIT_FOR_LOGS = 5000
JITA_BASE_URL = "https://jita-web-server-1.eng.nutanix.com/api/v2/"
JP_GET_URL = JITA_BASE_URL + "job_profiles"
TASK_GET_URL = JITA_BASE_URL + "agave_tasks"
SDK_BASE_URL = "https://developers.internal.nutanix.com/api/v1/namespaces"
GITHUB_URL = "github.com/raeesulasaad/ntnx_v4_sdk_qualification"
def find_jp_id(**kwargs):
  """
  This method returns job profile id of JOB_PROFILE_NAME.
  Returns:
    ID of job profile.
  """
  job_profile = kwargs.get("job_profile")
  print("Fetching job profile ID of %s" %job_profile)
  get_jp_id_url = JP_GET_URL + "?search=%5E{0}%24".format(job_profile)
  jp = requests.get(get_jp_id_url, verify=False)
  jp_json = jp.json()
  jp_id = jp_json['data'][0]['_id']['$oid']
  return jp_id

def find_latest_sdk(**kwargs):
  """
  This method fetches latest sdk version available for  name_space/pc_branch/v4_version
  Returns:
    sdk version
  """
  name_space = kwargs.get("name_space")
  v4_version = kwargs.get("v4_version")
  pc_branch = kwargs.get("pc_branch")
  if pc_branch == "master":
    pc_branch = "main"
  sdk_url = f"{SDK_BASE_URL}/{name_space}/versions/{v4_version}/artifact-versions?branchName={pc_branch}"
  sdk_resp = requests.get(sdk_url, verify=False)
  sdk_resp_json = sdk_resp.json()
  try:
    latest_sdk_version = sdk_resp_json['versions'][0]['artifact_version'].split('-')[0]
  except KeyError:
    print("Unable to fetch sdk version using %s, please check parameter --name_space or --v4_version or --pc_branch is set correctly " % sdk_url)
    return None
  print("Latest sdk version available in %s namespace is %s " % (name_space, latest_sdk_version))
  return latest_sdk_version

def update_jp_with_latest_sdk(jobprofileid, sdk_name, sdk_version, **kwargs):
  """
  This method updates job profile with sdk_version
  Args:
      jobprofileid(str): ID of job profile.
      sdk_name (str) : sdk name
      sdk_version(str): sdk version
  """
  job_profile = kwargs.get("job_profile")
  jp_get_by_id_url = JP_GET_URL + "/" + jobprofileid
  jp = requests.get(jp_get_by_id_url, verify=False)
  jp_json = jp.json()
  jp_json['data']['sdk_installation_options']['override_sdks'] = sdk_name+'==' + sdk_version
  jp_put_url = JP_GET_URL + "/" + jobprofileid
  requests.put(jp_put_url, json=jp_json['data'], auth=HTTPBasicAuth('jita', 'jita'), verify=False)
  time.sleep(10)
  jp = requests.get(jp_get_by_id_url, verify=False)
  jp_json = jp.json()
  pass_message = "Job profile %s is updated with latest sdk %s==%s" % (job_profile, sdk_name, sdk_version)
  fail_message = "Failed to update Job profile %s with latest sdk %s==%s" % (job_profile, sdk_name, sdk_version)
  assert jp_json['data']['sdk_installation_options']['override_sdks'].split('==')[1] == sdk_version, fail_message
  print(pass_message)

def trigger_jp_with_latest_sdk(jobprofileid, **kwargs):
  """
  This method triggers job profile
  Args:
      jobprofileid(str): ID of job profile.
  Returns:
    task_id of jita task
  """
  job_profile = kwargs.get("job_profile")
  jita_username = kwargs.get("jita_username")
  jita_password = kwargs.get("jita_password")

  jp_trigger_url = JP_GET_URL + "/" + jobprofileid+ "/trigger"
  trigger_resp = requests.post(jp_trigger_url, json=dict(), auth=HTTPBasicAuth(jita_username, jita_password), verify=False)
  if trigger_resp.json()['success']:
    task_id = trigger_resp.json()['task_ids'][0]['$oid']
    pass_message = "Job profile %s is triggered with task_id %s" % (
      job_profile, task_id)
    print(pass_message)
    print("Jita link : https://jita.eng.nutanix.com/results?task_ids=%s" %task_id)
    return task_id
  print("Failed to trigger job profile %s with latest sdk" % job_profile)
  return None


def wait_for_jp_trigger_task_completion(task_id, **kwargs):
  """
  This method waits for jita task completion .
  Args:
      task_id(str): ID of jita task.
  """
  job_profile = kwargs.get("job_profile")
  time.sleep(20)
  task_get_by_id_url = TASK_GET_URL + "/" + task_id
  is_jp_trigger_task_running = 1
  while is_jp_trigger_task_running:
    task_resp = requests.get(task_get_by_id_url, verify=False)
    task_details = task_resp.json()
    if ('TASK_COMPLETED' in task_details['data']['stages']) or ('TASK_KILLED' in task_details['data']['stages']):
      is_jp_trigger_task_running = 0
    else:
      running_msg = "Job profile %s triggered with task_id %s is still running, polling it after %s seconds" % (
        job_profile, task_id, DEFAULT_JITA_TASK_POLL_TIME)
      print(running_msg)
      time.sleep(DEFAULT_JITA_TASK_POLL_TIME)
def validate_jp_trigger_task(task_id):
  """
  This method validates jita task .
  Args:
      task_id(str): ID of jita task.
  Returns :
    True , if all tests passed in jita task
    False , if any test failed in jita task
  """
  task_get_by_id_url = TASK_GET_URL + "/" + task_id
  task_resp = requests.get(task_get_by_id_url, verify=False)
  task_details = task_resp.json()
  total_tests = task_details['data']['test_result_count']['Total']
  passed_tests = task_details['data']['test_result_count']['Succeeded']
  return passed_tests == total_tests

def fetch_wait_time(jobprofileid, status):
  """
  This method fetches wait time before going for
   next iteration of job profile execution .
   User can configure it from job profile.
   With default , 3600 seconds of delay is used betweeniterations .
  Args:
      jobprofileid(str): ID of job profile.
      status (str): status of jita task .
  Returns :
    wait_time(str)
  """
  jp_get_by_id_url = JP_GET_URL + "/" + jobprofileid
  jp = requests.get(jp_get_by_id_url, verify=False)
  jp_json = jp.json()
  wait_time = DEFAULT_WAIT_TIME_AFTER_ONE_RUN
  try:
    if status == "passed":
      wait_time = jp_json['data']['tester_container_config']['environment']['wait_time_post_success']
    else:
      wait_time = jp_json['data']['tester_container_config']['environment']['wait_time_post_failure']
  except KeyError:
    pass
  return int(wait_time)

def apply_results_and_git_push(task_id, sdk_name, sdk_version, status, **kwargs):
  """
  This method saves results of jita task and uploads it to GITHUB portal.
  Args:
      task_id(str): ID of jita task .
      sdk_name(str) : sdk name
      sdk_version (str): sdk_version used to qualify.
      status (str): status of jita task .
  """
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  full_local_path = "./sdk-qual-repo"+dt_string
  username = kwargs.get("git_username")
  password = kwargs.get("git_token")
  remote = f"https://{username}:{password}@{GITHUB_URL}.git"
  commit_message = "SDK qualification: "+sdk_name+"=="+sdk_version
  if not os.path.isdir(full_local_path):
    Repo.clone_from(remote, full_local_path)
  repo = Repo(full_local_path)
  origin = repo.remote(name='origin')
  origin.pull()
  if status == "passed":
    mark_sdk_qualified(full_local_path, sdk_name, sdk_version, **kwargs)
  save_logs(full_local_path, task_id, sdk_name, sdk_version, status, **kwargs)
  time.sleep(10)
  repo.git.add(all=True)
  repo.index.commit(commit_message)
  print("Pushing the results to https://%s/tree/main/qualified_sdks" % GITHUB_URL)
  origin.push()

def mark_sdk_qualified(repo_path, sdk_name, sdk_version, **kwargs):
  """
  This method update qualified sdk version if jita task passes.
  Args:
      repo_path(str): Local repo path for saving results.
      sdk_name (str): sdk name
      sdk_version (str): sdk_version used to qualify.
  """
  name_space = kwargs.get("name_space")
  v4_version = kwargs.get("v4_version")
  pc_branch = kwargs.get("pc_branch")
  sdk_folder = repo_path+"/qualified_sdks/"+name_space+"/"+pc_branch+"/"+v4_version+"/"
  if not os.path.isdir(sdk_folder):
    os.makedirs(sdk_folder)
  qual_file = sdk_folder+"latest_qualified_sdk.txt"
  print("Updating file %s with %s==%s " % (qual_file, sdk_name, sdk_version))
  with open(qual_file, 'w+') as fptr:
    fptr.write(sdk_name+"=="+sdk_version)
  fptr.close()

def save_logs(repo_path, task_id, sdk_name, sdk_version, status, **kwargs):
  """
  This method update logs of jita task.
  Args:
      repo_path(str): Local repo path for saving results.
      task_id(str): ID of jita task .
      sdk_name (str): sdk name.
      sdk_version (str): sdk_version used to qualify.
      status (str): status of jita task .
  """
  name_space = kwargs.get("name_space")
  v4_version = kwargs.get("v4_version")
  pc_branch = kwargs.get("pc_branch")
  log_url = "https://jita.eng.nutanix.com/results?task_ids=" + task_id
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logs_to_write = dt_string+ " : " + sdk_name+"=="+sdk_version + " : logs==" + log_url
  sdk_folder = repo_path+"/qualified_sdks/"+name_space+"/"+pc_branch+"/"+v4_version+"/"
  log_folder = sdk_folder+"logs/"+status
  log_file = log_folder+"/sdk_"+status+"_logs.txt"
  if not os.path.isdir(log_folder):
    os.makedirs(log_folder)
  with open(log_file, 'a+') as fptr:
    fptr.seek(0)
    lines = fptr.readlines()
  fptr.close()
  print("Updating log file %s with jita task url %s " % (log_file, log_url))
  with open(log_file, 'w+') as fptr:
    lines.insert(0, logs_to_write + "\n\n")
    lines = lines[:DEFAULT_MAX_LIMIT_FOR_LOGS]
    fptr.writelines(lines)
    fptr.close()

def get_input_args():
  """
    Get input args from commandline
  Returns:
    args object
  """
  arg_parse = argparse.ArgumentParser("Input Args")
  arg_parse.add_argument("--job_profile",
                         help="Job Profile Name created with tests to qualify SDK",
                         type=str, required=True)
  arg_parse.add_argument("--name_space",
                         help="Name space of sdk to qualify",
                         type=str, required=True)
  arg_parse.add_argument("--v4_version",
                         help="V4 version to qualify",
                         type=str, required=True)
  arg_parse.add_argument("--pc_branch",
                         help="PC Branch where sdk to qualify",
                         type=str, required=True)
  arg_parse.add_argument("--git_username",
                         help="Git user name for pushing the results to github repo",
                         type=str, required=True)
  arg_parse.add_argument("--git_token",
                         help="Git pass word for pushing the results to github repo",
                         type=str, required=True)
  arg_parse.add_argument("--jita_username",
                         help="Jita username for running jita jobs",
                         type=str, required=True)
  arg_parse.add_argument("--jita_password",
                         help="Jita password for running jita jobs",
                         type=str, required=True)
  args = arg_parse.parse_args()
  return args

def qualify_sdk():
  """
  This method automates end to end process of sdk qualification
  """
  iteration = 1
  kwarg_namespace = get_input_args()
  kwargs = vars(kwarg_namespace)
  jobprofileid = find_jp_id(**kwargs)
  name_space = kwargs.get("name_space")
  sdk_name = NAMESPACE_TO_SDK_NAME_MAPPING[name_space]
  while 1:
    print("\n")
    print("*"*41+ "Starting  Iteration : %s  "  %iteration+ "*"*41)
    sdk_version = find_latest_sdk(**kwargs)
    update_jp_with_latest_sdk(jobprofileid, sdk_name, sdk_version, **kwargs)
    trigger_task_id = trigger_jp_with_latest_sdk(jobprofileid, **kwargs)
    wait_for_jp_trigger_task_completion(trigger_task_id, **kwargs)
    is_jp_passed = validate_jp_trigger_task(trigger_task_id)
    if is_jp_passed:
      apply_results_and_git_push(trigger_task_id, sdk_name, sdk_version, "passed", **kwargs)
      wait_time_post_success = fetch_wait_time(jobprofileid, "passed")
      print(name_space+" sdk %s qualified, waiting for %s seconds before checking for new sdk version " % (sdk_version, wait_time_post_success))
      time.sleep(wait_time_post_success)
    else:
      apply_results_and_git_push(trigger_task_id, sdk_name, sdk_version, "failed", **kwargs)
      wait_time_post_failure = fetch_wait_time(jobprofileid, "failed")
      print("Some tests did not pass, waiting for %s seconds to re-trigger the job profile again " % wait_time_post_failure)
      time.sleep(wait_time_post_failure)
    print("*"*41+ " Iteration : %s  completed"  %iteration+ "*"*41)
    print("\n")
    iteration+=1

if __name__ == "__main__":
  qualify_sdk()
