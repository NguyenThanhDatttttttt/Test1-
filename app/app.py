from flask import Flask, jsonify, render_template, request, session
from functools import wraps

app = Flask(__name__)
app.secret_key = "replace-this-lab-secret"

USERS = {
    "alice": {"password": "AliceLab123!", "name": "Nguyễn Minh Anh", "sid": "SV2024001"},
    "bob": {"password": "BobLab123!", "name": "Trần Quốc Bảo", "sid": "SV2024002"},
    "chi": {"password": "ChiLab123!", "name": "Lê Ngọc Chi", "sid": "SV2024003"},
}
EXAMS = {
    1001: {"id":1001,"owner":"alice","subject":"An toàn mạng","semester":"HK1 2026-2027","score":8.5,"status":"Đã công bố"},
    1002: {"id":1002,"owner":"bob","subject":"An toàn mạng","semester":"HK1 2026-2027","score":6.0,"status":"Đã công bố"},
    1003: {"id":1003,"owner":"chi","subject":"An toàn mạng","semester":"HK1 2026-2027","score":9.0,"status":"Đã công bố"},
    2001: {"id":2001,"owner":"alice","subject":"Lập trình Python","semester":"HK1 2026-2027","score":7.5,"status":"Đã công bố"},
    2002: {"id":2002,"owner":"bob","subject":"Lập trình Python","semester":"HK1 2026-2027","score":8.0,"status":"Đã công bố"},
    2003: {"id":2003,"owner":"chi","subject":"Lập trình Python","semester":"HK1 2026-2027","score":8.5,"status":"Đã công bố"},
}

def auth(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return jsonify(error="Bạn cần đăng nhập"), 401
        return fn(*args, **kwargs)
    return wrapped

def serialize(exam):
    user = USERS[exam["owner"]]
    return {"id":exam["id"],"student_id":user["sid"],"student_name":user["name"],
            "subject":exam["subject"],"semester":exam["semester"],
            "score":exam["score"],"status":exam["status"]}

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or request.form
    username = str(data.get("username","")).strip().lower()
    password = str(data.get("password",""))
    if username not in USERS or USERS[username]["password"] != password:
        return jsonify(error="Tài khoản hoặc mật khẩu không đúng"), 401
    session.clear()
    session["username"] = username
    u = USERS[username]
    return jsonify(username=username, name=u["name"], student_id=u["sid"])

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

@app.get("/api/me")
@auth
def me():
    username = session["username"]
    u = USERS[username]
    return jsonify(username=username, name=u["name"], student_id=u["sid"])

@app.get("/api/exams")
@auth
def exams():
    # Danh sách này đã lọc theo tài khoản hiện tại.
    return jsonify([serialize(e) for e in EXAMS.values() if e["owner"] == session["username"]])

@app.get("/api/exams/<int:exam_id>")
@auth
def exam_detail(exam_id):
    exam = EXAMS.get(exam_id)
    if not exam:
        return jsonify(error="Không tìm thấy kết quả"), 404
    # IDOR CỐ Ý: thiếu kiểm tra exam["owner"] == session["username"].
    # Khi vá lab, bỏ comment hai dòng dưới:
    # if exam["owner"] != session["username"]:
    #     return jsonify(error="Không có quyền xem kết quả này"), 403
    return jsonify(serialize(exam))

@app.patch("/api/exams/<int:exam_id>")
@auth
def update_exam(exam_id):
    exam = EXAMS.get(exam_id)
    if not exam:
        return jsonify(error="Không tìm thấy kết quả"), 404
    data = request.get_json(silent=True) or {}
    if data.get("status") not in ("Đã công bố", "Đang rà soát"):
        return jsonify(error="Trạng thái không hợp lệ"), 400
    # IDOR CỐ Ý: thiếu kiểm tra quyền sở hữu trước khi cập nhật.
    # Khi vá lab, bỏ comment hai dòng dưới:
    # if exam["owner"] != session["username"]:
    #     return jsonify(error="Không có quyền sửa kết quả này"), 403
    exam["status"] = data["status"]
    return jsonify(ok=True, exam=serialize(exam))

@app.get("/api/health")
def health():
    return jsonify(status="ok", service="EduResultLab")

if __name__ == "__main__":
    # Chỉ expose trong mạng sandbox cô lập, không đưa lab dễ tổn thương lên Internet.
    app.run(host="0.0.0.0", port=5000, debug=False)
