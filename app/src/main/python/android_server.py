"""Start the KODI MAHIRI Python demo API on Android loopback only."""
import os
import sys
import threading

_httpd = None
_thread = None

def start(home, port=8765):
    global _httpd, _thread
    home = str(home)
    os.environ["KODI_MAHIRI_HOME"] = home
    if home not in sys.path:
        sys.path.insert(0, home)
    import server
    if _httpd is not None:
        return "already-running"
    _httpd = server.ThreadingHTTPServer(("127.0.0.1", int(port)), server.H)
    _thread = threading.Thread(target=_httpd.serve_forever, name="KodiMahiriHTTP", daemon=True)
    _thread.start()
    return "started"
