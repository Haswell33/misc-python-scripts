import shlex
import subprocess

def run_cmd_1(cmd, check=True):
    process = subprocess.run(shlex.split(cmd), stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=check, text=True)
    return process.stdout or process.stderr

def run_cmd_2(cmd, check=True):
    process = subprocess.Popen(shlex.split(cmd), stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if check and stderr:
        raise subprocess.CalledProcessError(cmd=cmd, stderr=stderr, returncode=process.returncode)
    return stdout if stdout else stderr
