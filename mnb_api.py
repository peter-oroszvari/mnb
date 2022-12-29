from mnb import MNBClient, XMLParser
from flask import Flask, request
from flask_restful import Resource, Api, abort
import json

app = Flask(__name__)
api = Api(app)

class ExchangeRateResource(Resource):
    def get(self):
        # Make the request to the MNB web service
        mnb_client = MNBClient()
        xml_parser = XMLParser()
        result = mnb_client.get_exchange_rates()
        if result is None:
            # Return a 404 error if the result is None
            abort(404, message="Exchange rates not found")
        currencies = xml_parser.process_xml(result)
        # Return the exchange rate as a JSON response
        return {'MBN Exchange Rates': currencies}, 200


api.add_resource(ExchangeRateResource, '/exchange_rate')

@app.errorhandler(404)
def handle_404_error(error):
    return {'error': 'Not found'}, 404

if __name__ == '__main__':
    app.run()