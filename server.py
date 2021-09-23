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
    
    '''
    This api fetches data from the file specified in the endpoint
    '''
    def serve_read_file_request(self, filepath): 
        #Initialize variables
        base_url = lib.lib["baseUrl"]
        result = ""
        mimetype = mimetypes["binary"]
        status = status_flags["success"]
        url = base_url+filepath

        #Get last slug from the filepath/endpoint
        end_slug = url.split("/").pop()

        #Check if its a directory else redirect to file
        if(url.endswith("/")):
            url += "index.html"
        elif(os.path.isdir(url) and end_slug!=""):
            status = status_flags["moved_permanently"]
            url += "/index.html"

        # Try to read from file and set result, status and mimetype based on filetype
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

        #return data
        return status, result, mimetype

    def handle(self):
        #receive data from client
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        #parse data to get the endpoint
        endpoint = str(self.data).split(" ")[1]

        #Initialize default response variables
        result = ""
        mimetype = mimetypes["binary"]
        status = status_flags["success"]

        #Fetch file body based on endpoint only if tis a GET request
        if("GET" not in str(self.data).split(" ")[0]):
            status = status_flags["method_not_allowed"]
        else:
            status, result, mimetype = self.serve_read_file_request(endpoint) #Api call to fetch file data
            
        #Create response String
        response = f"{lib.lib['protocol']} {status}\r\nContent-Type: {mimetype}\r\nContent-Length: {len(result)}\r\nConnection: closed\r\n\r\n{result}"
        
        #Send response back to client
        self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # # Activate the server; this will keep running until you
    # # interrupt the program with Ctrl-C
    server.serve_forever()