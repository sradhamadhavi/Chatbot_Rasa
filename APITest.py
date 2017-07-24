# from zeep import Client,xsd
# import sys
# import xml.etree.ElementTree as ET
# client=Client('http://ecommercedemo.sparity.com/api/v2_soap?wsdl=1')
# sessionID=client.service.login('NAV_User','NAV_User')
# # print(sessionID)
# # response=client.service.catalogProductInfo(sessionID,2933,'','','')
# # try:
# # retType=client.get_type('ns0:catalogProductEntityArray')
# # print(retType)
# # response=retType(client.service.catalogProductList(sessionID,'','',''))
# resp=client.service.catalogProductList(sessionID,'','','').item[0]
# # resp=client.service.catalogProductInfo(sessionID,2933,'','','').product_id
# print(resp)
# # except:
# # 	for ex1 in sys.exc_info:
# # 		print(ex1)

# # with client.options(raw_response=True):
# # 	response = client.service.catalogProductList(sessionID,'','','')
# import magento
# from magento import catalog
# client = magento.Product('http://ecommercedemo.sparity.com/api/v2_soap?wsdl=1', 'NAV_User', 'NAV_User')
# products = client.currentStore('','')
# print(products)
################################
# from magento.api import API
# from magento import catalog
# import magento

# client=magento.Product('http://ecommercedemo.sparity.com/api/v2_soap?wsdl=1', 'NAV_User', 'NAV_User')
# sku='C11B'
# print(client)
##########################################
import magento
import redis
redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
redis_db.flushdb()

url = 'http://ecommercedemo.sparity.com/'
apiuser =  'NAV_User'
apipass =  'NAV_User'

with magento.Inventory(url, apiuser, apipass) as inventory_api:   
    AllProducts = inventory_api.list([4644,4650,4662,4668,4704,4750,4756,20193,20194,20195])
    for product in AllProducts:
    	redis_db.set(product['product_id'],product['is_in_stock'])
    	print(redis_db.get(product['product_id']))

    	



   
# with magento.Product(url, apiuser, apipass) as product_api:
#     # order_filter = {'created_at':{'from':'2011-09-15 00:00:00'}}
#     products = product_api.list()
#     print(products[0])
