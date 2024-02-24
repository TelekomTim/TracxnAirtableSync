"""
TRACXN-AIRTABLE INTERFACE 1.0.0
--------------------------------
This program imports company profiles from Tracxn into an Airtable base.

Requirements:
1. Include a 'config.json' file with:
   a. "fields": Maps the data fields from Tracxn to the corresponding fields in Airtable.
      - Data with no corresponding field in Airtable will be ignored.
      - Fields not provided by Tracxn will remain empty in Airtable.
   b. "links": Contains URLs for the Airtable base/table and the target company.

2. Save your Tracxn API token as an environment variable (named 'API_KEY_TRACXN').
3. Save your Airtable API token with write permissions as an environment variable (named 'API_KEY_AIRTABLE').

Features:
1. Import any available company data from Tracxn into your Airtable tables (matching columns required) using the company URL.
2. Prevent duplicate imports of the same company data.

Future Enhancements:
1. Additional methods for importing companies.
2. Support for more data fields (e.g., categories).

Notes:
- The program checks for the existence of data and fields before importing to avoid duplicates.
- Ensure that the Airtable base has the necessary schema to accommodate the data being imported.
"""

# Import necessary libraries
from pyairtable import Api, utils     # Airtable library for Python requests.
import requests                        # HTTP library for making calls to the Tracxn API.
import os                              # To retrieve API tokens stored as system variables.
import json                            # For parsing and formatting JSON data from Tracxn.
from urllib.parse import urlparse      # Utility for formatting company URLs for Tracxn searches.
import re                              # Regular expression library for pattern matching in URLs.
import logging                         # Logging library for tracking events and errors.


def getAirtableAPI() -> Api:
    """
    Retrieves the Airtable API key from environment variables and returns an Api object.
    Raises a ValueError if the API key is not found.
    """
    airtable_key = os.getenv("API_KEY_AIRTABLE")
    if airtable_key: 
        return Api(airtable_key)
    else:
        raise ValueError("No Airtable API token found in OS. Please save the token under 'API_KEY_AIRTABLE'")


def getAirtableTable(fBaseKey: str, fTableKey: str, api: Api) -> Api.table:
    """
    Retrieves a specific table from Airtable using base key and table key.
    Raises a ValueError if the table is not found.
    """
    try:
        return api.table(fBaseKey, fTableKey)
    except:
        raise ValueError("Table not found. Please check the Base Key and the Table Key")
    

def getTraxcnToken() -> str:
    """
    Retrieves the Tracxn API token from environment variables.
    Raises a ValueError if the API token is not found or set to 'none'.
    """
    tracxn_token = os.getenv("API_KEY_TRACXN")
    if tracxn_token and tracxn_token.lower():
        return tracxn_token
    else:
        raise ValueError("No Tracxn API token found in OS. Please save the token under 'API_KEY_TRACXN'")
    

def request_data(url: str, tracxn_token: str) -> dict:
    """
    Requests data from the Tracxn API using the provided URL and token.
    Returns the JSON response.
    Raises an exception if the company is not found or if an error occurs.
    """
    request_body = {
        "filter":{"domain":[simplify_url(url)]}
    }

    result = requests.post("https://tracxn.com/api/2.2/companies", headers={'accessToken': tracxn_token}, json=request_body)

    if result.status_code != 200:
        raise ValueError("Error in API request or Company not found in Tracxn Database")
    else:
        return result.json()


def simplify_url(url: str) -> str:
    """
    Simplifies a given URL to its domain name.
    Removes 'www.' and any port numbers, and ensures the URL has a scheme.
    """

    parsed_url = urlparse(url, scheme='http')
    domain = parsed_url.netloc

    if domain.startswith('www.'):
        domain = domain[4:]

    domain = domain.split(':')[0]

    return domain



def add_data_to_table(data_dict: dict, table: Api.table, field_names: dict, check_for_url: bool = False):
    """
    Adds data to the specified table.
    If check_for_url is True, checks for the existence of the URL in the table before adding.
    Returns True if data is added, False otherwise.
    """
    if not check_for_url:
        table.create(data_dict)
        return True
    
    
    table_content = table.all()
    for row in table_content:
        if field_names["URL"] in row["field"] and row["fields"][field_names["URL"]] ==data_dict[field_names["URL"]]:
            logging.info(f"{row['fields'][field_names['URL']]} has already been fed to the table.")
            return False
    
    table.create(data_dict)
    return True



def extract_data(json_file, field_names):
    """
    Extracts data from a given JSON file based on specified field names.
    Returns a dictionary with the extracted data.
    """
    data_dict = dict()
    for company in json_file.get("result", []):
        for field, airtable_field in field_names.items():
            if airtable_field:
                try:
                    field_processor = {
                        "Name": lambda c: c.get('name', ''),
                        "Logo": lambda c: (utils.attachment(c['logos']['imageUrl']) if c['logos']['imageUrl'] else [],),
                        "Short Description": lambda c: c['description']['short'],
                        "Long Description": lambda c: c['description']['long'],
                        "Headquaters": lambda c: ", ".join([c['location']['city'], c['location']['country'], c['location']['continent']]),
                        "Founded Year": lambda c: str(c['foundedYear']) + "-01-01",
                        "Employee Count": lambda c: c['latestEmployeeCount']['value'],
                        "URL": lambda c: c.get('domain', '')
                    }
                    if field in field_processor:
                        data_dict[airtable_field] = field_processor[field](company)
                except Exception as e:
                    logging.error(f"Error processing field {field}: {e}")
                    data_dict[field_names[field]] = None
    return data_dict


def extract_keys(url: str) -> tuple:
    """
    Extracts base key and table key from an Airtable URL using regex.
    Returns a tuple (baseKey, tableKey). If no match is found, returns (None, None).
    """
    pattern = r'https://airtable.com/(app[\w\d]+)/([\w\d]+)/'
    match = re.search(pattern, url)

    if match:
        baseKey, tableKey = match.groups()
        return baseKey, tableKey
    else:
        return None, None



def main():
    """
    Main function of the application.
    
    This function orchestrates the process of reading the configuration,
    extracting keys from the Airtable URL, simplifying the company URL,
    interacting with the Airtable API, and adding data to the Airtable table.
    It handles the integration of different functional components and includes
    error handling for various stages of the process.
    
    Raises:
        Exception: If any error occurs during the process, including issues
        with loading the configuration file, extracting data, or interacting
        with APIs.
    """
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        baseKey, tableKey=  extract_keys(config['links']['airtable'])
        if baseKey is None or tableKey is None:
            raise ValueError("Invalid Airtable URL in the configuration.")

        company_url = simplify_url(config['links']['company'])
        field_names = config['fields']

        airtable_api = getAirtableAPI()
        airtable_table = getAirtableTable(baseKey, tableKey, airtable_api)
        tracxn_token = getTraxcnToken()

        data_to_add = extract_data(request_data(company_url, tracxn_token), field_names)
        add_data_to_table(data_to_add, airtable_table, field_names)

    except Exception as e:
        logging.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
   main()

