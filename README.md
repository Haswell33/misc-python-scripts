# python-scripts
### checksum-md5
- `checksum-md5.py` checks the checksum of specified file</br>
---
### file-observer
- `file-observer.pyw` updates the selected local file every time it is modified to the target ftp server</br>
- `file-downloader.pyw` checks the local file being examined for a newer version (earlier modified date than local file) on the target ftp server<br>

Scripts should be configured in the task scheduler. Configuration files are in `task-scheduler-xml` directory
and there are 3 lines to edit before import to task scheduler:
```
<Command>{path_to_python}</Command>
<Arguments>{scriptname}.pyw {--arguments}</Arguments>
<WorkingDirectory>{path_to_script}</WorkingDirectory>
```
---
### ftp-upload
- `ftp-upload.py` sends specified local directory (recursively) to FTP server
---
### hilbert-curve
- `hilbert-curve.py` draws a hilbert curve
---
### synchronize-dirs
- `synchronize.py` syncs local directory with directory on the remote host using rsync
---
### backup-rsync
- `backup-rsync.py` backups specified directory or directories to specified dest host or other local directory, if the num of backups is greated than declared, the script will delete the oldest copy to maintain the required num of backups 