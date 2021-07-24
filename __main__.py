import io
import os
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import json
import cat_detector as cd
from PIL import Image
import motor_control

PAGE="""\
<html>
<head>
<title>Robot Dog</title>
</head>
<body>
<center><h1>Control the Robot Dog</h1></center>
<center><h2 id="cat_label">Waiting for Data</h2></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
<center><button id='dog-forward'>Forward</button>
<button id='dog-backward'>Backward</button>
<button id='dog-stop'>Stop</button>
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

const dsbutton = document.getElementById('dog-stop');
dsbutton.addEventListener('click', _ => move("dog", "stop"));

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

var catChecker = setInterval(function() {
  let xhr = new XMLHttpRequest();
  xhr.open('GET', '/cat', true);
  xhr.onload = function () {
    var ret_data = this.responseText;
    
    if (ret_data.length > 0) {
      var catlab = document.getElementById('cat_label');
      if (ret_data.includes("True")) {
        catlab.innerHTML = 'Doggy sees a cat';
      } else {
        catlab.innerHTML = "Doggy doesn't see a cat";
      }
        
    }
  };
  xhr.send();
}, 1000);

</script>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
    
    def read(self):
        return self.frame

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
        elif self.path == '/cat':
            with output.condition:
                output.condition.wait()
                frame = output.frame
            img = Image.open(io.BytesIO(frame))
            hasCat = catDetector.isCatImage(img)
            if hasCat:
                os.system('omxplayer --no-keys Dog.mp3 &')
            content = str(hasCat).encode('utf-8')
                
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
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
                if data['device'] == 'dog' and data['direction'] == 'forward':
                    dog.move_forward()
                elif data['device'] == 'dog' and data['direction'] == 'backward':
                    dog.move_backward()
                elif data['device'] == 'dog' and data['direction'] == 'stop':
                    dog.stop_moving()
                elif data['device'] == 'dog' and data['direction'] == 'left':
                    dog.turn_left()
                elif data['device'] == 'dog' and data['direction'] == 'right':
                    dog.turn_right()
                elif data['device'] == 'camera' and data['direction'] == 'up':
                    dog.move_camera(pan=-10)
                elif data['device'] == 'camera' and data['direction'] == 'down':
                    dog.move_camera(pan=10)
                elif data['device'] == 'camera' and data['direction'] == 'left':
                    dog.move_camera(tilt=10)
                elif data['device'] == 'camera' and data['direction'] == 'right':
                    dog.move_camera(tilt=-10)
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

with picamera.PiCamera(resolution='640x480', framerate=16) as camera:
    dog = motor_control.Dog()
    catDetector = cd.CatDetector('./CatNet13-07-2021-1050.pickle')
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    camera.rotation = 180
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()