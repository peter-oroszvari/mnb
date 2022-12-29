from mnb import MNBClient, XMLParser
from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/exchange_rate', methods=['GET'])
def get_exchange_rate():

    # Make the request to the MNB web service
    mnb_client = MNBClient()
    xml_parser = XMLParser()
    result = mnb_client.get_exchange_rates()
    currencies = xml_parser.process_xml(result)
    # Return the exchange rate as a JSON response
    return json.dumps(currencies)

if __name__ == '__main__':
    app.run()