import logging
import argparse
import sys
import os 
import subprocess

import lib.common.utils as utils
logger = logging.getLogger(__name__)

script_name = os.path.basename(sys.argv[0])
  
def get_all_version(project_name, service_name, service_status, configuration_cmd):
    """
    Function to get all the versions of a service for a particular project
    return list of versions
    """

    if project_name is None or service_name is None or service_status is None:
        logger.error("Please provide project name, service name and service status to get the version count")
        return False

    version_cmd = "gcloud app versions list --project {} --configuration {} --service {} --filter=version.servingStatus='{}' |awk '{{print $2}}' | sed '1d'".format(project_name, configuration_cmd, service_name, service_status)
    version_list = (utils.exec_cmd_return_output(version_cmd)).split("\n")
    version_list.pop()
    logger.info("List of versions presently having status {} is {} ".format(service_status, version_list))

    return version_list

def stop_old_version(operation, project_name, service_name, service_status, configuration_cmd, *num_of_versions):
    """
    Function to stop the N or ALL older version of a service of a particular Project
    return Status Code
    """
    versions = get_all_version(project_name, service_name,service_status, configuration_cmd)
    
    if 'Listed 0 items.' in versions:
        logger.error("Versions with Status = {} is not found. ".format(service_status))
        return False

    num_of_versions = int(num_of_versions[0])
    
    if ( operation == "STOPALL" or ( num_of_versions > len(versions) ) ):
        versions_to_stop = len(versions)
        logger.info("EITHER number_of_versions to stop provided is more than the actual number OR Operation is STOPALL, so stopping all the instances")

    else:
        versions_to_stop = num_of_versions
    
    completed = 0
    for i in range(versions_to_stop):
        logger.info("Going to {} the following version : {} ".format(operation, versions[i]))
        gcloud_cmd = "gcloud app versions stop --service={} {} --project {} --configuration {} -q".format(service_name, versions[i], project_name, configuration_cmd)
        is_successful = utils.exec_shell_cmd(gcloud_cmd)
        logger.info("Status Code of the {} command = {} ".format(operation, is_successful))              
        completed += 1

    if completed == versions_to_stop:
        return True

    else:
        return False

def start_old_version(operation, project_name, service_name, service_status, num_of_versions, configuration_cmd):
    """
    Function to start the N older version of a service of a particular Project
    return Status Code
    """
    versions = get_all_version(project_name, service_name,service_status, configuration_cmd)
    
    if 'Listed 0 items.' in versions:
        logger.error("Versions with Status = {} is not found. ".format(service_status))
        return False

    last_idx = len(versions) - 1
    num_of_versions = int(num_of_versions[0])

    if num_of_versions > len(versions):
        logger.info("Since Number of versions to start provided is more than the actual number, so starting all the instances")
        versions_to_start = len(versions)
    else:
        versions_to_start = num_of_versions

    completed = 0

    for i in range(versions_to_start):
        logger.info("Going to {} the following version : {} ".format(operation, versions[last_idx - i]))
        gcloud_cmd = "gcloud app versions start --service={} {} --project {}  --configuration {} -q".format(service_name, versions[last_idx - i], project_name, configuration_cmd)
        is_successful = utils.exec_shell_cmd(gcloud_cmd)
        logger.info("Status Code of the {} command = {} ".format(operation, is_successful))              
        completed += 1
    
    if completed == versions_to_start:
        return True
        
    else:
        return False

def delete_old_version(operation, project_name, service_name, service_status, configuration_cmd, *num_of_versions):
    """
    Function to Delete the N or ALL older version of a service of a particular Project
    return Status Code
    """
    versions = get_all_version(project_name, service_name,service_status, configuration_cmd)
    
    if 'Listed 0 items.' in versions:
        logger.error("Versions with Status = {} is not found. ".format(service_status))
        return False

    num_of_versions = int(num_of_versions[0])
    
    if ( operation == "DELETEALL" or ( num_of_versions > len(versions) ) ):
        versions_to_delete = len(versions)
        logger.info("EITHER number_of_versions to Delete provided is more than the actual number OR Operation is DELETEALL, so Deleting all the versions")

    else:
        versions_to_delete = num_of_versions
    
    completed = 0
    for i in range(versions_to_delete):
        logger.info("Going to {} the following version : {} ".format(operation, versions[i]))
        gcloud_cmd = "gcloud app versions delete --service={} {} --project {} --configuration {} -q".format(service_name, versions[i], project_name, configuration_cmd)
        is_successful = utils.exec_shell_cmd(gcloud_cmd)
        logger.info("Status Code of the {} command = {} ".format(operation, is_successful))              
        completed += 1

    if completed == versions_to_delete:
        return True

    else:
        return False
