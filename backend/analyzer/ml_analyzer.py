class FinancialAnalyzer:
    """
    Simple rule-based analyzer that mimics ML-style scoring.
    You can later replace rules with a trained ML model.
    """

    def __init__(self):
        # Thresholds – you can tune later
        self.good_roe = 10.0
        self.good_median_sales_growth = 20.0
        self.low_debt = 10.0
        self.bad_sales_growth = 5.5

    def analyze_company(self, metrics: dict) -> dict:
        pros = []
        cons = []

        debt_to_equity = metrics.get('debt_to_equity') or 0
        roe = metrics.get('roe') or 0
        sales_growth = metrics.get('sales_growth') or 0
        median_sales_growth = metrics.get('median_sales_growth') or 0
        dividend_paid = bool(metrics.get('dividend_paid'))

        # PROS
        if debt_to_equity < self.low_debt:
            pros.append("Company is almost debt-free")

        if roe > self.good_roe:
            pros.append("Company has a good return on equity (ROE)")

        if dividend_paid:
            pros.append("Company has a healthy dividend payment track record")

        if median_sales_growth > self.good_median_sales_growth:
            pros.append("Company has strong median sales growth over past years")

        # CONS
        if sales_growth < self.bad_sales_growth:
            cons.append("Company has delivered poor sales growth in the past year")

        if not dividend_paid:
            cons.append("Company is not paying regular dividends")

        if roe < 5:
            cons.append("Company has delivered poor return on equity in recent years")

        if debt_to_equity > 50:
            cons.append("Company has a high debt burden")

        # HEALTH RATING
        if len(pros) >= 3 and len(cons) <= 1:
            health_rating = 'GOOD'
        elif len(cons) >= 3 and len(pros) <= 1:
            health_rating = 'BAD'
        else:
            health_rating = 'NEUTRAL'

        return {
            'pros': pros,
            'cons': cons,
            'health_rating': health_rating,
        }
