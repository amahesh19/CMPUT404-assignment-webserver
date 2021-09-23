#  coding: utf-8 
import socketserver, os
import lib

status_flags = lib.lib["status_flags"]
mimetypes = lib.lib["mimetypes"]

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):                    
    
    def serve_read_file_request(self, filepath): 
        base_url = lib.lib["baseUrl"]
        result = ""
        mimetype = mimetypes["text"]
        status = status_flags["success"]
        url = base_url+filepath

        end_slug = url.split("/").pop()

        if(url.endswith("/")):
            url += "index.html"
        elif(os.path.isdir(url) and end_slug!=""):
            status = status_flags["moved_permanently"]
            url += "/index.html"

        try:
            if(filepath.startswith("/../")):
                raise

            fileObj = open(url, 'r')
            result = fileObj.read()

            if(url.endswith(".css")):
                mimetype = mimetypes["css"]
            elif(url.endswith(".html")):
                mimetype = mimetypes["html"]
        except:
            status = status_flags["http_error"]

        return status, result, mimetype

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        endpoint = str(self.data).split(" ")[1]

        result = ""
        mimetype = mimetypes["text"]
        status = status_flags["success"]

        if("GET" not in str(self.data).split(" ")[0]):
            status = status_flags["method_not_allowed"]
        else:
            status, result, mimetype = self.serve_read_file_request(endpoint)
            
        response = f"{lib.lib['protocol']} {status}\r\nContent-Type: {mimetype}\r\nContent-Length: {len(result)}\r\nConnection: closed\r\n\r\n{result}"
        self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # # Activate the server; this will keep running until you
    # # interrupt the program with Ctrl-C
    server.serve_forever()