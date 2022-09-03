import os
import sys

def createDir(folder):
    ## Create log folder if not exists ##
    path = os.path.join(sys.path[0], folder)
    # Check whether the specified path exists or not
    path_exist = os.path.exists(path)
    # Create log path if not exists
    if not path_exist:
        os.makedirs(path)
        print(f"Log path {path} not detected, so we created it!")

    return path