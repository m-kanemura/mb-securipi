import os
import time

def cleanup_old_videos(directory, retention_days):
    deleted_files = False
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Check if the file is older than the retention period
        if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > (retention_days * 86400):
            os.remove(file_path)
            deleted_files = True
    if deleted_files == True:
        print("cleaned up videos older than 7 days!")