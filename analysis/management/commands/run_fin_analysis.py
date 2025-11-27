# from django.core.management.base import BaseCommand
# from analysis.models import Company, MLResult
# from analysis.utils import fetch_company_data, generate_pros_cons
# import pandas as pd
# import os

# class Command(BaseCommand):
#     help = "Fetch financial data & run analysis"

#     def add_arguments(self, parser):
#         parser.add_argument("--excel", type=str, required=True)

#     def handle(self, *args, **options):
#         excel_path = options["excel"]

#         df = pd.read_excel(excel_path)
#         col = df.columns[0]   # first column must be Company IDs

#         for _, row in df.iterrows():
#             company_id = str(row[col]).strip()
#             self.stdout.write(f"Processing {company_id}...")

#             data = fetch_company_data(company_id)
#             pros, cons = generate_pros_cons(data)

#             company, _ = Company.objects.get_or_create(company_id=company_id)

#             MLResult.objects.create(
#                 company=company,
#                 analysis_json=data,
#                 pros=pros,
#                 cons=cons
#             )

#             self.stdout.write(self.style.SUCCESS(f"Done: {company_id}"))



















# analysis/management/commands/run_fin_analysis.py
import os
from django.core.management.base import BaseCommand
from analysis.utils import fetch_company_data, generate_pros_cons
from analysis.models import Company, MLResult
import pandas as pd

class Command(BaseCommand):
    help = "Fetch companies from Excel and run ML financial analysis"

    def add_arguments(self, parser):
        parser.add_argument("--excel", type=str, default=os.getenv("COMPANY_EXCEL_PATH"))

    def handle(self, *args, **options):
        excel_path = options["excel"]
        if not excel_path or not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f"Excel file not found at {excel_path}"))
            return

        df = pd.read_excel(excel_path)
        # Assuming the excel has a column "CompanyID" or "id" with values like TCS
        if "CompanyID" in df.columns:
            id_col = "CompanyID"
        elif "id" in df.columns:
            id_col = "id"
        elif "company_id" in df.columns:
            id_col = "company_id"
        else:
            # fallback to first column
            id_col = df.columns[0]

        for idx, row in df.iterrows():
            company_id = str(row[id_col]).strip()
            if not company_id:
                continue
            try:
                self.stdout.write(f"Processing {company_id} ...")
                data = fetch_company_data(company_id)
                analysis = generate_pros_cons(data)
                # Create or get company
                company_obj, _ = Company.objects.get_or_create(company_id=company_id, defaults={"name": row.get("Name") if "Name" in row else None})
                # Save MLResult
                ml = MLResult.objects.create(company=company_obj, analysis_json=data, pros=analysis["pros"], cons=analysis["cons"])
                self.stdout.write(self.style.SUCCESS(f"Saved analysis for {company_id} with {len(analysis['pros'])} pros and {len(analysis['cons'])} cons."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {company_id}: {e}"))

