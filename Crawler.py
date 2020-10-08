import re
import socket
import sys

# author Chen Gu, Jiahao Song
#
CSRFTOKEN = ""
SESSIONID = ""
SESSIONID2 = ""
SIZE = 4096
HOST = "cs5700fa20.ccs.neu.edu"
SOCKET = ""
USER = sys.argv[1]
PASSWORD = sys.argv[2]
CONTENT_LENGTH = 560
CONNECTION = "Keep-Alive"
CONTNET_TYPE = "text/html; charset=utf-8"
ACCEPT_ENCODING = "gzip, deflate, br"
COOKIE = "csrftoken=" + CSRFTOKEN + "; sessionid=" + SESSIONID
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"

"""
process all the http request to the server
request: a string that represents the http request
"""
def processRequest(request):
    try:
        sc = socket.create_connection((HOST, 80))
        sc.sendall(request.encode('utf-8'))
    except socket.error:
        exit('failed')
    reply = sc.recv(4096)
    return reply.decode('utf-8')


"""
Generate the csrftoken and sessionid token and set to global variable
"""
def getToken():
    request = processRequest(
        "GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: " + HOST + "\r\n\r\n")

    csrftoken = re.compile(r'csrftoken=([a-z0-9]+)\;')
    sessionid = re.compile(r'sessionid=([a-z0-9]+)\;')
    try:
        global CSRFTOKEN
        CSRFTOKEN = csrftoken.findall(request)[0]
        global SESSIONID
        SESSIONID = sessionid.findall(request)[0]
    except IndexError:
        sys.exit("token generate failed")


"""
get the new sessionid after login
"""
def login():
    requestbody = 'csrfmiddlewaretoken=' + CSRFTOKEN + '&username=' + USER \
                  + '&password=' + PASSWORD + '&next=/fakebook'
    request = "POST /accounts/login/ HTTP/1.1\r\nHost: " + HOST + "\r\nConnection: keep-alive\r\nContent-Length: " \
              + str(len(requestbody)) + "\r\nContent-Type: application/x-www-form-urlencoded\r\nCookie: csrftoken=" \
              + CSRFTOKEN + "; sessionid=" + SESSIONID + "\r\n\r\n" + requestbody
    response = processRequest(request)
    sessionid = re.compile(r'sessionid=([a-z0-9]+)\;')
    try:
        global SESSIONID2
        SESSIONID2 = sessionid.findall(response)[0]
    except IndexError:
        sys.exit("location generate failed")


"""
generate the GET request
return: the page that we are going to crawl
"""
def getContent(url):
    # print(CSRFTOKEN)
    # print(SESSIONID)
    data = "GET " + url + " HTTP/1.1\r\nHost: " + HOST + "\r\nConnection: keep-alive" + "\r\nCache-Control: max-age=0" + "\r\nCookie: csrftoken=" \
           + CSRFTOKEN + "; sessionid=" + SESSIONID2 + "\r\n\r\n"
    return processRequest(data)


"""
find all the urls that exist in current page
"""
def findUrl(page):
    urls = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
    links = urls.findall(page)
    return links


"""
find secret flags on current page 
parm: content: the current html page
flags: a list that contains all the flags 
return: the flags list with the new flag added
"""
def findSecretFlag(content, flags):
    reg = re.compile(r'style=\"color:red\">FLAG: (\w+)</h2>')
    flag = reg.findall(content)
    if flag:
        flags.extend(flag)
    return flags


"""
get the status code from the http response
"""
def getStatusCode(content):
    statusCode = re.findall(r"\D(\d{3})\D", content)
    if len(statusCode) != 0:
        # print("statue code is " + statusCode[0])
        return str(statusCode[0])
    return "-1"


"""
main program that process the crawl.
step: using BFS algorithm to process the crawl, 
startUrl: represents the start point of BFS, which is the first page of fakebook
urlList: the list that contains all the urls that needs to be crawled
visited: the list that records all the urls that has already been crawled, this meant to prevent the cycle in BFS
flagCont: count the number of flags we get
flagList: records all the secret flags that have been found
return: the flagList  
"""
def crawler(starturl):
    urlList = [starturl]
    visited = [starturl]
    flagCount = 0
    flagList = []
    count = 0
    while flagCount != 5 and len(urlList) != 0:
        url = urlList.pop()
        pageContent = getContent(url)
        flagList = findSecretFlag(pageContent, flagList)
        count+=1
	# print("Searching webpage : " + str(count))
        if flagCount != len(flagList):
            flagCount += 1
        newUrls = findUrl(pageContent)
        for u in newUrls:
            if u not in visited:
                urlList.append(u)
                visited.append(u)
        statusCode = getStatusCode(pageContent)
        # if encounter the 500 error or any other bad request, resend the request
        if statusCode != "200":
            getContent(url)
            urlList.insert(0, url)
        # print("%%%%%%%%%%%%%%%%%%%%%Current Flag are %%%%%%%%%%%%%%%%%%%%%%%")
        # print(flagList)
    return flagList


"""
initialize the program
"""
def main():
    getToken()
    login()
    lst = crawler("/fakebook/")
    # print("\n*********Final secret flags are**************")
    for item in lst:
    	print(item.__str__())
    # print("***********************************************\n")
    #print(crawler("/fakebook/"))

main()
