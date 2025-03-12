# agents/stock_lookup_agent.py
from ..agent_registry import MCPAgent, register_agent
import json


@register_agent
class StockLookupAgent(MCPAgent):
    agent_name = "stock_lookup"
    agent_description = "Quickly look up current stock prices and basic info"
    agent_version = "1.0"
    agent_author = "Your Name"

    def run(self, params):
        """Look up stock information"""
        if "ticker" not in params:
            return {"error": "Ticker symbol required"}

        ticker = params["ticker"].upper()

        try:
            # Get basic info
            info_result = self.toolkit.yfinance_get_ticker_info(ticker)
            info = json.loads(info_result)

            # Get latest price data
            price_result = self.toolkit.yfinance_get_historical_data(
                ticker, period="1d")
            price_data = json.loads(price_result)

            if "data" in price_data and price_data["data"]:
                latest = price_data["data"][-1]
                current_price = latest.get("Close", "N/A")
            else:
                current_price = "N/A"

            # Get company name from info
            company_name = info.get("info", {}).get("longName", ticker)

            return {
                "success": True,
                "ticker": ticker,
                "company_name": company_name,
                "current_price": current_price,
                "currency": info.get("info", {}).get("currency", "USD")
            }
        except Exception as e:
            return {"error": f"Error looking up {ticker}: {str(e)}"}
