"""
Unit tests for MNB Exchange Rate Fetcher
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from lxml import etree

from mnb import (
    MNBClient,
    MNBClientError,
    XMLParser,
    ExchangeRate,
    ExchangeRates,
    OutputFormatter,
)


# Sample XML responses for testing
SAMPLE_CURRENT_RATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<MNBCurrentExchangeRates>
    <Day date="2025-11-04">
        <Rate unit="1" curr="USD">337.68</Rate>
        <Rate unit="1" curr="EUR">388.37</Rate>
        <Rate unit="100" curr="JPY">220.00</Rate>
    </Day>
</MNBCurrentExchangeRates>"""

SAMPLE_HISTORICAL_RATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<MNBExchangeRates>
    <Day date="2025-11-04">
        <Rate unit="1" curr="USD">337,68000</Rate>
    </Day>
    <Day date="2025-11-03">
        <Rate unit="1" curr="USD">336,50000</Rate>
    </Day>
</MNBExchangeRates>"""


class TestExchangeRate:
    """Test ExchangeRate dataclass."""

    def test_exchange_rate_creation(self):
        """Test creating an ExchangeRate instance."""
        rate = ExchangeRate(currency="USD", unit=1, rate=337.68, date="2025-11-04")
        assert rate.currency == "USD"
        assert rate.unit == 1
        assert rate.rate == 337.68
        assert rate.date == "2025-11-04"

    def test_exchange_rate_str(self):
        """Test string representation of ExchangeRate."""
        rate = ExchangeRate(currency="USD", unit=1, rate=337.68, date="2025-11-04")
        assert str(rate) == "USD\t1\t337.68"


class TestExchangeRates:
    """Test ExchangeRates dataclass."""

    def test_exchange_rates_creation(self):
        """Test creating an ExchangeRates instance."""
        rates = [
            ExchangeRate(currency="USD", unit=1, rate=337.68, date="2025-11-04"),
            ExchangeRate(currency="EUR", unit=1, rate=388.37, date="2025-11-04"),
        ]
        exchange_rates = ExchangeRates(date="2025-11-04", rates=rates)
        assert exchange_rates.date == "2025-11-04"
        assert len(exchange_rates.rates) == 2

    def test_exchange_rates_to_dict(self):
        """Test converting ExchangeRates to dictionary."""
        rates = [
            ExchangeRate(currency="USD", unit=1, rate=337.68, date="2025-11-04"),
        ]
        exchange_rates = ExchangeRates(date="2025-11-04", rates=rates)
        result = exchange_rates.to_dict()
        assert result["date"] == "2025-11-04"
        assert len(result["rates"]) == 1
        assert result["rates"][0]["currency"] == "USD"
        assert result["rates"][0]["rate"] == 337.68


class TestXMLParser:
    """Test XMLParser class."""

    def test_parse_current_rates_success(self):
        """Test parsing current exchange rates from XML."""
        parser = XMLParser()
        result = parser.parse_current_rates(SAMPLE_CURRENT_RATES_XML)

        assert result.date == "2025-11-04"
        assert len(result.rates) == 3
        assert result.rates[0].currency == "USD"
        assert result.rates[0].rate == 337.68
        assert result.rates[1].currency == "EUR"
        assert result.rates[2].unit == 100

    def test_parse_current_rates_no_day_element(self):
        """Test parsing XML without Day element."""
        parser = XMLParser()
        invalid_xml = '<?xml version="1.0"?><MNBCurrentExchangeRates></MNBCurrentExchangeRates>'

        with pytest.raises(MNBClientError, match="No exchange rate data found"):
            parser.parse_current_rates(invalid_xml)

    def test_parse_current_rates_invalid_xml(self):
        """Test parsing invalid XML."""
        parser = XMLParser()
        invalid_xml = "not valid xml"

        with pytest.raises(MNBClientError, match="Invalid XML response"):
            parser.parse_current_rates(invalid_xml)

    def test_parse_historical_rates_success(self):
        """Test parsing historical exchange rates from XML."""
        parser = XMLParser()
        result = parser.parse_historical_rates(SAMPLE_HISTORICAL_RATES_XML)

        assert len(result) == 2
        assert "2025-11-04" in result
        assert "2025-11-03" in result
        assert result["2025-11-04"] == "337,68000"
        assert result["2025-11-03"] == "336,50000"

    def test_parse_historical_rates_invalid_xml(self):
        """Test parsing invalid historical XML."""
        parser = XMLParser()
        invalid_xml = "not valid xml"

        with pytest.raises(MNBClientError, match="Invalid XML response"):
            parser.parse_historical_rates(invalid_xml)


class TestOutputFormatter:
    """Test OutputFormatter class."""

    def setup_method(self):
        """Set up test data."""
        self.rates = [
            ExchangeRate(currency="USD", unit=1, rate=337.68, date="2025-11-04"),
            ExchangeRate(currency="EUR", unit=1, rate=388.37, date="2025-11-04"),
        ]
        self.exchange_rates = ExchangeRates(date="2025-11-04", rates=self.rates)

    def test_format_table(self):
        """Test table formatting."""
        formatter = OutputFormatter()
        result = formatter.format_table(self.exchange_rates)

        assert "Date: 2025-11-04" in result
        assert "Currency\tUnit\tRate" in result
        assert "USD\t1\t337.68" in result
        assert "EUR\t1\t388.37" in result

    def test_format_json(self):
        """Test JSON formatting."""
        formatter = OutputFormatter()
        result = formatter.format_json(self.exchange_rates)

        assert '"date": "2025-11-04"' in result
        assert '"currency": "USD"' in result
        assert '"rate": 337.68' in result

    def test_format_csv(self):
        """Test CSV formatting."""
        formatter = OutputFormatter()
        result = formatter.format_csv(self.exchange_rates)

        assert "Date,Currency,Unit,Rate" in result
        assert "2025-11-04,USD,1,337.68" in result
        assert "2025-11-04,EUR,1,388.37" in result

    def test_format_historical_table(self):
        """Test historical table formatting."""
        formatter = OutputFormatter()
        historical_rates = {"2025-11-04": "337,68", "2025-11-03": "336,50"}
        result = formatter.format_historical_table(historical_rates)

        assert "2025-11-04: 337,68" in result
        assert "2025-11-03: 336,50" in result

    def test_format_historical_json(self):
        """Test historical JSON formatting."""
        formatter = OutputFormatter()
        historical_rates = {"2025-11-04": "337,68", "2025-11-03": "336,50"}
        result = formatter.format_historical_json(historical_rates, "USD")

        assert '"currency": "USD"' in result
        assert '"date": "2025-11-04"' in result
        assert '"rate": "337,68"' in result


class TestMNBClient:
    """Test MNBClient class."""

    @patch("mnb.Client")
    def test_client_initialization_success(self, mock_client):
        """Test successful client initialization."""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        client = MNBClient()

        assert client.wsdl_url == "http://www.mnb.hu/arfolyamok.asmx?wsdl"
        assert client._client == mock_client_instance
        mock_client.assert_called_once_with("http://www.mnb.hu/arfolyamok.asmx?wsdl")

    @patch("mnb.Client")
    def test_client_initialization_custom_url(self, mock_client):
        """Test client initialization with custom URL."""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        custom_url = "http://custom.url/test.asmx?wsdl"

        client = MNBClient(wsdl_url=custom_url)

        assert client.wsdl_url == custom_url
        mock_client.assert_called_once_with(custom_url)

    @patch("mnb.Client")
    def test_get_current_exchange_rates_success(self, mock_client):
        """Test successful retrieval of current exchange rates."""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.service.GetCurrentExchangeRates.return_value = (
            SAMPLE_CURRENT_RATES_XML
        )

        client = MNBClient()
        result = client.get_current_exchange_rates()

        assert result == SAMPLE_CURRENT_RATES_XML
        mock_client_instance.service.GetCurrentExchangeRates.assert_called_once()

    @patch("mnb.Client")
    def test_get_exchange_rates_success(self, mock_client):
        """Test successful retrieval of historical exchange rates."""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.service.GetExchangeRates.return_value = (
            SAMPLE_HISTORICAL_RATES_XML
        )

        client = MNBClient()
        result = client.get_exchange_rates("2025-11-01", "2025-11-04", "USD")

        assert result == SAMPLE_HISTORICAL_RATES_XML
        mock_client_instance.service.GetExchangeRates.assert_called_once_with(
            "2025-11-01", "2025-11-04", "USD"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
