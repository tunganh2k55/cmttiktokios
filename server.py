from flask import Flask, request, jsonify
from threading import Lock
from datetime import datetime

app = Flask(__name__)

# Lưu job trong RAM: { "192.168.1.5": {"iplocal": "...", "message": "...", "updated_at": "..."} }
jobs = {}
lock = Lock()

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

@app.get("/api")
def api():
    action = request.args.get("action", "").strip()
    iplocal = request.args.get("localip", "").strip()

    if not action:
        return jsonify({"error": "missing action"}), 400

    if action in ("createJob", "checkStatus", "updateStatus", "deleteJob") and not iplocal:
        return jsonify({"error": "missing localip"}), 400

    # action=createJob&localip=...&message=...
    if action == "createJob":
        message = request.args.get("message", "")
        with lock:
            jobs[iplocal] = {"iplocal": iplocal, "message": message, "updated_at": now_iso()}
        return jsonify({"action": "createJob", "status": "create done"}), 200

    # action=checkStatus&localip=...
    if action == "checkStatus":
        with lock:
            job = jobs.get(iplocal)
        if not job:
            return jsonify({"action": "checkStatus", "status": False, "error": "not found", "localip": iplocal}), 404
        return jsonify({"action": "checkStatus", "status": True, **job}), 200

    # action=updateStatus&localip=...&message=done
    if action == "updateStatus":
        message = request.args.get("message", None)
        # bạn bị typo "massage" trong mô tả, nên mình hỗ trợ luôn:
        if message is None:
            message = request.args.get("massage", None)

        if message is None:
            return jsonify({"error": "missing message"}), 400

        with lock:
            if iplocal not in jobs:
                return jsonify({"action": "updateStatus", "status": False, "error": "not found", "localip": iplocal}), 404
            jobs[iplocal]["message"] = message
            jobs[iplocal]["updated_at"] = now_iso()

        return jsonify({"action": "updateStatus", "status": "update done", "localip": iplocal, "message": message}), 200

    # action=deleteJob&localip=...
    if action == "deleteJob":
        with lock:
            existed = iplocal in jobs
            if existed:
                jobs.pop(iplocal, None)
        return jsonify({"action": "deleteJob", "status": "delete done" if existed else "not found", "localip": iplocal}), 200

    return jsonify({"error": "unknown action", "action": action}), 400


if __name__ == "__main__":
    # 0.0.0.0 để máy khác trong LAN gọi được; port tuỳ bạn
    app.run(host="0.0.0.0", port=5000, debug=False)
