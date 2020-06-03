import errno
import os
import socket
import subprocess
import time

try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, URLError

from tools.wpt import wpt

def is_port_8080_in_use():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 8080))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return True
        else:
            raise e
    finally:
        s.close()
    return False

def test_serve():
    if is_port_8080_in_use():
        assert False, "WAVE Test Runner failed: Port 8080 already in use."

    p = subprocess.Popen([os.path.join(wpt.localpaths.repo_root, "wpt"),
        "serve-wave",
        "--config",
        os.path.join(wpt.localpaths.repo_root, "tools/wave/tests/config.json")])

    start = time.time()
    try:
        while True:
            if p.poll() is not None:
                assert False, "WAVE Test Runner failed: Server not running."
            if time.time() - start > 6 * 60:
                assert False, "WAVE Test Runner failed: Server did not start responding within 6m."
            try:
                resp = urlopen("http://web-platform.test:8080/_wave/api/sessions/public")
                print(resp)
            except URLError:
                print("Server not responding, waiting another 10s.")
                time.sleep(10)
            else:
                assert resp.code == 200
                break
    finally:
        p.terminate()
