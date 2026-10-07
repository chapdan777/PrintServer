#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common_env

host = os.getenv("LOCAL_SERVER_HOST", "192.168.2.141")
user = os.getenv("LOCAL_SERVER_USER", "user")
password = os.getenv("LOCAL_SERVER_PASSWORD", "")

cmd = sys.argv[1] if len(sys.argv) > 1 else "uname -a"

expect_script = f"""#!/usr/bin/expect -f
set timeout 30
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {user}@{host} {{ {cmd} }}
expect {{
    "yes/no" {{
        send "yes\\r"
        exp_continue
    }}
    "password:" {{
        send "{password}\\r"
    }}
    timeout {{
        puts "Timeout connecting to {host}"
        exit 1
    }}
    eof {{
        puts "Connection closed"
        exit 1
    }}
}}
expect {{
    timeout {{
        puts "Timeout waiting for command output"
        exit 1
    }}
    eof
}}
"""

proc = subprocess.run(["expect", "-c", expect_script], capture_output=True, text=True)
print(proc.stdout)
if proc.stderr:
    print("STDERR:", proc.stderr, file=sys.stderr)
