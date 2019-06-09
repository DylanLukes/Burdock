from os import PathLike
from shlex import quote
import subprocess


def run_daikon(decls: PathLike, dtrace: PathLike):
    cmd = "java -cp /usr/local/opt/daikon/daikon-src/daikon.jar daikon.Daikon --nohierarchy {decls} {dtrace}".format(decls=quote(decls), dtrace=quote(dtrace))
    stdout = subprocess.check_output(cmd, shell=True)

    for line in stdout.strip().decode().splitlines():
        print(line)

