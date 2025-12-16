from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
from datetime import datetime

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
        .tabs {
            display: flex;
            gap: 0;
            margin-bottom: 15px;
        }
        .tab {
            flex: 1;
            padding: 10px 20px;
            background: #f5f5f5;
            color: #555;
            border: 1px solid #ddd;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
        }
        .tab:first-child {
            border-radius: 6px 0 0 0;
        }
        .tab:last-child {
            border-radius: 0 6px 0 0;
            border-left: none;
        }
        .tab.active {
            background: #fff;
            color: #000;
            border-bottom-color: #fff;
            font-weight: 500;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .upload-form {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .note-form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        input[type="file"], input[type="text"] {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            border: 1px dashed #aaa;
            border-radius: 6px;
        }
        input[type="text"] {
            border-style: solid;
        }
        textarea {
            width: 100%;
            min-height: 200px;
            padding: 10px;
            border: 1px solid #aaa;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            resize: vertical;
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
        .note-actions {
            display: flex;
            gap: 8px;
        }
        .edit-btn {
            background: #444;
            padding: 6px 14px;
            font-size: 0.8em;
        }
        .edit-btn:hover {
            background: #666;
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
            <div class="tabs">
                <div class="tab active" onclick="switchTab(0)">파일 업로드</div>
                <div class="tab" onclick="switchTab(1)">노트 작성</div>
            </div>

            <div class="tab-content active">
                <form action="/" method="post" enctype="multipart/form-data" class="upload-form">
                    <input type="file" name="file" required>
                    <button type="submit">업로드</button>
                </form>
            </div>

            <div class="tab-content">
                <form action="/note" method="post" class="note-form">
                    <input type="text" name="note_title" placeholder="노트 제목 (예: my-note.md)" required pattern=".*\.md$">
                    <textarea name="note_content" placeholder="마크다운 내용을 입력하세요..." required></textarea>
                    <button type="submit">노트 저장</button>
                </form>
            </div>
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
                        <span>{% if file.is_note %}📝{% else %}📄{% endif %}</span>
                        <div>
                            <a href="{% if file.is_note %}/view-note/{{ file.name }}{% else %}/files/{{ file.name }}{% endif %}" class="file-name">{{ file.name }}</a>
                            <div class="file-size">{{ file.size }}</div>
                        </div>
                    </div>
                    <div class="note-actions">
                        {% if file.is_note %}
                        <form action="/edit-note/{{ file.name }}" method="get" style="display: inline;">
                            <button type="submit" class="edit-btn">수정</button>
                        </form>
                        {% endif %}
                        <form action="/delete/{{ file.name }}" method="post" style="display: inline;">
                            <button type="submit" class="delete-btn" onclick="return confirm('정말 삭제하시겠습니까?')">삭제</button>
                        </form>
                    </div>
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
    <script>
        function switchTab(index) {
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');

            tabs.forEach((tab, i) => {
                if (i === index) {
                    tab.classList.add('active');
                    contents[i].classList.add('active');
                } else {
                    tab.classList.remove('active');
                    contents[i].classList.remove('active');
                }
            });
        }
    </script>
</body>
</html>
"""

NOTE_EDIT_HTML = """
<!doctype html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>노트 수정 - {{ filename }}</title>
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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 1.3em;
        }
        .back-btn {
            padding: 8px 16px;
            background: #666;
            color: #fff;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9em;
        }
        .back-btn:hover {
            background: #888;
        }
        .edit-section {
            padding: 20px;
        }
        textarea {
            width: 100%;
            min-height: 500px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            resize: vertical;
            margin-bottom: 10px;
        }
        button {
            padding: 12px 24px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 {{ filename }}</h1>
            <a href="/" class="back-btn">← 돌아가기</a>
        </div>
        <div class="edit-section">
            <form method="post">
                <textarea name="note_content" required>{{ content }}</textarea>
                <button type="submit">저장</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

NOTE_VIEW_HTML = """
<!doctype html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ filename }}</title>
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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 1.3em;
        }
        .actions {
            display: flex;
            gap: 10px;
        }
        .back-btn, .edit-btn {
            padding: 8px 16px;
            background: #666;
            color: #fff;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9em;
        }
        .edit-btn {
            background: #000;
        }
        .back-btn:hover {
            background: #888;
        }
        .edit-btn:hover {
            background: #333;
        }
        .content {
            padding: 30px;
        }
        .markdown-body {
            line-height: 1.6;
            color: #333;
        }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            margin-top: 24px;
            margin-bottom: 16px;
        }
        .markdown-body h1 {
            font-size: 2em;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }
        .markdown-body h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eee;
            padding-bottom: 6px;
        }
        .markdown-body h3 {
            font-size: 1.25em;
        }
        .markdown-body p {
            margin-bottom: 16px;
        }
        .markdown-body code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .markdown-body pre {
            background: #f5f5f5;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin-bottom: 16px;
        }
        .markdown-body pre code {
            background: none;
            padding: 0;
        }
        .markdown-body ul, .markdown-body ol {
            margin-left: 24px;
            margin-bottom: 16px;
        }
        .markdown-body li {
            margin-bottom: 8px;
        }
        .markdown-body blockquote {
            border-left: 4px solid #ddd;
            padding-left: 16px;
            color: #666;
            margin-bottom: 16px;
        }
        .markdown-body a {
            color: #0066cc;
            text-decoration: none;
        }
        .markdown-body a:hover {
            text-decoration: underline;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 {{ filename }}</h1>
            <div class="actions">
                <a href="/edit-note/{{ filename }}" class="edit-btn">수정</a>
                <a href="/" class="back-btn">← 돌아가기</a>
            </div>
        </div>
        <div class="content">
            <div class="markdown-body" id="markdown-content"></div>
        </div>
    </div>
    <script>
        const content = {{ content|tojson }};
        document.getElementById('markdown-content').innerHTML = marked.parse(content);
    </script>
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
                'size': get_file_size(filepath),
                'is_note': filename.endswith('.md')
            })

    files.sort(key=lambda x: x['name'])
    return render_template_string(HTML, files=files)

@app.route("/note", methods=["POST"])
def create_note():
    note_title = request.form["note_title"]
    note_content = request.form["note_content"]

    if not note_title.endswith('.md'):
        note_title += '.md'

    filepath = os.path.join(UPLOAD_DIR, note_title)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(note_content)

    return redirect(url_for('upload'))

@app.route("/files/<path:filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/view-note/<path:filename>")
def view_note(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        return redirect(url_for('upload'))

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return render_template_string(NOTE_VIEW_HTML, filename=filename, content=content)

@app.route("/edit-note/<path:filename>", methods=["GET", "POST"])
def edit_note(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)

    if request.method == "POST":
        new_content = request.form["note_content"]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return redirect(url_for('view_note', filename=filename))

    if not os.path.exists(filepath):
        return redirect(url_for('upload'))

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return render_template_string(NOTE_EDIT_HTML, filename=filename, content=content)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('upload'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
