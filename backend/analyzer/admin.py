from django.contrib import admin
from .models import Company, Analysis

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'company_name', 'roe', 'sales_growth', 'median_sales_growth')
    search_fields = ('company_id', 'company_name')

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('company', 'health_rating', 'analysis_date')
    list_filter = ('health_rating',)
