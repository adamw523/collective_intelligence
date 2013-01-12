import httplib
from xml.dom.minidom import parse, parseString, Node

devKey = 'e29c88f6-03e6-41bc-96cf-b486908ddcb2'
appKey = 'AdamWisn-a537-450a-b061-7ec6d1d727e4'
certKey = 'da9902de-9ea0-4925-9c7a-172ea98273d4'
userToken = 'AgAAAA**AQAAAA**aAAAAA**I07JUA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCZeApw+dj6x9nY+seQ**qQUCAA**AAMAAA**U5p7o/wbdFqHi5gSamD4ZMqHzjwqRlZapK7zVydZgz6EQe+BHaserp13L6QSZrsRK7wqOk1B1jv9XNDUHU0cvu9tBOCydzRz2TBbvn1tg9poPuv22wDHdAWt24DoDFoPuQZ2V1EM3ZTyW+sKdk+TE5g0X3vipNcYRoI0v2jWNN1oRGxN8e01oLIgHcZB9DMjuuJ147RCRd2gi01qq3yLE4ATjM1xI4pS4E6NCghmKvH8FafQk4dUa4JNn6rx8hF55UXvBywAhvVX4UsQshGTkicko2/M5VnKywhR1U/usn+9WWz1obRKBRtH49ckHr8+fPVx63mkgbyIV3wMsheRfMnwLwlpT3Sk09u8VZUoF89Tmh/DwC0RHocwvxyMLdRu8kOn+NFmk6imkEwQKoGlyfHeaoV9fq8qQCUrY777cRpnGYL6iwjdD1At67clIwHofa9sx8HxiztU2kE+/z5AfRAGM9oTYnseHfHnz+YXzMzCm7jZ7Q9liZBheQVSteTa1xDNmOLYI5f9JBT/qk/KPSKy7yTglitW+Jn+3SokrcdFLlMv41V3iQXNm/u9n6zBshVeJxMx4/3+hAv4oi+Ct7wh9a1Y/Y3YsPaD6MN56sqkGY/At7FErIfANka0NSU2v+wJtAVLsF5pu6dsdYxir78WcfB+MKpBJSLQur5LBUDAMFLcYFEf9/Uw0Jm49dPqbyFq2ZXQJxMKK5IJRxDmiB06h/IeCVCVT0iiXRahGjQLjHrSzYLuPwBM/yEm1sbo'
serverUrl = 'api.ebay.com'

def getHeaders(apicall, siteID='0', compatabilityLevel='433'):
    headers = {'X-EBAY-API-COMPATIBILITY-LEVEL': compatabilityLevel,
                'X-EBAY-API-DEV-NAME': devKey,
                'X-EBAY-API-APP-NAME': appKey,
                'X-EBAY-API-CALL-NAME': apicall,
                'X-EBAY-API-SITEID': siteID,
                'Content-Type': 'text/xml'}
    return headers

def sendRequest(apicall, xmlparameters):
    connection = httplib.HTTPSConnection(serverUrl)
    connection.request('POST', '/ws/api.dll', xmlparameters,
            getHeaders(apicall))
    response = connection.getresponse()
    if response.status != 200:
        print 'Error sending request: ' + response.reason
    else:
        data = response.read()
        connection.close()

    return data

def getSingleValue(node, tag):
    nl = node.getElementsByTagName(tag)
    if len(nl) > 0:
        tagNode = nl[0]
        if tagNode.hasChildNodes():
            return tagNode.firstChild.nodeValue
    return '-1'

def doSearch(query,categoryID=None,page=1):
  xml = "<?xml version='1.0' encoding='utf-8'?>"+\
        "<GetSearchResultsRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
        "<RequesterCredentials><eBayAuthToken>" +\
        userToken +\
        "</eBayAuthToken></RequesterCredentials>" + \
        "<Pagination>"+\
          "<EntriesPerPage>200</EntriesPerPage>"+\
          "<PageNumber>"+str(page)+"</PageNumber>"+\
        "</Pagination>"+\
        "<Query>" + query + "</Query>"
  if categoryID!=None:
    xml+="<CategoryID>"+str(categoryID)+"</CategoryID>"
  xml+="</GetSearchResultsRequest>"
  print xml

  data=sendRequest('GetSearchResults',xml)
  print data
  response = parseString(data)
  itemNodes = response.getElementsByTagName('Item');
  results = []
  for item in itemNodes:
    itemId=getSingleValue(item,'ItemID')
    itemTitle=getSingleValue(item,'Title')
    itemPrice=getSingleValue(item,'CurrentPrice')
    itemEnds=getSingleValue(item,'EndTime')
    results.append((itemId,itemTitle,itemPrice,itemEnds))
  return results

def getCategory(query='',parentID=None,siteID='0'):
  lquery=query.lower()
  xml = "<?xml version='1.0' encoding='utf-8'?>"+\
        "<GetCategoryInfoRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
        "<RequesterCredentials><eBayAuthToken>" +\
        userToken +\
        "</eBayAuthToken></RequesterCredentials>"+\
        "<DetailLevel>ReturnAll</DetailLevel>"+\
        "<ViewAllNodes>true</ViewAllNodes>"+\
        "<CategorySiteID>"+siteID+"</CategorySiteID>"
  if parentID==None:
    xml+="<LevelLimit>1</LevelLimit>"
  else:
    xml+="<CategoryParent>"+str(parentID)+"</CategoryParent>"
  xml += "</GetCategoryInfoRequest>"
  data=sendRequest('GetCategories',xml)
  categoryList=parseString(data)
  catNodes=categoryList.getElementsByTagName('Category')
  for node in catNodes:
    catid=getSingleValue(node,'CategoryID')
    name=getSingleValue(node,'CategoryName')
    if name.lower().find(lquery)!=-1:
      print catid,name

def getItem(itemID):
  xml = "<?xml version='1.0' encoding='utf-8'?>"+\
        "<GetItemRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
        "<RequesterCredentials><eBayAuthToken>" +\
        userToken +\
        "</eBayAuthToken></RequesterCredentials>" + \
        "<ItemID>" + str(itemID) + "</ItemID>"+\
        "<DetailLevel>ItemReturnAttributes</DetailLevel>"+\
        "</GetItemRequest>"
  data=sendRequest('GetItem',xml)
  result={}
  response=parseString(data)
  result['title']=getSingleValue(response,'Title')
  sellingStatusNode = response.getElementsByTagName('SellingStatus')[0];
  result['price']=getSingleValue(sellingStatusNode,'CurrentPrice')
  result['bids']=getSingleValue(sellingStatusNode,'BidCount')
  seller = response.getElementsByTagName('Seller')
  result['feedback'] = getSingleValue(seller[0],'FeedbackScore')

  attributeSet=response.getElementsByTagName('Attribute');
  attributes={}
  for att in attributeSet:
    attID=att.attributes.getNamedItem('attributeID').nodeValue
    attValue=getSingleValue(att,'ValueLiteral')
    attributes[attID]=attValue
  result['attributes']=attributes
  return result


