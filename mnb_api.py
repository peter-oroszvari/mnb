from mnb import MNBClient
from flask import Flask, request

app = Flask(__name__)


@app.route('/exchange_rate', methods=['GET'])
def get_exchange_rate():

    # Make the request to the MNB web service
    mnb_client = MNBClient()
    result = mnb_client.get_exchange_rates()
    

    # Return the exchange rate as a JSON response
    return {'currency': currency, 'date': date, 'rate': rate}

if __name__ == '__main__':
    app.run()