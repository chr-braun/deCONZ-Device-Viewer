#!/usr/bin/env python3
from flask import Flask, render_template_string
import socket

app = Flask(__name__)

# Beispiel-Routen
@app.route("/")
def index():
    return render_template_string("""
        <html>
            <head>
                <title>deCONZ Device Viewer</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #f4f4f4; color: #333; }
                    table { border-collapse: collapse; width: 80%; margin: 20px auto; }
                    th, td { border: 1px solid #999; padding: 8px; text-align: left; }
                    th { background-color: #4CAF50; color: white; }
                    tr:nth-child(even) { background-color: #eee; }
                </style>
            </head>
            <body>
                <h1 style="text-align:center;">deCONZ Device Viewer</h1>
                <table>
                    <tr><th>ID</th><th>Name</th></tr>
                    {% for device in devices %}
                    <tr><td>{{ device.id }}</td><td>{{ device.name }}</td></tr>
                    {% endfor %}
                </table>
            </body>
        </html>
    """, devices=[{'id': 1, 'name': 'Beispiel Gerät 1'}, {'id': 2, 'name': 'Beispiel Gerät 2'}])

def find_free_port(start=8500, end=8600):
    for port in range(start, end+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Kein freier Port verfügbar!")

if __name__ == "__main__":
    port = find_free_port()
    print(f"🚀 Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

