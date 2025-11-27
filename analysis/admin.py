# analysis/admin.py
from django.contrib import admin
from .models import Company, MLResult

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_id", "name")

@admin.register(MLResult)
class MLResultAdmin(admin.ModelAdmin):
    list_display = ("company", "created_at")
    readonly_fields = ("created_at",)
