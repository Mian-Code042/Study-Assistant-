"""
Simple HTTP server to serve the HTML UI
Run this alongside your FastAPI backend
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

PORT = 3000

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 50)
    print("  StudyMind AI - Modern UI Server")
    print("=" * 50)
    print(f"\n🚀 Server running at http://localhost:{PORT}")
    print(f"📂 Serving: {os.getcwd()}")
    print(f"\n✨ Open http://localhost:{PORT} in your browser")
    print(f"⚡ Backend should be at http://localhost:8000")
    print(f"\nPress Ctrl+C to stop\n")
    
    server = HTTPServer(('', PORT), CORSRequestHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        server.shutdown()
        sys.exit(0)
