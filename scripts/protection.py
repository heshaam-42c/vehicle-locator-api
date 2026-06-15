import sys
import requests
import re

# run:
# python3 protection.py apiId platform apiKey

apiId = ""
platform = ""
apiKey = ""

def matchUUID(uuid):
    return re.match("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", uuid)

def getArgs():
        global platform
        global apiId
        global apiKey

        if len(sys.argv) != 4:
            print("Error in number of args")
            sys.exit(1) #exit with error
        
        apiId = sys.argv[1]
        platform = sys.argv[2]
        apiKey = sys.argv[3]

        if not matchUUID(apiId):
            print("Error in api id format")
            sys.exit(1)

        # if not matchUUID(apiKey):
        #     print("Error in api key format")
        #     sys.exit(1)

def createProtections():
    url = platform + "/api/v1/apis/" + apiId + "/protection"

    headers = {}
    headers["X-API-KEY"] = apiKey

    r = requests.post(url, headers=headers)
    print ("Status Code: ", r.status_code)
    print ("Response: ", r.json())


def main():
    getArgs()
    createProtections()

main()