# MNB Exchange Rate Fetcher

A modern Python application for fetching exchange rates from the Hungarian National Bank (MNB) SOAP web service with support for multiple output formats, comprehensive error handling, and a flexible CLI interface.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- 🚀 **Modern Python**: Uses type hints, dataclasses, and async-ready architecture
- 📊 **Multiple Output Formats**: Support for table, JSON, and CSV formats
- 🎯 **Flexible CLI**: Comprehensive command-line interface with argparse
- 🔍 **Error Handling**: Robust error handling with custom exceptions and detailed logging
- ✅ **Well Tested**: Comprehensive unit tests with pytest
- 📝 **Well Documented**: Full docstrings and type annotations
- 🔄 **Both Current and Historical**: Fetch current rates or historical data for any period

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Development Installation

For development work with testing and code quality tools:

```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage

Fetch current exchange rates in table format:

```bash
python mnb.py
```

Output:
```
Date: 2025-11-04
Currency	Unit	Rate
AUD	1	219.32
BGN	1	198.57
BRL	1	63.03
...
```

### Output Formats

#### JSON Format

```bash
python mnb.py --format json
```

Output:
```json
{
  "date": "2025-11-04",
  "rates": [
    {
      "currency": "AUD",
      "unit": 1,
      "rate": 219.32
    },
    ...
  ]
}
```

#### CSV Format

```bash
python mnb.py --format csv
```

Output:
```csv
Date,Currency,Unit,Rate
2025-11-04,AUD,1,219.32
2025-11-04,BGN,1,198.57
...
```

### Historical Exchange Rates

Fetch historical rates for a specific currency and date range:

```bash
python mnb.py --historical --currency USD --start 2024-01-01 --end 2024-12-31
```

Fetch EUR rates for the last month in JSON format:

```bash
python mnb.py --historical --currency EUR --start 2024-10-01 --end 2024-11-04 --format json
```

### Save to File

Output to a file instead of stdout:

```bash
python mnb.py --format json --output rates.json
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
python mnb.py --verbose
```

### Custom WSDL URL

Use a custom WSDL endpoint (useful for testing):

```bash
python mnb.py --wsdl-url "http://custom.url/arfolyamok.asmx?wsdl"
```

## Command-Line Options

```
usage: mnb.py [-h] [--format {table,json,csv}] [--output OUTPUT] [--historical]
              [--currency CURRENCY] [--start START] [--end END] [--verbose]
              [--wsdl-url WSDL_URL]

Fetch exchange rates from the Hungarian National Bank (MNB)

options:
  -h, --help            show this help message and exit
  --format {table,json,csv}
                        Output format (default: table)
  --output OUTPUT, -o OUTPUT
                        Output file path (default: stdout)
  --historical          Fetch historical exchange rates
  --currency CURRENCY, -c CURRENCY
                        Currency code for historical rates (default: USD)
  --start START         Start date for historical rates (YYYY-MM-DD)
  --end END             End date for historical rates (YYYY-MM-DD)
  --verbose, -v         Enable verbose logging
  --wsdl-url WSDL_URL   Custom WSDL URL (default: http://www.mnb.hu/arfolyamok.asmx?wsdl)
```

## Usage as a Python Library

You can also use the code as a library in your Python projects:

```python
from mnb import MNBClient, XMLParser

# Initialize client
client = MNBClient()
parser = XMLParser()

# Fetch current rates
xml_data = client.get_current_exchange_rates()
exchange_rates = parser.parse_current_rates(xml_data)

# Access the data
print(f"Date: {exchange_rates.date}")
for rate in exchange_rates.rates:
    print(f"{rate.currency}: {rate.rate}")

# Fetch historical rates
xml_data = client.get_exchange_rates("2024-01-01", "2024-12-31", "USD")
historical_rates = parser.parse_historical_rates(xml_data)
```

## Development

### Running Tests

Run the test suite with pytest:

```bash
python -m pytest test_mnb.py -v
```

Run tests with coverage:

```bash
python -m pytest test_mnb.py --cov=mnb --cov-report=html
```

### Code Quality

Format code with black:

```bash
black mnb.py test_mnb.py
```

Type checking with mypy:

```bash
mypy mnb.py
```

Linting with ruff:

```bash
ruff check mnb.py
```

## Architecture

The application is structured with clean separation of concerns:

- **MNBClient**: Handles SOAP web service communication
- **XMLParser**: Parses XML responses into Python objects
- **OutputFormatter**: Formats data for different output formats
- **ExchangeRate/ExchangeRates**: Dataclasses for type-safe data handling
- **MNBClientError**: Custom exception for error handling

## Error Handling

The application includes comprehensive error handling:

- Network errors (connection failures, timeouts)
- SOAP service errors
- XML parsing errors
- Invalid data formats
- Custom `MNBClientError` exception for all MNB-specific errors

## Logging

The application uses Python's standard logging module:

- INFO level: Normal operations
- ERROR level: Errors and exceptions
- DEBUG level: Detailed debugging info (use `--verbose` flag)

## Supported Currencies

The MNB service provides exchange rates for 33+ currencies including:

- Major currencies: USD, EUR, GBP, JPY, CHF, CAD, AUD
- European currencies: BGN, CZK, DKK, HRK, NOK, PLN, RON, RSD, SEK
- Asian currencies: CNY, HKD, IDR, INR, ISK, KRW, MYR, PHP, SGD, THB
- Others: BRL, ILS, MXN, NZD, RUB, TRY, UAH, ZAR

## API Reference

For detailed API documentation, see the docstrings in the source code. All classes and methods are fully documented with type hints.

## References

- [MNB Official Documentation](https://www.mnb.hu/letoltes/aktualis-es-a-regebbi-arfolyamok-webszolgaltatasanak-dokumentacioja-1.pdf) (Hungarian)
- [python-zeep Documentation](https://docs.python-zeep.org/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 2.0.0 (Modernization Update)

- ✨ Added type hints throughout the codebase
- ✨ Added comprehensive error handling and logging
- ✨ Refactored code with better separation of concerns
- ✨ Added CLI argument parsing with argparse
- ✨ Added multiple output formats (JSON, CSV, table)
- ✨ Added docstrings and improved documentation
- ✨ Added unit tests with pytest (18 tests)
- ✨ Updated dependencies to latest versions (zeep 4.3.2)
- ✨ Added dataclasses for type-safe data handling
- ✨ Made script importable as a library
- 🔧 Improved XML parsing with better error handling
- 📝 Completely rewritten README with modern examples

### Version 1.0.0 (Original)

- Initial proof-of-concept implementation
- Basic SOAP service communication
- Simple XML parsing
- Console output only

## Acknowledgments

This script uses the official MNB (Magyar Nemzeti Bank) SOAP web service for exchange rate data.
