from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig
model_directory="./models/model_20170710-064728"
metadata = Metadata.load(model_directory)   # where model_directory points to the folder the model is persisted in
interpreter = Interpreter.load(metadata, RasaNLUConfig("config.json"))
##############################################
# query=u"show me some tops"
# Intent is shopping
# Entity is  product
# Category is tops
################################################
# query=u"men's t-shirts"
# Intent is shopping
# Entity is  category
# Value is men
# Entity is  product
# Value is t-shirts
################################################
# query=u"I want to shop. Can you please help me?"
# Intent is shopping
################################################
# query=u"Do you have men's tops?"
# Intent is shopping
# Entity is  category
# Value is men
# Entity is  product
# Value is tops
################################################
# query=u"show me women's t-shirts"
# Intent is shopping
# Entity is  category
# Value is women
# Entity is  product
# Value is t-shirts
################################################
query=u"Men"

result=interpreter.parse(query)
print(result)
print("Intent is "+result["intent"]["name"])
for msgEntity in result["entities"]:
	print("Entity is "+" "+msgEntity["entity"])
	print("Value is "+msgEntity["value"])
	
# 		result=interpreter.parse(query)
# print(result)
# print("Intent is "+result["intent"]["name"])
# for msgEntity in len(result["entities"]):
# 	print("Entity is "+" "+result["entities"][0]["entity"])
# 	print("Value is "+result["entities"][0]["value"])
# 	if len(result["entities"])>1:
# 		print("Entity is "+" "+result["entities"][1]["entity"])
# 		print("Value is "+result["entities"][1]["value"])
