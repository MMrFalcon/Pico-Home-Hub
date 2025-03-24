
# Available types: 1 - JSON, 2 - HTML
response_type_header = "X-RESPONSE-TYPE:"

class ResponseType():
    class _JSON:
        value = '1'
        def __str__(self):
            return "JSON"
        
        def getValue(self):
            return self.value
        
    class _HTML:
        value = '2'
        def __str__(self):
            return "HTML"
        
        def getValue(self):
            return self.value

    JSON = _JSON()
    HTML = _HTML()

class RequestMethod():
    class _GET:
        value = 'GET'
        def __str__(self):
            return "GET"
        
        def getValue(self):
            return self.value
        
    class _POST:
        value = 'POST'
        def __str__(self):
            return "POST"
        
        def getValue(self):
            return self.value
        
    class _PUT:
        value = 'PUT'
        def __str__(self):
            return "PUT"
        
        def getValue(self):
            return self.value
        
    class _DELETE:
        value = 'DELETE'
        def __str__(self):
            return "DELETE"
        
        def getValue(self):
            return self.value
        
    GET = _GET()
    POST = _POST()
    PUT = _PUT()
    DELETE = _DELETE()
        
class HttpRequest:

    responseType: ResponseType = ResponseType.HTML
    requestMethod: RequestMethod = RequestMethod.GET
    endpoint: str = ''

    def __init__(self, requestString: str):
        self.responseType = self._getResponseType(requestString)
        print("# {}".format(requestString))
        requestParts: list[str]= self._getRequestParts(requestString)
        print("### {}".format(requestParts))
        self.requestMethod = self._getRequestMethod(requestParts)
        self.endpoint = self._getRequestEndpoint(requestParts)

    def _getResponseType(self, request: str) -> ResponseType: 
        try:
            headerStart = request.find(response_type_header)
            if headerStart == -1:
                print("Header not found; defaulting to HTML.")
                return ResponseType.HTML
        
            headerValue = request[headerStart + len(response_type_header):].split("\r\n", 1)[0].strip()
            print(f"Extracted response type header: '{headerValue}'")

            if headerValue.startswith(ResponseType.JSON.getValue()):
                return ResponseType.JSON
            else:
                return ResponseType.HTML

        except IndexError as e:
            print("Error parsing the response type header, defaulting to HTML.", e)
            return ResponseType.HTML
    
        except Exception as e:
            print("An unexpected error occurred. Getting default response type.", e)
            return ResponseType.HTML
        
    def _getRequestMethod(self, requestParts: list[str]) -> RequestMethod:
        try:
            requestMethodString = requestParts[0].strip()
            print("Request method string: {}".format(requestMethodString))

            if (requestMethodString == RequestMethod.GET.getValue()):
                return RequestMethod.GET
            elif (requestMethodString == RequestMethod.PUT.getValue()):
                return RequestMethod.PUT
            elif (requestMethodString == RequestMethod.POST.getValue()):
                return RequestMethod.POST
            elif (requestMethodString == RequestMethod.DELETE.getValue()):
                return RequestMethod.DELETE
            else:
                print("Request method not found; defaulting to GET.")
                return RequestMethod.GET
            
        except IndexError as e:
            print("Error parsing the response type header, defaulting to HTML.", e)
            return ResponseType.HTML
    
        except Exception as e:
            print("An unexpected error occurred. Getting default response type.", e)
            return ResponseType.HTML
        
    def _getRequestEndpoint(self, requestParts: list[str]) -> str:
        try:
            return requestParts[1]
        except IndexError as e:
            print("Error parsing the response type header, defaulting to empty string.", e)
            return ''
        except Exception as e:
            print("An unexpected error occurred. Getting default response endpoint.", e)
            return ''
        
    def _getRequestParts(self, requestString: str) -> list[str]:
        try:
            # First characters are b'GET ...b=0, '=1.
            return requestString[2:].split()
        except IndexError as e:
            print("Error parsing the response type header, defaulting to ''.", e)
            return ['']
        except Exception as e:
            print("An unexpected error occurred. Getting default response endpoint.", e)
            return ['']
        
    def __str__(self):
        return f"""{self.endpoint}, {self.requestMethod}, {self.responseType}"""