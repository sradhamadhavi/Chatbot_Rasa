
import os
import sys
import json
import requests
import pymysql
from flask import Flask, request,jsonify
from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig
import redis
import magento
import facebook
import config as cfg # this was added to read data from Config file
from collections import defaultdict
################################################################

Rest_url=cfg.Rest_url

######################################################################
redis_db = redis.StrictRedis(host=cfg.redis['host'], port=cfg.redis['port'], db=cfg.redis['db'])
model_directory=cfg.model_dir
metadata = Metadata.load(model_directory)   # where model_directory points to the folder the model is persisted in
interpreter = Interpreter.load(metadata, RasaNLUConfig("config.json"))
app=Flask(__name__)
        
##################################################################################################################################
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "12345":#os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200

##################################################################################################################################
def getRestDetails(page_id):
    try:
        response = requests.request("GET", Rest_url+str(page_id)[:4])
        global magento_url
        magento_url=response.json()['magento_api_endpoint']
        global magento_user
        magento_user=response.json()['magento_api_username']
        global magento_pwd
        magento_pwd=response.json()['magento_api_password']
        global fb_token
        fb_token=response.json()['fb_app_token']
        global fb_url
        fb_url=response.json()['fb_app_url']
        global graph
        graph=facebook.GraphAPI(access_token=fb_token, version='2.7') 
         
    except:
        log(sys.exc_info()[0])
    
##################################################################################################################################

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)
    if data["object"] == "page":
        for entry in data["entry"]:
            page_id=entry["id"]
           
            getRestDetails(page_id)
            
            for messaging_event in entry["messaging"]:
               
                sender_id = messaging_event["sender"]["id"]

                if messaging_event.get("message"):
                    try:
                        details = graph.get_object(id=sender_id)

                        message_text = messaging_event["message"]["text"]
                    except:
                        message_text=""
                        log(sys.exc_info()[0])
                   
                    if message_text=="Women" or message_text=="Accessories" or message_text=="Kids" or  message_text=="Men":
                        msgtextRes=defaultdict(lambda:sendSubCategory,{
                        ('Men','Women'):sendSubCategory,
                         'Accessories':sendAcc_Category,
                        'Kids':sendKids_Category

                        })
                        msgtextRes[message_text](sender_id,message_text)

                    elif (message_text=="Tops" or message_text=="Bottoms" or message_text=="Lounge + Sleepwear" or message_text=="Blankets" or message_text=="Boys Tops" 
                    or message_text=="Boys Bottoms" or message_text=="Girls Bottoms" or message_text=="Girls Tops" or message_text=="Infants"):
                        msgtextRes=defaultdict(lambda:setSubCategory,{
                        ('Tops','Bottoms','Lounge + Sleepwear','Blankets','Boys Tops','Boys Bottoms','Girls Bottoms','Girls Tops','Infants'):setSubCategory
                       
                        })
                        msgtextRes[message_text](sender_id,message_text)
                        

                    elif message_text=="Yes":
                        try:
                            kC=sender_id + "category"
                            kS=sender_id + "subcategory"
                            kR=sender_id + "rowOffset"
                           
                            category=redis_db.get(kC).decode("utf-8")
                            log("category is "+category)
                            subcategory=redis_db.get(kS).decode("utf-8")
                            
                            log(subcategory)
                            rowOffset=redis_db.get(kR).decode("utf-8")
                            log("ROWOffset "+rowOffset)
                            getData(sender_id,category,subcategory,rowOffset,"")
                        except:
                            log("in exception block of YES")
                            log(sys.exc_info()[0])
                            log(sys.exc_info()[1])

                    elif message_text== 'No':
                        send_Textmessage(sender_id,"Do you wish to start over again?")
                        QuickReplyCategory(sender_id)

                    else:
                        try:
                            global afterParse
                            afterParse=interpreter.parse(message_text)
                            msgIntent=afterParse["intent"]["name"]
                            # send_Textmessage(sender_id,msgIntent)
                            intentResponse=defaultdict(lambda: sendGreetMsg, 
                                {'greet': sendGreetMsg,
                                 'affirm': sendAffirmMsg,
                                 'shopping': sendShoppingMsg,
                                 'goodbye':sendGoodbyeMsg
                                })
                            intentResponse[msgIntent](sender_id=sender_id,details=details)                                         
                            
                        except: 
                            log("in exception block of Else")
                            log(sys.exc_info()[0])
                            log(sys.exc_info()[1]) 
                        


                elif messaging_event.get("postback"):
                    message_text = messaging_event["postback"]["payload"]
                    # log("inside postback")
                    # log( message_text)
                    if message_text=="START_OVER" or message_text=='MAIN_MENU':
                        redis_db.flushdb()
                        QuickReplyCategory(sender_id)
                        

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

               

    return "ok", 200

##################################################################################################################################
def sendSubCategory(sender,category):
    log(category)
    catDict=defaultdict(lambda:'unknown',
        {('men','male'):'male',
        ('women','female'):'female'
        })
    categoryToSet=catDict[category.lower()]
    redis_db.set(sender+"category",categoryToSet)
    log(redis_db.get(sender+"category").decode("utf-8"))

    messageData = {
    "text":"Shopping is Awesome. Browse through some of our collections",
    "quick_replies":[
    {
                "content_type":"text",
                "title":"Tops",
                "payload":"tops"
            },
                
            {
                "content_type":"text",
                        "title":"Bottoms",
                        "payload":"bottoms"
                    },
                    
                    {
                       "content_type":"text",
                        "title":"Lounge + Sleepwear",
                        "payload":"Lounge + Sleepwear"
                    }
                ]
           
    }

    send_message(sender,messageData)


##################################################################################################################################
def send_message(recipient_id, message_text):
    #log("sending message1 to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    #log(message_text)
    params = {"access_token":fb_token}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message":  message_text
        
    })
    
    r = requests.post(fb_url, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
##################################################################################################################################
def send_Textmessage(recipient_id, message_text):
    #log("sending message1 to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    #log(message_text)
    params = {"access_token":fb_token}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    })
    r = requests.post(fb_url, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
##################################################################################################################################

def log(message):  # simple wrapper for logging to stdout on heroku
    print (str(message))
    sys.stdout.flush()
##################################################################################################################################
# def sendMessageSample(sender,text):
#     recipient = messages.Recipient(sender)
#     # Send text message
#     message = messages.Message(text=text)
#     request = messages.MessageRequest(sender, message)
#     messenger.send(request)
##################################################################################################################################


def sendKids_Category(sender,msgText):
    redis_db.set(sender+"category",msgText)
    messageData = {
            "text":"We have amazing collection for Apple of your eye.Please choose the category",
            "quick_replies":[
            
       
                    {
                        "content_type":"text",
                        "title":"Boys Tops",
                        "payload":"Boys Tops"
                    },
                    {
                        "content_type":"text",
                        "title":"Girls Tops",
                        "payload":"Girls Tops"
                    },
                    {
                        "content_type":"text",
                        "title":"Girls Bottoms",
                        "payload":"Girls Bottoms"
                    },
                    {
                        "content_type":"text",
                        "title":"Boys Bottoms",
                        "payload":"Boys Bottoms"
                    },
                    {
                        "content_type":"text",
                        "title":"Infants",
                        "payload":"INFANTS"
                    }
                ]
           
    }
    send_message(sender,messageData)
##################################################################################################################################

def sendAcc_Category(sender,msgText):
    redis_db.set(sender+"category",msgText)
    messageData={
            "text":"Accessories definitely enhance the looks.Here are some",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Blankets",
                "payload":"BLANKETS"
            }
            ]  
    }
    send_message(sender,messageData)


##################################################################################################################################
def getData(sender,category,subCategory,rowOffset,colour):
    try:
        dbQuery=cfg.selectQuery
        dbRecCountQuery=cfg.countQuery
        log(subCategory.lower())
        options=defaultdict(lambda:cfg.topsTitle,{
            ('tops','t-shirts'):cfg.topsTitle+" and gender in ('"+category+"','unisex') ",
            'bottoms':cfg.bottomsTitle+" and gender in ('"+category+"','unisex')  ",
            'lounge + sleepwear':cfg.sleepWearTitle+" and gender in ('"+category+"','unisex')  ",
            'blankets':cfg.blanketsTitle,
            'boys bottoms':cfg.boysBottomsTitle,
            'girls bottoms':cfg.girlsBottomsTitle,
            'girls tops':cfg.girlsTopsTitle,
            'boys tops':cfg.boysTopsTitle,
            'infants':cfg.infantsTitle

            })
        if colour =="":
            filterCond=options[subCategory.lower()]+"limit "+str(rowOffset)+",10"
        else:
            filterCond=options[subCategory.lower()]+" and color='"+colour+"'""limit "+str(rowOffset)+",10"

        dbQuery=dbQuery+filterCond
        log(dbQuery )
        dbRecCountQuery=dbRecCountQuery+filterCond
      
                  
        conn=pymysql.connect(cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['passwd'],cfg.mysql['db'])
           
        cursor=conn.cursor()    
        cursor.execute(dbQuery)
        rows=cursor.fetchall()
        productList=[]
        for row in rows:
            productList.append(row[0])
        
        i=0
        try:
            with magento.Inventory(magento_url, magento_user, magento_pwd) as inventory_api:
                AllProducts = inventory_api.list(productList)
                
                for product in AllProducts:
                    if product['is_in_stock']=="1" or product['is_in_stock']==True:
                        redis_db.set(sender+product['product_id'],"In Stock")
                    else:
                        redis_db.set(sender+product['product_id'],"Out of Stock")
                    # log(redis_db.get(product['product_id']))
        except:
            log("in magento")
            log(sys.exc_info()[0])
            log(sys.exc_info()[1])
            log(sys.exc_info())

        messageData="{\"attachment\": {\"type\": \"template\",\"payload\": {\"template_type\": \"generic\",\"image_aspect_ratio\":\"square\",\"elements\": [{"
        for row in rows:
            i=i+1
            messageData+="\"title\": \""+row[1]+"\",\"image_url\": \""+row[3]
            messageData+="\",\"subtitle\":\""+redis_db.get(sender+product['product_id']).decode("utf-8")+" |  Sizes Available:"+row[4]+"\""
            messageData+=",\"buttons\": [{\"type\": \"web_url\",\"url\": \""+row[2]+"\",\"title\": \"Click here to Buy\""
            messageData+="}],}"
            if i==cursor.rowcount:
                messageData+="] } }  }"
            else:
                messageData+=", {"
        cursor.close()
        conn.close()   
        
        send_message(sender,messageData)

        if rowOffset=="0":
            getRecCount(sender,dbRecCountQuery)
        redis_db.set(sender+"rowOffset",str(int(rowOffset)+10))
        
        if int(redis_db.get(sender+"dbRecCount"))>int(redis_db.get(sender+"rowOffset")):
            ShowMore(sender)
        else:
            send_Textmessage(sender,"Well, We have reached the end of collection. I am sure you liked some")
    except:
        log("inside  getData")
        log(sys.exc_info()[1])
        send_Textmessage(sender,"I wish I could help you.")

##################################################################################################################################
def getRecCount(sender,query):
    conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
    cursor=conn.cursor()
   
    try:
        cursor.execute(query)
        dbRecCount=cursor.fetchone()[0]
    except:
        log("inside new dbRecCount")
        log(sys.exc_info()[1])

    cursor.close()
    conn.close() 

    redis_db.set(sender+"dbRecCount", dbRecCount)

##################################################################################################################################

def QuickReplyCategory(sender):
    for key in redis_db.scan_iter(sender+'*'):
        log("this key will be deleted in QuickReplyCategory "+key.decode("utf-8"))
        redis_db.delete(key)
    messageData={
            "text":"I believe Shopping is an art and you are the best",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Men",
                "payload":"men"
            },
            {
                "content_type":"text",
                "title":"Women",
                "payload":"women"
            }, 
            {
                "content_type":"text",
                "title":"Kids",
                "payload":"KIDS"
            },
	        {
                "content_type":"text",
                "title":"Accessories",
                "payload":"ACCESSORIES"
            }
            ]  
    }
    send_message(sender,messageData)
##################################################################################################################################
def ShowMore(sender):
    messageData={
            "text":"Do you want to view more..?",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Yes",
                "payload":"YES"
            },
            {
                "content_type":"text",
                "title":"No",
                "payload":"NO"
            }
            ]  
    }
    send_message(sender,messageData)
##################################################################################################################################
def sendGreetMsg(**kwargs):
    sender=kwargs.get('sender_id')
    details=kwargs.get('details')
    for key in redis_db.scan_iter(sender+'*'):
        redis_db.delete(key)
    send_Textmessage(sender, "Hello "+details['first_name']+" "+details['last_name']+", How can I help you?")
    QuickReplyCategory(sender)
###############################################################
def sendAffirmMsg(**kwargs):
    sender=kwargs.get('sender_id')
    send_Textmessage(sender, "Good.Do you wish to browse through our collection again?")
###############################################################
def sendGoodbyeMsg(**kwargs):
    sender=kwargs.get('sender_id')
    send_Textmessage(sender, "Goodbye.See you soon again")
###############################################################
def sendShoppingMsg(**kwargs):
    sender=kwargs.get('sender_id')
    details=kwargs.get('details')
    
    for key in redis_db.scan_iter(sender+'*'):
        log("this key will be deleted "+key.decode("utf-8"))
        redis_db.delete(key)
    if(len(afterParse["entities"])>0):
        for msgEntity in afterParse["entities"]:
            msgKey=sender+msgEntity["entity"]
            msgValue=msgEntity["value"]
            log("Entity is "+" "+msgKey +"Value is "+msgValue)
            redis_db.set(msgKey,msgValue)
        if redis_db.get(sender+"category") is not None and redis_db.get(sender+"product") is None and redis_db.get(sender+"subcategory") is None:
            category=redis_db.get(sender+"category").decode("utf-8")
            categoryOptions=defaultdict(lambda: test2, 
                {'male': sendSubCategory,
                'female': sendSubCategory,
                'accessories': sendAcc_Category, 
                'kids': sendKids_Category})
          
            categoryOptions[category](sender,category)

        elif redis_db.get(sender+"category") is not None  and redis_db.get(sender+"subcategory") is not None:
            getData(sender,redis_db.get(sender+"category").decode("utf-8"),redis_db.get(sender+"subcategory").decode("utf-8"),"0","")

        elif redis_db.get(sender+"category") is not None  and redis_db.get(sender+"product") is not None and redis_db.get(sender+"colour") is not None:
            getData(sender,redis_db.get(sender+"category").decode("utf-8"),redis_db.get(sender+"product").decode("utf-8"),"0",redis_db.get(sender+"colour").decode("utf-8"))

        elif redis_db.get(sender+"category") is not None  and redis_db.get(sender+"product") is not None and redis_db.get(sender+"colour") is  None:
            getData(sender,redis_db.get(sender+"category").decode("utf-8"),redis_db.get(sender+"product").decode("utf-8"),"0","")
        else:
            sendSubCategory(sender)

#################################################################
def setSubCategory(sender,msgText):
    try:
        redis_db.set(sender+"subcategory",msgText)
        category=redis_db.get(sender+"category").decode("utf-8")
        redis_db.set(sender+"rowOffset","0")
        getData(sender,category,msgText,"0","")
    except:  
        log("in exception block of setSubCategory")
        log(sys.exc_info()[0])
        log(sys.exc_info()[1])

#################################################################
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')#,ssl_context=context)
