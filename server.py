from flask import Flask, request, render_template_string, send_from_directory
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML = """
<!doctype html>
<title>Local Share</title>
<h2>Upload a file</h2>
<form action="/" method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <button type="submit">Upload</button>
</form>

<h2>Files</h2>
<ul>
{% for f in files %}
  <li><a href="/files/{{ f }}">{{ f }}</a></li>
{% endfor %}
</ul>
"""

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        if f.filename:
            f.save(os.path.join(UPLOAD_DIR, f.filename))
    files = os.listdir(UPLOAD_DIR)
    return render_template_string(HTML, files=files)

@app.route("/files/<path:filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
