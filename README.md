# python-scripts
### checksum-md5
- <code>checksum-md5.py</code> checks the checksum of specified file</br>
---
### file-observer
- <code>file-observer.pyw</code> updates the selected local file every time it is modified to the target ftp server</br>
- <code>file-downloader.pyw</code> checks the local file being examined for a newer version (earlier modified date than local file) on the target ftp server<br>
---
Scripts should be configured in the task scheduler. Configuration files are in <code>task-scheduler-xml</code> directory
and there is 3 lines to edit before import to task scheduler:
- <code><Command>{path_to_python}</Command></code>
- <Arguments>{scriptname}.pyw --pathToFile :) --ftpHost :) --ftpUser :) --ftpPass :) --ftpDir :)</Arguments>
- WorkingDirectory F:/Misc/keepass/haswell/
      

