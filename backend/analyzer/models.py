from django.db import models

from django.db import models

class Company(models.Model):
    company_id = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=200)
    debt_to_equity = models.FloatField(null=True, blank=True)
    roe = models.FloatField(null=True, blank=True)  # Return on Equity
    sales_growth = models.FloatField(null=True, blank=True)
    median_sales_growth = models.FloatField(null=True, blank=True)
    dividend_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_name} ({self.company_id})"


class Analysis(models.Model):
    HEALTH_CHOICES = [
        ('GOOD', 'Good Financial Health'),
        ('BAD', 'Poor Financial Health'),
        ('NEUTRAL', 'Neutral'),
    ]

    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    health_rating = models.CharField(max_length=10, choices=HEALTH_CHOICES)
    pros = models.TextField(help_text="Comma-separated pros")
    cons = models.TextField(help_text="Comma-separated cons")
    analysis_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.company_name} - {self.health_rating}"
