# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 22:07:41 2016

@author: Sandeep Raikar

References:
http://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
http://stackoverflow.com/questions/27218415/python-socket-programming-with-multiple-threads
http://www.eurion.net/python-snippets/snippet/Threaded%20Server.html
http://ilab.cs.byu.edu/python/threadingmodule.html
http://www.tutorialspoint.com/python/python_networking.htm
"""
import socket
import _thread
import sys

# create a socket object
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# get local machine name
host = ''                           
port = 9999                                           
# bind to the port
tcpSerSock.bind((host, port))                                  
tcpSerSock.listen(1)                                               
cache_dict={} #dictionary to hold the cache informations

def proxy_server_impl(conn, client_addr):
    log = open('./log.txt', 'a')    
    message = conn.recv(2048)
    
    log.writelines("Length of request in bytes" +str(len(message)))
    if(not "GET" in str(message)):
        print("Unsupported method has been received, will not be processed.")
        conn.send(str.encode("Unsupported method has been received, will not be processed."))
        conn.close()
    else:
        print("GET HTTP method")
        if(len(cache_dict)>0):     
            print('Printing the contents of cache_dict')            
            for key, val in cache_dict.items():
                print(key,"-",val)
        
        message_parsed = message.decode('utf-8')
        http_request = message_parsed.split('\n')

        http_request_method = http_request[0].split(' ')[0]
        log.writelines("HTTP Method: " + http_request_method+"\n")    
        
        host_name = http_request[1].split(' ')[1]
        host_name= host_name.strip()
        http_request_method = http_request_method.strip()
        log.writelines("HOST Name: " + host_name+"\n")
        log.writelines("Received message: "+"\n")
        log.writelines(str(message))
        log.writelines('\n*************************************************\n')
        print(host_name)
        print(http_request_method)
        if(http_request_method=='GET'):
                        
            if(host_name in cache_dict):
                print("Returning from cache!!")
                with open(cache_dict[host_name], 'r') as content_file:
                    content = content_file.read()
                conn.send(str.encode(content))
                conn.close()
                print('done')
            else:
                print("create a new file and store contents here!!!!")             
                try:
                    
                    csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    csock.connect((host_name,80))
                    csock.send(message)
                    cache_dict[host_name]=host_name+".txt"
                    temp_file_name = host_name
                    temp_file_name.replace("www.","",1)
                    print("temp file name: ",temp_file_name)
                    cache_file = open(temp_file_name+".txt", "wb")
                    
                    output = csock.recv(4096)
                    if("400" in str(output)):
                        print("Bad request encountered")
                        conn.send(str.encode("400 - Bad request encountered"))
                        conn.close()
                        return
                    if("404" in str(output)):
                        print("404 - File not found encountered")
                        conn.send(str.encode("404 - File not found error code encountered"))
                        conn.close()
                        return
                    if("405" in str(output)):
                        print("405 - Method not found encountered")
                        conn.send(str.encode("405 - Method not found error code encountered"))
                        conn.close()
                        return
                    if("405" in str(output)):
                        print("405 - Method not found encountered")
                        conn.send(str.encode("405 - Method not found error code encountered"))
                        conn.close() 
                        return
                    if("500" in str(output)):
                        print("500 - Internal server encountered")
                        conn.send(str.encode("500 - Internal server error code encountered"))
                        conn.close() 
                        return
                    print(output)
                    if(len(output)>0):
                        conn.send(output)
                        cache_file.write(output)
                    
                    cache_file.close()
                    csock.close()
                    conn.close()
                except socket.error as msg:
                    print('Error: ', msg)
                    sys.exit(1)
        else:
            print("Unsupported method has been received, will not be processed")
            conn.send(str.encode("Unsupported method has been received, will not be processed"))
            conn.close()
if __name__ == '__main__':
    while True:
        conn_object, client_addr = tcpSerSock.accept()
        _thread.start_new_thread(proxy_server_impl, (conn_object, client_addr))