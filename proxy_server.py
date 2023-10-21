import socket
from urllib.request import Request, urlopen, HTTPError

cache=[' ']
welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSocket.bind(('localhost',5005))
welcomeSocket.listen(50)
while True:
    print('WEB PROXY SERVER IS LISTENING')

    clientSocket, addr = welcomeSocket.accept()     #proxy server welcomeSocket accepts any client connection
    
    print('Connected by', addr)
    rawdata = clientSocket.recv(1024)               #original request is received from client

    data = str(rawdata, 'utf-8')                    #original byte data is decoded into a string
    print('MESSAGE RECEIVED FROM CLIENT: \n')
    print(data)
    print('END OF MESSAGE RECEIVED FROM CLIENT\n')
    # parsing the request

    first_line = data.split("\n")[0]                # parse the header
    method = first_line.split(" ")[0]               # get the method from header
    if len(first_line) > 1:
        url = first_line.split(' ')[1]                  # get the url
        httpv = first_line.split(' ')[2]                # get http version
    else:
        url = first_line
        httpv = first_line
    dest = url[1:len(url)]                          # get destination address
    message = data.split("\n")[2:6]                 
    get = ""
    for x in message:                               
        get = get + x + '\n'
    
    

    print('\n[PARSE MESSAGE HEADER]')               # display method, address, and http version
    print('METHOD = ', method, ', ', 'DESTADDRESS = ', dest, ', ', 'HTTPVersion = ', httpv)
    print('\n')
    print('\n')
    
    if method == 'GET':                             # GET methods enter main path
        flag = False
        destination = dest.split('/')               # parse destiantion address and used to determine size data received
        host = dest.split('/')[0]                   # get host from address
        if(len(destination) >= 2):
            link = dest[len(host):len(dest)]        # get link from address
        else:
            link = '/'
        
        if(len(destination) < 3):                   # if file does not exist then set to link else get file
            file = link
        else:
            file = link.split('/')[2]
        
        try:                                        # tries to find file in cache if found enter path
            fin = open('./' + file)             # opens cache file
            content = fin.read()                    # reads cache into content 
            fin.close()                             # closes cache file
        
            print('[LOOK UP THE CACHE]: FOUND IN THE CACHE: FILE = ', file)
            print('\n')
            print('RESPONSE HEADER FROM PROXY TO CLIENT: ')
            print(content.split('\n')[0])                # prints data of cached file
            print(content.split('\n')[12])
            print(content.split('\n')[14])
            content = content.encode('utf-8')
            clientSocket.send(content)              # sends cached data to client
            print('\nEND OF HEADER\n')
            
            
        except IOError:
            print('[LOOK UP THE CACHE]: NOT FOUND, BUILD REQUEST TO SEND TO ORIGINAL SERVER')
            print('[PARSE REQUEST HEADER] HOSTNAME IS ', host)
            if len(destination) > 1:                # if url exist then set
                print('[PARSE REQUEST HEADER] URL IS ', link[1:len(link)])
            if len(destination) > 2:                # if file exist then set
                print('[PARSE REQUEST HEADER] FILESNAME IS ', file)
                
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create serverSocket
            serverSocket.connect((host, 80))


            print('\nREQUEST MESSAGE SENT TO ORIGINAL SERVER:')
                                                    # compose request sent to original server            
            request = method + ' '+ link + ' ' + httpv + '\n' + 'Host: ' + host + '\r\n' + get
            request += 'Connection: close\r\nUpgrade-Insecure-Requests: 1\r\n\r\n'

            r = request.encode('utf-8')             # encodes request 
            print(request)                          # prints request sent
            serverSocket.sendall(r)                 # sends request to original server
            print('END OF MESSAGE SENT TO ORIGINAL SERVER\n')
            
            rawResp = serverSocket.recv(1024)       # saves original server's response
            serverSocket.close()                    # closes serverSocket
            
            if (len(rawResp) > 0):                  # if server response is not empty then send data to client
                clientSocket.send(rawResp)

          
            
            resp = str(rawResp, 'utf-8')            # convert original server response to string
            respHeader = resp.split('\n\r\n')[0]    # parse response header from original response
            print('RESPONSE HEADER FROM ORIGINAL SERVER:')
            print(respHeader)                       # print response header
            print('\nEND OF HEADER\n')
            cacheFile = 'cache/' + file
            header_first_line = respHeader.split('\n')[0]   # parses first line from response header
            resp_code = header_first_line.split(' ')[1]     # parses code from first line of response header

            if resp_code == '200':                          # if response code is 200 OK then enter path
                print('[WRITE FILE INTO CACHE]: ', cacheFile, '\n')
                cache_file = open("./" + file, "w")         # open cache file
                cache_file.write(resp)                      # save file into cache
                cache_file.close()                          # close cache file
                print('\nRESPONSE HEADER FROM PROXY TO CLIENT:')
                print(header_first_line)
                print(resp.split('\n')[8])
                print('\nEND OF HEADER\n')
            if resp_code == '404':                          # if response code is 404 NOT FOUND then enter path
                print('\nRESPONSE HEADER FROM PROXY TO CLIENT:')
                print(header_first_line)
                print(resp.split('\n')[1])
                print('\nEND OF HEADER\n')
            if resp_code == '302':                          # if response code is 302 OK then enter path
                print('\nRESPONSE HEADER FROM PROXY TO CLIENT:')
                print(respHeader)
                print('\nEND OF HEADER\n')
    else:                                                   # if request method is not GET then enter path
        host = dest.split('/')[0]                           # get host from address
        link = dest[len(host):len(dest)]                    # get link from address
        
        if(len(destination) < 3):                           # if file does not exist then set to link else get file
            file = link
        else:
            file = link.split('/')[2]
                                                            # create server socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.connect((host, 80))
                                                            # create request sent to original server
        print('\nREQUEST MESSAGE SENT TO ORIGINAL SERVER:')
        request = method + ' '+ link + ' ' + httpv + '\n' + 'Host: ' + host + '\r\n' + get
        request += 'Connection: close\r\nUpgrade-Insecure-Requests: 1\r\n\r\n'

        r = request.encode('utf-8')                         # encode request to original server
        print(request)                                      # print request to original server
        serverSocket.sendall(r)                             # send request to original server
        print('END OF MESSAGE SENT TO ORIGINAL SERVER\n')
        
        rawResp = serverSocket.recv(1024)                   # saves original server's response
        serverSocket.close()                                # close serverSocket

        if (len(rawResp) > 0):                              # if server response is not empty then send data to client
            clientSocket.send(rawResp)
   
        resp = str(rawResp, 'utf-8')                        # convert original server response to string
        respHeader = resp.split('\n\r\n')[0]                # parse response header from original response
        print('RESPONSE HEADER FROM ORIGINAL SERVER:')
        print(respHeader)                                   # print response header from original server
        print('\nEND OF HEADER\n')

        print('\nRESPONSE HEADER FROM PROXY TO CLIENT:')
        print(respHeader)                                   # print response header so client from proxy
        print('\nEND OF HEADER\n')
        
print('END OF PROXY SERVER')
exit()
  
