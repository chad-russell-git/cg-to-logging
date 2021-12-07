# Events to Logs

## Overview

This is a sample function to write Events from the OCI Events service to OCI Logging.

### Architecture
![](images\Events_to_Logs.png)

## Prerequisites

### OCI Permissions
Below is an example of on OCI policy that grants the permissions required to preform the below tasks in this README.md.
```
# Needed to Create and deploy functions
allow group <group-name> to read objectstorage-namespaces in tenancy
allow group <group-name> to inspect compartments in tenancy
allow group <group-name> to read logging-family in tenancy
allow group <group-name>to read repos in tenancy
allow group <group-name>to manage repos in tenancy where target.repo.name = '/<repo-name>-/'
# Needed to create the policy to allow service connector to write the stream
allow group <group-name> to manage policies in compartment <compartment-name>
# Needed to create the Event Rule at the tenancy level
allow group <group-name>to manage cloudevents-rules in tenancy
allow group <group-name>to manage logging-family in compartment <splunk_comp_name>
allow group <group-name>to manage serviceconnectors in compartment <splunk_comp_name>
allow group <group-name>to manage streams in compartment <splunk_comp_name>
allow group <group-name>to manage functions-family in compartment <splunk_comp_name>
Allow group <group-name> to use apm-domains in compartment  <splunk_comp_name>
Allow group <group-name> to use virtual-network-family in compartment <compartment-name>
Allow group <group-name> to read metrics in compartment <compartment-name>
Allow group <group-name> to manage functions-family in compartment <compartment-name>
Allow group <group-name> to read metrics in compartment <compartment-name>
Allow group <group-name> to manage logging-family in compartment <compartment-name>
Allow group <group-name> to use virtual-network-family in compartment <compartment-name>

```

Before you deploy this sample function, make sure you have run steps A, B 
and C of the [Oracle Functions Quick Start Guide for Cloud Shell](https://www.oracle.com/webfolder/technetwork/tutorials/infographics/oci_functions_cloudshell_quickview/functions_quickview_top/functions_quickview/index.html)
### A - Set up your tenancy

Policy Example: 
```
allow any-user to use fn-function in compartment id compartment’_of_function’ where all {request.principal.type='serviceconnector', request.principal.compartment.id=‘compartment’_of_connector’}
allow any-user to use fn-invocation in compartment id compartment’_of_function’ where all {request.principal.type='serviceconnector', request.principal.compartment.id=‘compartment’_of_connector’}

allow any-user to {STREAM_READ, STREAM_CONSUME} in compartment id compartment_of_stream where all {request.principal.type='serviceconnector', target.stream.id=‘stream’_id, request.principal.compartment.id='compartment’_of_connector'}
```
### B - Create application
### C - Set up your Cloud Shell dev environment


### List Applications 

After you have successfully completed the prerequisites, you should see your 
application in the list of applications.

```
fn ls apps
```

## Create a Custom Log
1. From the navigation menu, select **Logging**
1. Click `Logs`
1. Click `Create custom log`
    1. Enter a Custom Log Name 
    1. Select the Compartment
    1. Select the Log group
1. Click `Create custom log` 
1. Select `Add configuration later`
1. Click `Create custom log`
1. Click on the Log Name
1. Copy the `OCID` and save it for later use. ex. `ocid1.log.oc1.iad.....`

## Review and customize the function

Review the following files in the current folder:
* Function code, [func.py](./func.py)
* Function dependencies, [requirements.txt](./requirements.txt)
* Function metadata, [func.yaml](./func.yaml) - In this file set the LOGGING_OCID to the to `OCID` you copied from the Custom Log
    * ex: `LOGGING_OCID: ocid1.log.oc1.iad.....`

## Deploy the function

* In Cloud Shell, create the oci function by runing the `fn init --runtime python <function-name>` this will create a generic function in a directory called `<function-name>`
* Drag the `func.py` and `requirements.txt` into Cloud Shell. This will put them in the home directory
* Go into the function directory`cd <function-name>`
* Remove the existing `func.py` and `requirements.txt` by running `rm func.py requirements.txt`
* Copy the code into the function directory by running 
```
cp ~/func.py .
cp ~/requirements.py
```
* Now run `fn deploy` command to build *this* function and its dependencies as a Docker image, push the image to the specified Docker registry, and deploy *this* function to Oracle Functions 
in the application created earlier:

```
fn -v deploy --app <app-name>
```
e.g.,
```
fn -v deploy --app myapp
```

## Create the permission for the function
### Get the function OCID
1. From the navigation menu, select **Functions** 
1. Click the Application Name
1. Click the Function Name
1. Copy the OCID ex. `ocid1.fnfunc.oc1.iad....`

### Create the Dynamic Group
1. Copy the function OCID
1. From the navigation menu, select **Identity**, and then select **Dynamic Groups**.
1. Click `Create Dynamic Group1`
    1. Enter a Name
    1. Enter a Description
    1. Under `Matching Rules` 
        1. Select `Match all rules defined below`
        1. Under Rule 1 enter `resource.type = 'fnfunc'`
        1. Click `+Additional Rule`
        1. Under Rule 2 enter `resource.id = '<fnfunc_ocid>'`
    1. Click `Create`
    1. Remember your Dynamic Group Name for the next part

### Create Policy
1. From the navigation menu, select **Identity**, and then select **Policies**.
1. Click `Create Policy`
    1. Enter a Name
    1. Enter a Description
    1. Select a Compartment
    1. Select `Show manual editor`
    1. Enter the below policy in the Policy Builder
    ```
    Allow dynamic-group <dynamic-group-name>. to use logging-family in compartment <compartment-of-the-custom-log>
    ```

## Create and Event Rule to Send all Cloud Guard Problems to the Log

1. From the navigation menu, select **Events**, and then select **Rules**.
1. Select the `(root)` compartment
1. Click `Create Rule`
    1. Enter a Display Name
    1. Enter a Description
    1. Under Rule Conditions
        1. Select Condition `Event Type`
        1. Select Service Name `Cloud Guard`
        1. Select Event Type ex. `Detected Problem` and `Remediated Problem` 
    1. Under Actions
        1. Selection `Functions`
        1. Under Function Compartment select the compartment the function is in
        1. Select the Function Application of the function
        1. Select the Function of the function name
1. Click `Create Rule`
