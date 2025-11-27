from django.db import models

class Company(models.Model):
    company_id = models.CharField(max_length=50, unique=True)  # e.g., TCS
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.company_id} - {self.name or ''}"


class MLResult(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="ml_results")
    created_at = models.DateTimeField(auto_now_add=True)
    analysis_json = models.JSONField()  # store the raw analysis and metrics
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)

    def __str__(self):
        return f"MLResult {self.company.company_id} @ {self.created_at}"
