#!/usr/bin/python

import os
import shutil

def get_directory_size(directory):
    """
    Determines the total occupied disk size.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size


def delete_files_to_limit(directory, limit):
    """
    Deletes the oldest files until the total occupied disk size is under the given limit.
    """
    total_size = get_directory_size(directory)
    
    while total_size > limit:
        # Find the oldest file under the given directory
        oldest_file = min((os.path.join(dirpath, filename)
                           for dirpath, dirnames, filenames in os.walk(directory)
                           for filename in filenames),
                          key=os.path.getctime)
        
        try:
            os.remove(oldest_file)
            print(f"Deleted: {oldest_file}")
        except Exception as e:
            print(f"Error deleting {oldest_file}: {e}")
            break
        
        total_size = get_directory_size(directory)


if __name__ == "__main__":
    target_directory = "/var/lib/traffic-logger/hourly_pcaps"  # Delete files underneath here
    # Set the desired max occupied disk space limit in megabytes
    space_limit_mb = 1500
    
    delete_files_to_limit(target_directory, space_limit_mb * 1024 * 1024)  # Convert megabytes to bytes
