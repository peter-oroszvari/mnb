"""
MNB Exchange Rate Fetcher

A modern Python script for fetching exchange rates from the Hungarian National Bank (MNB)
SOAP web service with support for multiple output formats and comprehensive error handling.
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

from lxml import etree
from zeep import Client
from zeep.exceptions import Fault, TransportError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ExchangeRate:
    """Represents a single exchange rate entry."""

    currency: str
    unit: int
    rate: float
    date: str

    def __str__(self) -> str:
        return f"{self.currency}\t{self.unit}\t{self.rate}"


@dataclass
class ExchangeRates:
    """Collection of exchange rates for a specific date."""

    date: str
    rates: List[ExchangeRate] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "date": self.date,
            "rates": [
                {"currency": r.currency, "unit": r.unit, "rate": r.rate}
                for r in self.rates
            ],
        }


class MNBClientError(Exception):
    """Custom exception for MNB client errors."""

    pass


class MNBClient:
    """Client for interacting with the MNB SOAP web service."""

    def __init__(self, wsdl_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the MNB client.

        Args:
            wsdl_url: The WSDL URL for the MNB service. Defaults to the official MNB endpoint.
            timeout: Request timeout in seconds.

        Raises:
            MNBClientError: If the client cannot be initialized.
        """
        self.wsdl_url = wsdl_url or "http://www.mnb.hu/arfolyamok.asmx?wsdl"
        self.timeout = timeout
        self._client: Optional[Client] = None

        try:
            logger.info(f"Initializing MNB client with WSDL: {self.wsdl_url}")
            self._client = Client(self.wsdl_url)
        except TransportError as e:
            logger.error(f"Transport error while initializing client: {e}")
            raise MNBClientError(f"Failed to connect to MNB service: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error while initializing client: {e}")
            raise MNBClientError(f"Failed to initialize MNB client: {e}") from e

    def get_current_exchange_rates(self) -> str:
        """
        Retrieve current MNB exchange rates.

        Returns:
            XML string containing the exchange rates.

        Raises:
            MNBClientError: If the request fails.
        """
        try:
            logger.info("Fetching current exchange rates")
            result = self._client.service.GetCurrentExchangeRates()
            logger.info("Successfully fetched current exchange rates")
            return result
        except Fault as e:
            logger.error(f"SOAP fault: {e}")
            raise MNBClientError(f"SOAP service error: {e}") from e
        except TransportError as e:
            logger.error(f"Transport error: {e}")
            raise MNBClientError(f"Network error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise MNBClientError(f"Failed to fetch exchange rates: {e}") from e

    def get_exchange_rates(
        self, start_date: str, end_date: str, currency_names: str
    ) -> str:
        """
        Retrieve exchange rates for a specific period and currency.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            currency_names: Currency code (e.g., 'USD', 'EUR').

        Returns:
            XML string containing the exchange rates.

        Raises:
            MNBClientError: If the request fails.
        """
        try:
            logger.info(
                f"Fetching exchange rates for {currency_names} from {start_date} to {end_date}"
            )
            result = self._client.service.GetExchangeRates(
                start_date, end_date, currency_names
            )
            logger.info("Successfully fetched historical exchange rates")
            return result
        except Fault as e:
            logger.error(f"SOAP fault: {e}")
            raise MNBClientError(f"SOAP service error: {e}") from e
        except TransportError as e:
            logger.error(f"Transport error: {e}")
            raise MNBClientError(f"Network error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise MNBClientError(f"Failed to fetch exchange rates: {e}") from e


class XMLParser:
    """Parser for MNB XML responses."""

    @staticmethod
    def parse_current_rates(xml_data: str) -> ExchangeRates:
        """
        Parse current exchange rates from XML response.

        Args:
            xml_data: XML string containing exchange rates.

        Returns:
            ExchangeRates object containing parsed data.

        Raises:
            MNBClientError: If parsing fails.
        """
        try:
            root = etree.fromstring(xml_data.encode("utf-8"))
            day_element = root.find("Day")

            if day_element is None:
                raise MNBClientError("No exchange rate data found in response")

            date_str = day_element.get("date")
            if not date_str:
                raise MNBClientError("Date not found in response")

            rates = []
            for rate_element in day_element.findall("Rate"):
                currency = rate_element.get("curr")
                unit = int(rate_element.get("unit", "1"))
                rate_value = float(rate_element.text.replace(",", "."))

                rates.append(
                    ExchangeRate(
                        currency=currency, unit=unit, rate=rate_value, date=date_str
                    )
                )

            logger.info(f"Parsed {len(rates)} exchange rates for {date_str}")
            return ExchangeRates(date=date_str, rates=rates)

        except etree.XMLSyntaxError as e:
            logger.error(f"XML parsing error: {e}")
            raise MNBClientError(f"Invalid XML response: {e}") from e
        except (ValueError, AttributeError) as e:
            logger.error(f"Data parsing error: {e}")
            raise MNBClientError(f"Failed to parse exchange rate data: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise MNBClientError(f"Failed to parse response: {e}") from e

    @staticmethod
    def parse_historical_rates(xml_data: str) -> Dict[str, str]:
        """
        Parse historical exchange rates from XML response.

        Args:
            xml_data: XML string containing historical exchange rates.

        Returns:
            Dictionary mapping date to exchange rate.

        Raises:
            MNBClientError: If parsing fails.
        """
        try:
            root = etree.fromstring(xml_data.encode("utf-8"))
            rates = {}

            for day in root.findall("Day"):
                date_str = day.get("date")
                rate_element = day.find("Rate")

                if rate_element is not None and date_str:
                    rates[date_str] = rate_element.text

            logger.info(f"Parsed {len(rates)} historical exchange rates")
            return rates

        except etree.XMLSyntaxError as e:
            logger.error(f"XML parsing error: {e}")
            raise MNBClientError(f"Invalid XML response: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise MNBClientError(f"Failed to parse response: {e}") from e


class OutputFormatter:
    """Handles different output formats for exchange rate data."""

    @staticmethod
    def format_table(exchange_rates: ExchangeRates) -> str:
        """Format exchange rates as a text table."""
        output = [f"Date: {exchange_rates.date}", "Currency\tUnit\tRate"]
        for rate in exchange_rates.rates:
            output.append(str(rate))
        return "\n".join(output)

    @staticmethod
    def format_json(exchange_rates: ExchangeRates) -> str:
        """Format exchange rates as JSON."""
        return json.dumps(exchange_rates.to_dict(), indent=2)

    @staticmethod
    def format_csv(exchange_rates: ExchangeRates) -> str:
        """Format exchange rates as CSV."""
        output = ["Date,Currency,Unit,Rate"]
        for rate in exchange_rates.rates:
            output.append(f"{exchange_rates.date},{rate.currency},{rate.unit},{rate.rate}")
        return "\n".join(output)

    @staticmethod
    def format_historical_table(rates: Dict[str, str]) -> str:
        """Format historical rates as a text table."""
        output = []
        for date_str, rate in rates.items():
            output.append(f"{date_str}: {rate}")
        return "\n".join(output)

    @staticmethod
    def format_historical_json(rates: Dict[str, str], currency: str) -> str:
        """Format historical rates as JSON."""
        data = {
            "currency": currency,
            "rates": [{"date": date_str, "rate": rate} for date_str, rate in rates.items()],
        }
        return json.dumps(data, indent=2)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Fetch exchange rates from the Hungarian National Bank (MNB)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch current exchange rates
  python mnb.py

  # Fetch current rates in JSON format
  python mnb.py --format json

  # Fetch historical USD rates
  python mnb.py --historical --currency USD --start 2024-01-01 --end 2024-12-31

  # Output to file
  python mnb.py --format json --output rates.json
        """,
    )

    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "--historical",
        action="store_true",
        help="Fetch historical exchange rates",
    )

    parser.add_argument(
        "--currency",
        "-c",
        type=str,
        default="USD",
        help="Currency code for historical rates (default: USD)",
    )

    parser.add_argument(
        "--start",
        type=str,
        help="Start date for historical rates (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--end",
        type=str,
        help="End date for historical rates (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--wsdl-url",
        type=str,
        help="Custom WSDL URL (default: http://www.mnb.hu/arfolyamok.asmx?wsdl)",
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_arguments()

    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("zeep").setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        logging.getLogger("zeep").setLevel(logging.WARNING)

    try:
        # Initialize client
        client = MNBClient(wsdl_url=args.wsdl_url)
        parser = XMLParser()
        formatter = OutputFormatter()

        output = ""

        if args.historical:
            # Fetch historical rates
            start_date = args.start or "2024-01-01"
            end_date = args.end or date.today().strftime("%Y-%m-%d")

            logger.info(f"Fetching historical rates for {args.currency}")
            xml_data = client.get_exchange_rates(start_date, end_date, args.currency)
            rates = parser.parse_historical_rates(xml_data)

            if args.format == "json":
                output = formatter.format_historical_json(rates, args.currency)
            else:
                output = formatter.format_historical_table(rates)

        else:
            # Fetch current rates
            logger.info("Fetching current exchange rates")
            xml_data = client.get_current_exchange_rates()
            exchange_rates = parser.parse_current_rates(xml_data)

            # Format output
            if args.format == "json":
                output = formatter.format_json(exchange_rates)
            elif args.format == "csv":
                output = formatter.format_csv(exchange_rates)
            else:
                output = formatter.format_table(exchange_rates)

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Output written to {args.output}")
        else:
            print(output)

        return 0

    except MNBClientError as e:
        logger.error(f"MNB Client Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
