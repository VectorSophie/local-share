from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_file_size(filepath):
    """Get human-readable file size"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

HTML = """
<!doctype html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local Share</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f2f2f2;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .header {
            padding: 20px;
            border-bottom: 1px solid #ddd;
            text-align: center;
        }
        .header h1 {
            font-size: 1.6em;
            margin-bottom: 5px;
        }
        .header p {
            font-size: 0.9em;
            color: #555;
        }
        .upload-section {
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .upload-form {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        input[type="file"] {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            border: 1px dashed #aaa;
            border-radius: 6px;
        }
        button {
            padding: 10px 20px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 0.95em;
            cursor: pointer;
        }
        button:hover {
            background: #333;
        }
        .files-section {
            padding: 20px;
        }
        .files-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .file-count {
            background: #000;
            color: #fff;
            padding: 3px 10px;
            font-size: 0.8em;
            border-radius: 10px;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            margin-bottom: 10px;
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 6px;
        }
        .file-info {
            display: flex;
            gap: 12px;
        }
        .file-name {
            text-decoration: none;
            color: #000;
        }
        .file-name:hover {
            text-decoration: underline;
        }
        .file-size {
            font-size: 0.8em;
            color: #555;
        }
        .delete-btn {
            background: #222;
            padding: 6px 14px;
            font-size: 0.8em;
        }
        .delete-btn:hover {
            background: #444;
        }
        .empty-state {
            padding: 50px 20px;
            text-align: center;
            color: #777;
        }
        @media (max-width: 600px) {
            .file-item {
                flex-direction: column;
                gap: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Local Share</h1>
            <p>로컬 파일 공유 시스템</p>
        </div>

        <div class="upload-section">
            <form action="/" method="post" enctype="multipart/form-data" class="upload-form">
                <input type="file" name="file" required>
                <button type="submit">업로드</button>
            </form>
        </div>

        <div class="files-section">
            <div class="files-header">
                <h2>파일 목록</h2>
                <span class="file-count">{{ files|length }}개</span>
            </div>

            {% if files %}
            <ul class="file-list">
            {% for file in files %}
                <li class="file-item">
                    <div class="file-info">
                        <span>📄</span>
                        <div>
                            <a href="/files/{{ file.name }}" class="file-name">{{ file.name }}</a>
                            <div class="file-size">{{ file.size }}</div>
                        </div>
                    </div>
                    <form action="/delete/{{ file.name }}" method="post">
                        <button type="submit" class="delete-btn" onclick="return confirm('정말 삭제하시겠습니까?')">삭제</button>
                    </form>
                </li>
            {% endfor %}
            </ul>
            {% else %}
            <div class="empty-state">
                <br>아직 업로드된 파일이 없습니다
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        if f.filename:
            f.save(os.path.join(UPLOAD_DIR, f.filename))
            return redirect(url_for('upload'))

    files = []
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            files.append({
                'name': filename,
                'size': get_file_size(filepath)
            })

    files.sort(key=lambda x: x['name'])
    return render_template_string(HTML, files=files)

@app.route("/files/<path:filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('upload'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
