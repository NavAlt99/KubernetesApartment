#!/usr/bin/env python3
"""
serve.py — Launches local HTTP server for the Kubernetes Apartment Complex site.
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 60)
        print("Kubernetes Apartment Complex — Local Web Server")
        print(f"Serving at: {url}")
        print("Press Ctrl+C to stop the server.")
        print("=" * 60)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        httpd.serve_forever()
except OSError as e:
    if "Address already in use" in str(e):
        print(f"Port {PORT} is busy, trying port {PORT + 1}...")
        PORT += 1
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}/index.html"
            print(f"Serving at: {url}")
            httpd.serve_forever()
    else:
        raise
