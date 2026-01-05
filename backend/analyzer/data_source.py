import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class BluestockDataSource:
    """
    Fetch real financial + pros/cons data from Bluestock API.
    """
    def __init__(self):
        self.base_url = "https://bluemutualfund.in/server/api/company.php"
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY missing from .env file")

    def fetch_company_data(self, company_id: str) -> dict:
        company_id = company_id.upper()

        params = {
            "id": company_id,
            "api_key": self.api_key,
        }

        try:
            resp = requests.get(self.base_url, params=params, timeout=15)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as e:
            logger.error(f"API call failed for {company_id}: {e}")
            raise

        company = payload.get("company", {})
        data = payload.get("data", {})

        # Extract analysis rows and pick 10-year and 5-year summaries
        analysis_rows = data.get("analysis", []) or []
        ten_year = next(
            (row for row in analysis_rows if "10 Years" in (row.get("compounded_sales_growth") or "")), 
            None,
        )
        five_year = next(
            (row for row in analysis_rows if "5 Years" in (row.get("compounded_sales_growth") or "")), 
            None,
        )

        metrics_summary = {
            "sales_growth_10y": ten_year.get("compounded_sales_growth") if ten_year else None,
            "profit_growth_10y": ten_year.get("compounded_profit_growth") if ten_year else None,
            "roe_10y": ten_year.get("roe") if ten_year else None,
            "sales_growth_5y": five_year.get("compounded_sales_growth") if five_year else None,
        }

        # Pros & cons from API (may have multiple rows)
        pc_list = data.get("prosandcons", []) or []
        pros = []
        cons = []
        for row in pc_list:
            if row.get("pros") and row["pros"] != "NULL":
                pros.append(row["pros"])
            if row.get("cons") and row["cons"] != "NULL":
                cons.append(row["cons"])

        # Fallback if API returns none
        if not pros:
            pros.append("No strong positive indicators reported by API")
        if not cons:
            cons.append("No major red flags reported by API")

        # Simple numeric metrics (you can refine later)
        roe_percentage = company.get("roe_percentage")
        try:
            roe = float(roe_percentage) if roe_percentage is not None else 0.0
        except (TypeError, ValueError):
            roe = 0.0

        # TODO: extract more real metrics from API when you see the full response
        # e.g. debt/equity from company or data fields
        result = {
            "company_id": company_id,
            "company_name": company.get("company_name", company_id),
            "roe": roe,
            "debt_to_equity": 0.0,  # TODO: extract from real API
            "sales_growth": 0.0,    # TODO: extract from real API
            "median_sales_growth": 0.0,
            "dividend_paid": True,  # temporary assumption
            "api_pros": pros,
            "api_cons": cons,
            "details_url": f"https://bluemutualfund.in/app1/pages/company.php?id={company_id}",
            "metrics_summary": metrics_summary,
        }

        logger.info(f"Fetched {company_id}: ROE={roe}, pros={len(pros)}, cons={len(cons)}")
        return result

    def fetch_multiple(self, company_ids: list) -> dict:
        """
        Fetch multiple companies with error tolerance.
        """
        out = {}
        for cid in company_ids:
            try:
                out[cid] = self.fetch_company_data(cid)
            except Exception as e:
                logger.error(f"Failed {cid}: {e}")
                out[cid] = {
                    "company_id": cid,
                    "company_name": cid,
                    "roe": 0.0,
                    "debt_to_equity": 0.0,
                    "sales_growth": 0.0,
                    "median_sales_growth": 0.0,
                    "dividend_paid": False,
                    "api_pros": [],
                    "api_cons": [f"Error fetching data: {str(e)[:50]}..."],
                    "metrics_summary": {},
                    "details_url": f"https://bluemutualfund.in/app1/pages/company.php?id={cid}",
                }
        return out
