# TracxnAirtableSync
## Description

TracxnAirtableSync is a Python-based tool designed to import company profiles from Tracxn into an Airtable base. It streamlines the process of syncing Tracxn's comprehensive company data with your custom Airtable tables. The program is configurable, allowing users to specify how data fields from Tracxn correspond to fields in Airtable. It's ideal for professionals in market research, business analysis, and data management fields.


## Features

- Data Import: Easily import available company data from Tracxn using the company's URL.
- Duplicate Prevention: The program checks for existing entries to prevent duplicate imports.
- Configurable Mapping: Utilize a config.json file for custom field mapping between Tracxn data and Airtable fields.


## Requirements

- Python 3.x
- Access to Tracxn API and an Airtable base.
- A config.json file specifying field mappings and links.
- Tracxn and Airtable API tokens stored as environment variables (API_KEY_TRACXN and API_KEY_AIRTABLE, respectively).

## Installation

Clone the repository to your local machine:#

    git clone https://github.com/yourusername/TracxnAirtableSync.git
    cd TracxnAirtableSync

Install the required dependencies:

    pip install -r requirements.txt

## Usage

Ensure your config.json file is set up according to your field and link specifications.
Store your API tokens for Tracxn and Airtable in your environment variables.
Run the script with:

    python main.py

## Configuration
### config.json Structure

fields: Define the mapping of Tracxn fields to your Airtable base fields.

links: Provide the Airtable base/table link and the company's URL.

Example:

    {
        "fields": {
            "Name": "Name",
            "Logo": "Logo",
            ...
        },
        "links": {
            "airtable": "YOUR_AIRTABLE_LINK",
            "company": "COMPANY_URL"
        }
    }

## Future Enhancements

Support for additional import methods.
Integration of more data fields, such as categories.

