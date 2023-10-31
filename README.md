

<h1 align="center">SDK qualification script README
</h1>

<h2>What is this script about</h2>

This script can be used to qualify sdk versions for V4 API namespaces .  It will run job profiles with latest available sdk version in namespace/pc_branch/v4_version given by user. Also script will publish the results in this github repo under [qualified_sdks/ ](https://github.com/raeesulasaad/ntnx_v4_sdk_qualification/tree/main/qualified_sdks/ )/<namespace>/<pc_branch>/<v4_version>. The script is designed in a way that it runs job profile in multiple iterations without any expiry. By means of this, we can ensure the automation of end to end processes of sdk qualification.

---


<h2>What does this script do  </h2>

i)Fetch latest available sdk version within NAMESPACE/PC_BRANCH/V4_VERSION given by user.

ii)Run job profile against it .

iii)Publish results to [qualified_sdks]([https://github.com/raeesulgit/ntnx_v4_sdk_qualification/tree/main/qualified_sdks](https://github.com/raeesulasaad/ntnx_v4_sdk_qualification/tree/main/qualified_sdks/))

iv)Repeat steps 1-3 .



---

<h2>How to execute the script</h2>

From jenkin pipeline [sdk_qualification_pipeline](https://phx-p10y-jenkins-harbinger-prod-6.p10y.eng.nutanix.com/job/sdk_qualification/build?delay=0):
   ```
    It is a parameterized jenkin pipeline where parameters JOB_PROFILE, PC_BRANCH, NAMESPACE and V4_VERSION can be passed while running .

   ```

 <img src="https://github.com/raeesulgit/ntnx_v4_sdk_qualification/blob/1e4e9956a3e766422314bed6f3e75bcb8e305310/src/params.png" width="800" height="600">
  
  
  Each parameter used in jenkin pipeline is explained below:-

   <h4>Parameters:- </h4>

         1: JOB_PROFILE : name of job profile setup with tests to qualify sdk .

         2: PC_BRANCH : PC branch name where sdk need to be qualified
            (Eg:- master or fraser-2023.3-stable-pc-0, etc)
  
         3: NAMESPACE : name of namespace need to be qualified
            (Eg:- dataprotection or  storage or networking, etc).
       
         4: V4_VERSION : v4 version to be qualified in namespace given
            (Eg:- v4.0.a3 or v4.0.a4 or v4.0.a5, etc )

    
         5: JITA_CREDENTIALS : jita credential of user who wants to run job profile
              to qualify sdks . With default , "jita" account will be used.

  


<h2>More options :- </h2>

1: While the pipeline job being run , you can modify the job profile like adding more tests or changing resources or adding nutest patch etc.
   Updated job profile will be considered for new iterations happening in pipeline job. 

2: If needed, User can control the frequency of jita execution from outside by modifying below two fields in job profile. 

```
 Field location: Edit Job profile >>Advanced options >>Tester Environment Configuration

   wait_time_post_failure: This indicates how much time script should wait before triggering next iteration if current iteration has test failures. 

   wait_time_post_success: This indicates how much time script should wait before triggering next iteration if current iteration is passed.
```

NOTE:  Script will run without any expiry so that it keeps qualifying sdks without any manual intervention .

---

<h2>Result Analysis</h2>

Test results will be published [qualified_sdks/ ](https://github.com/raeesulasaad/ntnx_v4_sdk_qualification/tree/main/qualified_sdks/ )  folder.

-  ![#c5f015](https://placehold.co/15x15/c5f015/c5f015.png) `If all tests added in job profile passes, sdk version will be considered as qualified and updated in qualified_sdks/<namespace>/<pc_branch>/<v4_version>/latest_qualified_sdk.txt. Logs for the same will be updated in qualified_sdks/<namespace>/<pc_branch>/<v4_version>/logs/passed/sdk_passed_logs.txt. Respective team can use this data to update sdk version used in nutest.`

- ![#f03c15](https://placehold.co/15x15/f03c15/f03c15.png) `If any test fails, sdk version will not be qualified, but logs for the failure will be updated in  qualified_sdks/<namespace>/<pc_branch>/<v4_version>/logs/failed/sdk_failed_logs.txt. Respective test/dev team can check failure reasons and address it while script being run in brackground. If it is a test issue, respective tester/dev needs to fix it in product or nutest and wait for next iteration in script to pick the changes. Also if fix is not merged tester/dev can add patch of dev change (as patched resource) or test change (as nutest patch url) in job profile while script is being run. In this manner we can ensure complete automation of sdk qualification..`
