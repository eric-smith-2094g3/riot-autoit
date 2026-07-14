import base64
from pathlib import Path
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CANDIDATE_PATHS = [
    Path(r"C:\Riot Games\League of Legends\lockfile"),
    Path(r"D:\Riot Games\League of Legends\lockfile"),
    Path(r"E:\Riot Games\League of Legends\lockfile"),
]


class LCUClient:
    """Talks to League Client Ux over local https."""

    def __init__(self, lockfile_path=None):
        self.custom_path = Path(lockfile_path) if lockfile_path else None
        self.lockfile_path = None
        self.session = requests.Session()
        self.session.verify = False
        self.port = None
        self.auth_token = None
        self.connected = False
        self._last_status = None

    def find_lockfile(self):
        if self.custom_path and self.custom_path.exists():
            return self.custom_path
        for p in CANDIDATE_PATHS:
            if p.exists():
                return p
        return None

    def read_lockfile(self):
        target = self.find_lockfile()
        if not target:
            self.connected = False
            return False
        self.lockfile_path = target

        # league briefly opens lockfile exclusively during launches
        content = ""
        for _ in range(4):
            try:
                content = self.lockfile_path.read_text(encoding="utf-8").strip()
                break
            except PermissionError:
                time.sleep(0.08)
            except OSError:
                time.sleep(0.05)
        else:
            return False

        if not content:
            return False

        parts = content.split(":")
        if len(parts) != 5:
            return False

        self.port = int(parts[2])
        self.auth_token = parts[3]
        auth_blob = base64.b64encode(f"riot:{self.auth_token}".encode()).decode()
        self.session.headers.update({
            "Authorization": f"Basic {auth_blob}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.connected = True
        return True

    def request(self, method, endpoint, **kwargs):
        if not self.connected and not self.read_lockfile():
            return None
        url = f"https://127.0.0.1:{self.port}{endpoint}"
        try:
            kwargs.setdefault("timeout", 3)
            r = self.session.request(method, url, **kwargs)
            if r.status_code in (401, 403):
                # auth rotated after client restarted without deleting lockfile
                self.connected = False
                return None
            return r
        except requests.RequestException:
            self.connected = False
            return None

    def set_status_message(self, message):
        # avoid blasting the lcu endpoint with identical text every tick
        if message == self._last_status:
            return True

        r = self.request("put", "/lol-chat/v1/me", json={"statusMessage": message})
        # print(f"DEBUG: status update {r.status_code if r else 'none'} msg={message}")
        if r is not None and r.status_code == 200:
            self._last_status = message
            return True
        return False

    def get_gameflow_phase(self):
        # FIXME: inChampSelect returns 200 but body is quoted raw string, not json
        r = self.request("get", "/lol-gameflow/v1/gameflow-phase")
        if r is not None and r.status_code == 200:
            text = r.text.strip()
            if text.startswith('"') and text.endswith('"'):
                return text[1:-1]
            return text
        return None

    def get_current_presence(self):
        r = self.request("get", "/lol-chat/v1/me")
        if r is not None and r.status_code == 200:
            return r.json()
        return None
