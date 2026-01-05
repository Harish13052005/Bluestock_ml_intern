from .data_source import BluestockDataSource
from .ml_analyzer import FinancialAnalyzer

analyzer = FinancialAnalyzer()
data_source = BluestockDataSource()

from django.http import HttpResponse
def home(request):
  return HttpResponse(
      "<h1>Bluestock ML Backend</h1><p>Use /api/analyze/ and /api/results/ for data.</p>"
  )


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from .models import Company, Analysis

# Use the real Bluestock data source and a single FinancialAnalyzer instance
# (prevent duplicate imports/instances that caused ImportError during tests)
analyzer = FinancialAnalyzer()
data_source = BluestockDataSource()


@csrf_exempt
@api_view(['POST'])
def analyze_companies(request):
    """
    Body example:
    {
        "company_ids": ["TCS", "HDFCBANK", "INFY"]
    }
    """
    company_ids = request.data.get('company_ids')

    if not company_ids or not isinstance(company_ids, list):
        return Response(
            {"error": "Provide 'company_ids' as a list, e.g. ['TCS', 'INFY']"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 1. Fetch data (currently dummy)
    raw_data = data_source.fetch_multiple(company_ids)

    results = []

    for company_id, metrics in raw_data.items():
        # 1) Run your rule-based analyzer
        analysis_result = analyzer.analyze_company(metrics)

        # 2) Merge API pros/cons with ML pros/cons
        api_pros = metrics.get("api_pros", [])
        api_cons = metrics.get("api_cons", [])

        combined_pros = api_pros + analysis_result["pros"]
        combined_cons = api_cons + analysis_result["cons"]

        # grab metrics summary (populated by BluestockDataSource)
        metrics_summary = metrics.get("metrics_summary", {})

        # 3) Save Company
        company, _ = Company.objects.update_or_create(
            company_id=metrics["company_id"],
            defaults={
                "company_name": metrics["company_name"],
                "roe": metrics["roe"],
                "sales_growth": metrics.get("sales_growth"),
                "median_sales_growth": metrics.get("median_sales_growth"),
                "debt_to_equity": metrics.get("debt_to_equity"),
                "dividend_paid": metrics.get("dividend_paid", True),
            },
        )

        # 4) Save Analysis
        Analysis.objects.update_or_create(
            company=company,
            defaults={
                "health_rating": analysis_result["health_rating"],
                "pros": ", ".join(combined_pros),
                "cons": ", ".join(combined_cons),
            },
        )

        results.append({
            "company_id": company.company_id,
            "company_name": company.company_name,
            "health_rating": analysis_result["health_rating"],
            "pros": combined_pros,
            "cons": combined_cons,
            "metrics_summary": metrics_summary,
            "details_url": metrics.get("details_url"),
        })

    return Response(
        {
            "status": "success",
            "count": len(results),
            "results": results,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
def list_analyses(request):
    """
    Returns all stored analyses.
    """
    data = []
    for analysis in Analysis.objects.select_related('company'):
        data.append({
            "company_id": analysis.company.company_id,
            "company_name": analysis.company.company_name,
            "health_rating": analysis.health_rating,
            "pros": analysis.pros.split(", ") if analysis.pros else [],
            "cons": analysis.cons.split(", ") if analysis.cons else [],
            "analysis_date": analysis.analysis_date,
        })

    return Response({"status": "success", "results": data})
