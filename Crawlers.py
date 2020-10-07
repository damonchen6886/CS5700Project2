import re
import socket
import sys

#author Chen Gu, Jiahao Song
#
CSRFTOKEN = ""
SESSIONID = ""
SESSIONID2 = ""
SIZE = 4096
HOST = "cs5700fa20.ccs.neu.edu"
SOCKET = ""
# USER = sys.argv[1]
# PASSWORD = sys.argv[2]
# Chen Gu
USER = '001969763'
PASSWORD = 'I7NVEDDJ'
# Jiahao Song
# USER = '001767233'
# PASSWORD = 'T7529SAA'
CONTENT_LENGTH = 560
CONNECTION = "Keep-Alive"
CONTNET_TYPE = "text/html; charset=utf-8"
ACCEPT_ENCODING = "gzip, deflate, br"
COOKIE = "csrftoken=" + CSRFTOKEN + "; sessionid=" + SESSIONID
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"




def processRequest(request):
    try:

        sc =socket.create_connection((HOST, 80))
        sc.sendall(request.encode('utf-8'))
    except socket.error:
        # Send failed
        exit('failed')

    reply = sc.recv(4096)
    # print(reply.decode('utf-8'))
    return reply.decode('utf-8')


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

    print("##############################")
    print("token generated: ")
    print("CSRFTOKEN" + CSRFTOKEN)
    print("SESSIONID" + SESSIONID)
    print("##############################")


def login():
    requestbody = 'csrfmiddlewaretoken=' + CSRFTOKEN + '&username=' + USER \
                  + '&password=' + PASSWORD + '&next=/fakebook'
    request = "POST /accounts/login/ HTTP/1.1\r\nHost: " + HOST + "\r\nConnection: keep-alive\r\nContent-Length: " \
              + str(len(requestbody)) + "\r\nContent-Type: application/x-www-form-urlencoded\r\nCookie: csrftoken=" \
              + CSRFTOKEN + "; sessionid=" + SESSIONID + "\r\n\r\n" + requestbody
    # print('[DEBUG]Post login:\n' + request)

    response = processRequest(request)

    sessionid = re.compile(r'sessionid=([a-z0-9]+)\;')

    try:
        global SESSIONID2
        SESSIONID2 = sessionid.findall(response)[0]

    except IndexError:
        sys.exit("location generate failed")
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("session id updated to" + SESSIONID2)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


def getContent(url):
    # print(CSRFTOKEN)
    # print(SESSIONID)
    data = "GET " + url + " HTTP/1.1\r\nHost: " + HOST + "\r\nConnection: keep-alive" + "\r\nCache-Control: max-age=0" + "\r\nCookie: csrftoken=" \
           + CSRFTOKEN + "; sessionid=" + SESSIONID2 + "\r\n\r\n"

    # print('[DEBUG]Post getulr++++++++++++++++++++++++++++:\n' + data.__str__())

    return processRequest(data)


def findUrl(page):
    urls = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
    links = urls.findall(page)
    print("\nnew links are ++++++++++++++++++++++++")
    print(links)
    print("++++++++++++++++++++++++++++++++++")
    return links


def findSecretFlag(content, flags):
    reg = re.compile(r'<h2 class=\'secret_flag\' style=\"color:red\">FLAG: (\w+)</h2>')
    # reg = re.compile(r'secret_flag')
    flag = reg.findall(content)
    if flag:
        flags.extend(flag)
    print("\nflags are +++++++++++++++++++++++")
    print(flags)
    print("+++++++++++++++++++++++++++++++++")
    # return flags
    # pattern = re.compile(r'<h2 class=\'secret_flag\' style=\"color:red\">FLAG: (\w+)</h2>')
    # flag = pattern.findall(content)
    #flag =re.findall(r'FLAG:', content, re.I)
    # flags.extend(flag)
    # flag = re.findall(r'Zop',content, re.I)
    # print('Page\n' + page)
    # if flag != []:
    #     flags.extend(flag)
    # print("\nflags are +++++++++++++++++++++++")
    # print(flags)
    # print("+++++++++++++++++++++++++++++++++")
    return flags


def processBadRequest(statusCode):
    if statusCode == "200":
        return 0
    if statusCode == "500":
        return 1
    if statusCode == "301":
        return 2
    if statusCode == "404" or statusCode == "403" or statusCode =="-1":
        return 3
    else:
        return -1


def getStatuCode(content):
    statusCode = re.findall(r"\D(\d{3})\D", content)
    if len(statusCode)!= 0:
        # print("statue code is " + statusCode[0])
        return str(statusCode[0])
    return "-1"


# getToken()
# login()
# content = getContent()
# lst = []
# getStatuCode(content)
# findSecretFlag(content, lst)
# # find more content
# findUrl(content)


def crawler(starturl):
    urlList = [starturl]
    visited = [starturl]
    flagCount = 0
    flagList = []

    visit = 0
    while flagCount != 5 and len(urlList) != 0 :
        # count+=1
        # if count> 1000:
        #     break;
        # count+=1
        url = urlList.pop()
        pageContent = getContent(url)
        flagList = findSecretFlag(pageContent, flagList)
        if flagCount != len(flagList):
            flagCount += 1
        newUrls = findUrl(pageContent)
        for u in newUrls:
            if u not in visited:
                urlList.append(u)
                visited.append(u)
        # if url not in visited:
        #     visit+=1
        statusCode = getStatuCode(pageContent)
        if(statusCode != "200"):
            getContent(url)
            urlList.insert(0, url)
            # print("inserted&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            # while statusCode == "500":
            #     pageContent = getContent(url)
            # while processBadRequest(statusCode) != 0:
            #     pageContent = getContent(url)
            #     statusCode = getStatuCode(pageContent)
            #     visit+=1
            # print("content &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            # print(pageContent)
            # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            # if len(pageContent) == 0:
            #     visited.append(url)
            #     continue
            # print(" &&&&&&&&&&&&&&&&&&\n")
            # getStatuCode(pageContent)
            # print(" &&&&&&&&&&&&&&&&&&\n")
            # curFlags = []
            # flagList = findSecretFlag(pageContent, flagList)
            # if flagCount != len(flagList):
            #     flagCount += 1
            # newUrls = findUrl(pageContent)
    #     print("cur urllist is &&&&&&&&&&&&&&&&&&\n")
    #     print(urlList)
    #     print('&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    #     # visited.append(url)
    #     print("visited are ****************\n")
    #     print(visited)
    #     print('*****************************')
    #     print("visit time = " )
    #     print(visit)
    # print("\nvisited size is "+ str(len(visited)))
    #
    # print(flagList)
    # print("flag counts ****************\n")
    # print(flagCount)
    # print('*****************************')
    return flagList


def main():
    getToken()
    login()
    # flags = []

    print(crawler("/fakebook/"))



main()

#
# getToken()
# login()
# # print(CSRFTOKEN)
# # print(SESSIONID)
# # print(SESSIONID2)
# result = getUrl()
# print(findUrl(result))
# #TODO BFS URL
# FIND SECRET FLAG
