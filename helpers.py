import os
import sys

def createLogDir(log_folder):
    ## Create log folder if not exists ##
    log_path = os.path.join(sys.path[0], log_folder)
    # Check whether the specified path exists or not
    log_path_exist = os.path.exists(log_path)
    # Create log path if not exists
    if not log_path_exist:
        os.makedirs(log_path)
        print(f"Log path {log_path} not detected, so we created it!")

    return log_path