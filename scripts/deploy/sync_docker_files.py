#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

files_to_fetch = [
    "/home/user/docker/printserver/docker-compose.yml",
    "/home/user/docker/printserver/Dockerfile",
    "/home/user/docker/printserver/start.sh",
    "/home/user/docker/printserver/samba/Dockerfile",
    "/home/user/docker/printserver/samba/smb.conf",
    "/home/user/docker/printserver/samba/start.sh",
    "/home/user/docker/printserver/samba/client.conf"
]

base_dir = Path(__file__).resolve().parent.parent / "printserver" / "docker"

for fpath in files_to_fetch:
    print(f"Fetching {fpath}...")
    content = ssh_server(f"cat {fpath}")
    # strip expect banner / password prompt
    lines = content.splitlines()
    clean_lines = []
    started = False
    for line in lines:
        if "spawn ssh" in line or "password:" in line or "known hosts" in line:
            continue
        clean_lines.append(line)
    clean_content = "\n".join(clean_lines).strip() + "\n"
    
    rel_path = fpath.replace("/home/user/docker/printserver/", "")
    target = base_dir / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(clean_content, encoding="utf-8")
    print(f"Saved to {target} ({len(clean_content)} bytes)")

print("Done fetching docker files.")
