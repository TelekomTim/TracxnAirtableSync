'''
TRACXN-AIRTABLE INTERFACE 1.0.0
This programm allows you to import company profiles into your Airtable base.

To run the programm properly you need to:
- 

Features:
1. 
2.
3.
4.

To be implemented:
1.
2.
3.
'''
#Airtables library for Python requests
from pyairtable import Api, utils
# HTTP-library to make the calls to the tracxn API
import requests 
#Recieves the API token, which should be stored in the system variables
import os
#Formats the response from tracxn 
import json
#Helps to format each company-URL into a format Traxcn takes to search for the company
from urllib.parse import urlparse


def getAirtableAPI():
    airtable_key = os.getenv("API_KEY_AIRTABLE")
    if airtable_key: 
        return Api(airtable_key)
    else:
        raise Exception("No Airtable API token found in OS. Please save the token under 'API_KEY_AIRTABLE'")

def getAirtableTable(fBaseKey, fTableKey):
    try:
        return airtable_api.table(fBaseKey, fTableKey)
    except:
        raise Exception("Table not found. Please check the Base Key nad the Table Key")
    

def getTraxcnToken():
    tracxn_token = os.getenv("API_KEY_TRACXN")
    
    if tracxn_token != "none":
        return tracxn_token
    else:
        raise Exception("No Tracxn API token found in OS. Please save the token under 'API_KEY_TRACXN'")
    

def requestData(fUrl):
    url = fUrl
    requestBody = {
        "filter":{
            "domain":[
                simplifyUrl(url)
                ]
        }
    }
    #Actual Traxcn request happeninghere
    #NOTE: Explain the request library and why we use this to make the request
    result = requests.post("https://tracxn.com/api/2.2/companies", headers={'accessToken': tracxn_token}, json=requestBody)

    if result == "":
        raise Exception("Company not found in Traxcn Database")
    else:
        return result.json()

#TODO: Check if this is bullet proof for Tracxn API
def simplifyUrl(fUrl):
    url = fUrl
    # Check if the URL has a scheme. If not, prepend 'http://'.
    if not urlparse(url).scheme:
        url = 'http://' + url

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Remove 'www.' if it exists
    if domain.startswith('www.'):
        domain = domain[4:]

    # Remove port number if it exists
    domain = domain.split(':')[0]

    return domain


'''
The dictionary (fFieldNames) is used to track:
1. What data should be added to the table
2. In which field the data should be stored

For this:
1. The data where there is no field provided or available will not be filled in
2. The data that is not provided from Tracxn will be empty (?)

The structure should look like the following:


'''
#TODO: How to make check for URL (existence) a boolean?
def addDataToTable(fDataDict, table, checkForURL = False):
    if checkForURL == False:
        table.create(fDataDict)
        return True
    else:
        tableContent = table.all()
        for rows in tableContent:
            for field in rows["fields"]:
                if field == fieldNames["URL"]:
                    if rows["fields"][field] == fDataDict[fieldNames["URL"]]:
                        print(rows["fields"][field] + " has already been fed to the table.")
                        return False
        else:
            table.create(fDataDict)
            return True



def extractData(jsonFile, fieldNames):
    dataDict = dict()
    for company in jsonFile.get("result", []):
        for field in fieldNames:
            if fieldNames[field] != None:
                try:
                    #Matches the JSON structure to the field names in Airtable
                    if field == "Name":
                        dataDict[fieldNames[field]] = company.get('name', '')

                    elif field == "Logo":
                        dataDict[fieldNames[field]] = utils.attachment(company['logos']['imageUrl']) if company['logos']['imageUrl'] else [],

                    elif field == "Short Description":
                        dataDict[fieldNames[field]] = company['description']['short']

                    elif field == "Long Description":
                        dataDict[fieldNames[field]] = company['description']['long']

                    elif field == "Headquaters":
                        dataDict[fieldNames[field]] = ", ".join([company['location']['city'], company['location']['country'], company['location']['continent']])

                    elif field == "Founded Year":
                        dataDict[fieldNames[field]] = str(company['foundedYear']) + "-01-01"

                    elif field == "Employee Count":
                        dataDict[fieldNames[field]] = company['latestEmployeeCount']['value']

                    elif field == "URL":
                        dataDict[fieldNames[field]] = company.get('domain', '')
                except:
                    dataDict[fieldNames[field]] = ''
    return dataDict




    

#TODO: Name arguments correctly
#TODO: Find out baseKey & TableKey via the link of the Base
#TODO: Get to know the Main function better
#TODO: How to ensure the right arguments are being given?

#def tracxn_airtable_api_main(fCompanyUrl, fBaseKey, fTableKey):

company_url = "hiya.com"
baseKey = "appffsUqhuRXKiqmT"
tableKey = "tbl4oxAFNsMFdX3CB"

airtable_api = getAirtableAPI()
airtable_table = getAirtableTable(baseKey, tableKey)
tracxn_token = getTraxcnToken()

fieldNames = {
    "Name" :                "Name",
    "Logo" :                "Logo",
    "Short Description" :   "Description (short)",
    "Long Description" :    "Description (long)",
    "Headquaters" :         "Country",
    "Founded Year" :        "Founded year",
    "Employee Count" :      "Tracxn Score",
    "URL" :                 "URL"
}

addDataToTable(extractData(requestData(company_url), fieldNames), airtable_table, True)