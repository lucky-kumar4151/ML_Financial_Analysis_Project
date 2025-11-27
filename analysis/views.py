# analysis/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Company, MLResult
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
from django.conf import settings

def home(request):
    companies = Company.objects.all().order_by("company_id")
    return render(request, "company_list.html", {"companies": companies})

def company_detail(request, company_id):
    company = get_object_or_404(Company, company_id=company_id)
    latest = company.ml_results.order_by("-created_at").first()
    return render(request, "company_detail.html", {"company": company, "latest": latest})

def view_all(request):
    companies = Company.objects.all().order_by("company_id")
    return render(request, "view_all.html", {"companies": companies})

# Simple endpoint to trigger management command via HTTP (not recommended for production).
# It's included for convenience. It will run synchronously (blocking) — for large runs use manage.py on terminal.
@csrf_exempt
def run_analysis_now(request):
    # Warning: this blocks until the command finishes.
    # For Windows environment, run python manage.py run_fin_analysis
    # We'll call subprocess to run it
    try:
        cmd = [os.path.join(os.getcwd(), "venv", "Scripts", "python.exe"), os.path.join(os.getcwd(), "manage.py"), "run_fin_analysis"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output = []
        for line in proc.stdout:
            output.append(line)
        proc.wait()
        return JsonResponse({"status": "done", "output": output})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
