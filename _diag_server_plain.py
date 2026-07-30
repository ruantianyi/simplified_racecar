"""Same as _diag_server.py but WITHOUT COOP/COEP headers, to mimic `python -m http.server`."""
import http.server
import socketserver
import os

PORT = 8124
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_diag_log_plain.txt")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/__log'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            with open(LOG_PATH, 'ab') as f:
                f.write(body + b"\n")
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    open(LOG_PATH, 'wb').close()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"plain diag server on http://127.0.0.1:{PORT}")
        httpd.serve_forever()
