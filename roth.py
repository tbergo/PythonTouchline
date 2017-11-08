#!/usr/bin/env python

__author__      = "Lars-Georg S. Paulsen"
__copyright__   = "Copyright 2016, dev.n0ll.com"
__license__     = "GPL"
__version__     = "0.1"
__email__       = "lars.georg.paulsen@gmail.com"
__status__      = "Development"
__webpage__     = "https://dev.n0ll.com/roth-touchline/"

## Import 
import argparse
import requests
from lxml import etree
from prettytable import PrettyTable ## Only need if you want pretty output in status

## Setting Option arguments
parser = argparse.ArgumentParser(description='Python ROTH Touchline script')
parser.add_argument('-t','--target', help='ip/dns name of touchline device',required=True)
parser.add_argument('-m','--mode',help='Read/Write mode ', required=False)
parser.add_argument('-i','--id',help='EndPoint #', required=False)
parser.add_argument('-n','--name',help='Endpoint Name', required=False)
parser.add_argument('-v','--value',help='Value ', required=False)
args = parser.parse_args()
 
## Define global variables ##
host=args.target
headers = {'Content-Type': 'text/xml', 'User-Agent': 'Roth-Touchline.../1.05'} # Basic Headers needed :)

def read():
    x = args.id
    data = '<body><version>1.0</version><client>App</client><file_name>Controller</file_name><item_list_size>13</item_list_size><item_list><i><n>G'+x+'.kurzID</n></i><i><n>G'+x+'.ownerKurzID</n></i><i><n>G'+x+'.RaumTemp</n></i><i><n>G'+x+'.SollTemp</n></i><i><n>G'+x+'.OPMode</n></i><i><n>G'+x+'.WeekProg</n></i><i><n>G'+x+'.TempSIUnit</n></i><i><n>G'+x+'.SollTempMaxVal</n></i><i><n>G'+x+'.SollTempMinVal</n></i><i><n>G'+x+'.SollTempStepVal</n></i><i><n>G'+x+'.OPModeEna</n></i><i><n>G'+x+'.WeekProgEna</n></i><i><n>CD.rooms['+x+']</n></i></item_list></body>'
    xml=requests.post('http://'+host+'/cgi-bin/ILRReadValues.cgi', data=data, headers=headers).text
    r = etree.fromstring(xml)
    print(r.xpath('//i[n[text()="G'+args.id+'.'+args.name+'"]]/v/text()')[0])

def write():
    payload = {'G'+args.id+'.'+args.name: args.value}
    repons = requests.get('http://'+host+'/cgi-bin/writeVal.cgi', params=payload)
    print(repons.text)

def getcount():
   ## Get how many endpoints we can controll
   data = """ <body><version>1.0</version><item_list_size>1</item_list_size><item_list><i><n>totalNumberOfDevices</n></i></item_list></body> """
   xml=requests.post('http://'+host+'/cgi-bin/ILRReadValues.cgi', data=data, headers=headers).text
   respons = etree.fromstring(xml)
   numbers = respons.find('item_list/i/v')
   return int( numbers.text)

    
def status():
   numbers = getcount()
   ## Defining pretty table
   status = PrettyTable(["#", "Room", "Current Temp", "Target Temp", "Mode"])
   status.align['Room'] = "l"
   ## Loop through endpoints and get stats.
   print("Getting data from endpoints...")
   for x in range(0,numbers):
      x = str(x) ## concatenate 
      ## Define xml post statment
      room = '<body><version>1.0</version><client>App</client><file_name>Controller</file_name><item_list_size>13</item_list_size><item_list><i><n>G'+x+'.kurzID</n></i><i><n>G'+x+'.ownerKurzID</n></i><i><n>G'+x+'.RaumTemp</n></i><i><n>G'+x+'.SollTemp</n></i><i><n>G'+x+'.OPMode</n></i><i><n>G'+x+'.WeekProg</n></i><i><n>G'+x+'.TempSIUnit</n></i><i><n>G'+x+'.SollTempMaxVal</n></i><i><n>G'+x+'.SollTempMinVal</n></i><i><n>G'+x+'.SollTempStepVal</n></i><i><n>G'+x+'.OPModeEna</n></i><i><n>G'+x+'.WeekProgEna</n></i><i><n>CD.rooms['+x+']</n></i></item_list></body>'
      ## Send request and parse xml 
      xml=requests.post('http://'+host+'/cgi-bin/ILRReadValues.cgi', data=room, headers=headers).text
      r = etree.fromstring(xml)
   
      ## Collection values for room X
      ## Search for <n> tag, check parent for <v> and get value, only one value get first element
      Name            = r.xpath('//i[n[text()="CD.rooms['+x+']"]]/v/text()')[0]
      Mode            = r.xpath('//i[n[text()="G'+x+'.OPMode"]]/v/text()')[0]
      Temp_Target     = r.xpath('//i[n[text()="G'+x+'.SollTemp"]]/v/text()')[0]
      Temp_Current    = r.xpath('//i[n[text()="G'+x+'.RaumTemp"]]/v/text()')[0]
   
      ## Cleaning up Temp 
      Temp_Target = round(float(Temp_Target)/100,1)
      Temp_Current = round(float(Temp_Current)/100,1)

      ## Mode fix
      if Mode == "0":
         Mode = "Normal"
      elif Mode == "1":
         Mode = "Night"
      elif Mode == "2":
         Mode = "Holliday"
      ## Add values to PrettyTable
      status.add_row([x,Name,Temp_Current,Temp_Target,Mode])
   print(status)

if args.mode == "read":
    read()
elif args.mode == "write":
    write()
else:
    status()