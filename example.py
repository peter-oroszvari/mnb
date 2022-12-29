from mnb import MNBClient, XMLParser

# Create a client for interacting with the MNB web service
mnb_client = MNBClient()

# Get the exchange rates of the actual day, transform the XML and print the result
result = mnb_client.get_exchange_rates()
xml_parser = XMLParser()
print(xml_parser.process_xml(result))

# Get the exchange rates in a given period for a given currency and print the result
result = mnb_client.get_currencies("2022-01-01", "2022-12-28", "USD")
rates = xml_parser.parse_rates(result)

for date, rate in rates.items():
    print(f"{date}: {rate}")