#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common_env

SERVER_HOST = os.getenv("LOCAL_SERVER_HOST", "192.168.2.141")
SERVER_USER = os.getenv("LOCAL_SERVER_USER", "user")
SERVER_PASSWORD = os.getenv("LOCAL_SERVER_PASSWORD", "1")

def send_reboot():
    expect_script = f"""#!/usr/bin/expect -f
set timeout 10
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {SERVER_USER}@{SERVER_HOST} {{ echo '{SERVER_PASSWORD}' | sudo -S reboot }}
expect {{
    "yes/no" {{ send "yes\\r"; exp_continue }}
    "password:" {{ send "{SERVER_PASSWORD}\\r" }}
    timeout {{ puts "Timeout on connect"; exit 0 }}
    eof {{ puts "Reboot command sent / connection closed"; exit 0 }}
}}
expect {{
    timeout {{ puts "Timeout waiting for reboot ack"; exit 0 }}
    eof {{ puts "Connection closed after reboot"; exit 0 }}
}}
"""
    subprocess.run(["expect", "-c", expect_script], capture_output=True, text=True)

def wait_for_ssh(timeout=120):
    start = time.time()
    print(f"Ожидание возвращения сервера {SERVER_HOST} после перезагрузки...")
    time.sleep(15)  # дать время на отключение
    while time.time() - start < timeout:
        res = subprocess.run(["nc", "-z", "-w", "2", SERVER_HOST, "22"], capture_output=True)
        if res.returncode == 0:
            print(f"[OK] Порт 22 на {SERVER_HOST} снова открыт! (прошло {int(time.time() - start)} сек)")
            time.sleep(5)  # дать время демонам стартовать
            return True
        time.sleep(3)
    print("[FAIL] Таймаут ожидания перезагрузки сервера")
    return False

if __name__ == "__main__":
    print("Отправка команды sudo reboot на сервер...")
    send_reboot()
    if wait_for_ssh():
        print("Сервер успешно перезагрузился и доступен по SSH.")
    else:
        sys.exit(1)
