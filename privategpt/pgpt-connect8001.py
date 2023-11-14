from gradio_client import Client
import os
import requests
import json

# NOTE: You need the Docker container maadsdocker/privategpt running for this API to work:
# 1. docker pull: docker pull maadsdocker/tml-privategpt-no-gpu-amd64
# 2. Docker Run: docker run -d -p 8001:8001 --env PORT=8001 maadsdocker/tml-privategpt-no-gpu-amd64:latest

############### GRADIO Client
def chat(port):
  client = Client("http://localhost:" + port + "/")
  result = client.predict(
		"if a fire extinguher is not charged, and it is not in a critical area, is this high, medium, or low priority? Choose one priority.",	# str  in 'Message' Textbox component
		"LLM Chat",	# str  in 'Mode' Radio component
		"testdoc.txt",	# str (filepath on your computer (or URL) of file) in 'Upload a File' Uploadbutton component
		api_name="/chat"
  )
  print(result)

  #client.view_api(return_format="dict")

############### REST API Client

def getingested(docname,port):
  url="http://127.0.0.1:" + port + "/v1/ingest/list"
  docids = []
  docidsstr = []

  obj=requests.get(url)
  js = json.loads(obj.text)
  for j in js["data"]:
     if j["doc_metadata"]["file_name"]==docname:
        #print(j["doc_id"])
        docids.append(j["doc_id"])
        docidsstr.append(j["doc_id"])

  #print(obj.text)
  docstr= (', '.join('"' + item + '"' for item in docids))

  #print(docidsstr)
  
  return docids,docstr,docidsstr

def deleteingested(docids, port):
  url="http://127.0.0.1:" + port + "/v1/ingest/"

  for j in docids:
     obj=requests.delete(url+j)
     print(obj.text) 


def gradiorestget(port):
  #url="http://127.0.0.1:8001/run/predict"
  url="http://127.0.0.1:" + port + "/health"

  obj=requests.get(url)

  print(obj.text) 

def gradiorestpostchat(prompt,context,docfilter,port):
  #url="http://127.0.0.1:8001/run/predict"
  url="http://127.0.0.1:" + port + "/v1/completions"

    
  headers = {"content-type": "application/json"}
  if docfilter != "":
    payload = {
          "include_sources": False,
          "prompt": prompt,
          "stream": False,
          "use_context": context,
          "context_filter": { "docs_ids": docfilter }
    }
   # print(payload)  
  else:
    payload = {
          "include_sources": False,
          "prompt": prompt,
          "stream": False,
          "use_context": context
    }
     
  #payload = {"data": [prompt,"Query Docs","ar2022-eng.pdf"]}
  #print(payload)  
  obj=requests.post(url, json=payload,headers=headers)

  print(obj.text) 

def ingestfile(mainfile, port):
  url="http://127.0.0.1:" + port + "/v1/ingest"

  files = {
    'file': (mainfile, open(mainfile, 'rb')),
  }

#  headers = {"Content-Type": "multipart/form-data"}

  obj=requests.post(url, files=files)

  print(obj.text) 
  
def getcontext(docname,mainport):
  ingestfile(docname,mainport)

  # Generate embeddings  
  docids,docstr,docidsstr=getingested(docname,mainport)
  return docids,docstr,docidsstr
############################################# CONTEXT
# Ingest file for context
docname="ar2022-eng.pdf"
mainport = "8001"

# Get context for privateGPT
docids,docstr,docidsstr=getcontext(docname,mainport)


#gradiorestpostchat("if a fire extinguher is not charged, and it is not in a critical area, is this high, medium, or low priority? Choose one priority.",False,"",mainport)
#gradiorestpostchat("What is Fintrac's main conclusions?",True,"",mainport)
#gradiorestpostchat("What is Sara's message?",True,"",mainport)
#gradiorestpostchat("What are the main challenges that Fintrac faces? And, how is it addressing these challenges?",True,"",mainport)
#gradiorestpostchat("What is Fintrac's goals? How much money are speding to acheive the goals?",True,"",mainport)
gradiorestpostchat("Can you give a full summary of this document?",True,docidsstr,mainport)

##########################################################




