import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import json

PAGE="""\
<html>
<head>
<title>Robot Dog</title>
</head>
<body>
<center><h1>Control the Robot Dog</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
<center><button id='dog-forward'>Forward</button>
<button id='dog-backward'>Backward</button>
<button id='dog-left'>Left</button>
<button id='dog-right'>Right</button>
<button id='cam-up'>Camera Up</button>
<button id='cam-down'>Camera Down</button>
<button id='cam-left'>Camera Left</button>
<button id='cam-right'>Camera Right</button></center>
<script>
const dfbutton = document.getElementById('dog-forward');
dfbutton.addEventListener('click', _ => move("dog", "forward"));

const dbbutton = document.getElementById('dog-backward');
dbbutton.addEventListener('click', _ => move("dog", "backward"));

const dlbutton = document.getElementById('dog-left');
dlbutton.addEventListener('click', _ => move("dog", "left"));

const drbutton = document.getElementById('dog-right');
drbutton.addEventListener('click', _ => move("dog", "right"));

const cubutton = document.getElementById('cam-up');
cubutton.addEventListener('click', _ => move("camera", "up"));

const cdbutton = document.getElementById('cam-down');
cdbutton.addEventListener('click', _ => move("camera", "down"));

const clbutton = document.getElementById('cam-left');
clbutton.addEventListener('click', _ => move("camera", "left"));

const crbutton = document.getElementById('cam-right');
crbutton.addEventListener('click', _ => move("camera", "right"));

async function move(device, direction) {
  try {     
    const response = await fetch('/move', {
      method: 'post',
      body: `{"device": "${device}", "direction": "${direction}"}`
    });
  } catch(err) {
    console.error(`Error: ${err}`);
  }
}
</script>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()
        
    def do_POST(self):
        if self.path == '/move':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                content_length = int(self.headers['Content-Length'])
                data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(data)
                print('device: {}'.format(data['device']))
                print('direction: {}'.format(data['direction']))
            except Exception as e:
                logging.warning(
                    'Got improper request %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()