from flask import Flask, request, render_template, send_from_directory, redirect, url_for
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
    return render_template('index.html', files=files)

@app.route("/note", methods=["POST"])
def create_note():
    note_title = request.form["note_title"]
    note_content = request.form["note_content"]

    # Always add .md extension
    note_title = note_title + '.md'

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

    return render_template('view_note.html', filename=filename, content=content)

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

    return render_template('edit_note.html', filename=filename, content=content)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('upload'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
