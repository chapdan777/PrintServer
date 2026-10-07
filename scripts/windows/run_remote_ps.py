import sys
import base64
import subprocess

def run_ps(ps_code, timeout=120):
    b64 = base64.b64encode(ps_code.encode('utf-16le')).decode('ascii')
    expect_script = f"""#!/usr/bin/expect -f
set timeout {timeout}
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ssh@192.168.2.72 powershell -NoProfile -EncodedCommand {b64}
expect {{
    "password:" {{
        send "ssh\\r"
    }}
    timeout {{
        puts "Timeout connecting"
        exit 1
    }}
    eof {{
        puts "EOF on connect"
        exit 1
    }}
}}
expect {{
    timeout {{
        puts "Timeout waiting for result"
        exit 1
    }}
    eof
}}
"""
    proc = subprocess.run(["expect", "-c", expect_script], capture_output=True, text=True)
    return proc.stdout + proc.stderr

if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()
    output = run_ps(code)
    print(output)
