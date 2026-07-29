import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 1. إنشاء الـ Workbook وتحديد الشيتات
wb = openpyxl.Workbook()
wb.remove(wb.active)  # حذف الشيت الافتراضي

# ألوان التنسيق الاحترافي
header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid") # كحلي داكن
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
data_font = Font(name="Calibri", size=10)
bold_font = Font(name="Calibri", size=10, bold=True)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
right_align = Alignment(horizontal="right", vertical="center")

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

# ----------------------------------------------------
# Sheet 1: Target Hospitals & Dialysis Centers
# ----------------------------------------------------
ws1 = wb.create_sheet(title="Hospitals_And_Centers")
headers1 = [
    "Region", "Country", "Facility Name", "Sector", 
    "Estimated Bed Count", "Dialysis Capabilities", 
    "Target AMECATH Portfolio", "Account Tier"
]
ws1.append(headers1)

hospitals_data = [
    ["GCC", "Saudi Arabia", "King Faisal Specialist Hospital & Research Centre", "Government", 1200, "HD / PD / Transplant", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "Saudi Arabia", "King Salman Center for Kidney Diseases", "Government", 78, "HD Dedicated", "HD Acute & Permcath", "Tier 1 Major"],
    ["GCC", "Saudi Arabia", "King Fahad Medical City", "Government", 1300, "HD / PD / ICU", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "UAE", "Sheikh Shakhbout Medical City (SSMC)", "Government", 741, "HD / PD / ICU", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "UAE", "Cleveland Clinic Abu Dhabi", "Private/Gov", 364, "HD / PD / Transplant", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "Qatar", "Hamad General Hospital - Nephrology Dept", "Government", 600, "HD / PD", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "Kuwait", "Amiri Hospital - Dialysis Center", "Government", 400, "HD / PD", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "Oman", "Royal Hospital Muscat - Nephrology", "Government", 630, "HD / PD", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["GCC", "Bahrain", "Salmaniya Medical Complex", "Government", 1200, "HD / PD", "HD Acute & Permcath / PD Catheters", "Tier 1 Major"],
    ["Southern Africa", "South Africa", "Groote Schuur Hospital - Renal Unit", "Government", 975, "HD / PD / Transplant", "HD Acute & Permcath", "Tier 1 Major"],
    ["Southern Africa", "South Africa", "Netcare Jakaranda Hospital - Dialysis", "Private", 200, "HD Dedicated", "HD Acute & Permcath", "Tier 2 Regional"],
    ["East Africa", "Kenya", "Kenyatta National Hospital - Renal Unit", "Government", 1800, "HD / Acute Care", "HD Acute & Permcath", "Tier 1 Major"],
    ["West Africa", "Nigeria", "Lagos University Teaching Hospital (LUTH)", "Government", 760, "HD Dedicated", "HD Acute & Permcath", "Tier 1 Major"],
    ["West Africa", "Ghana", "Korle Bu Teaching Hospital - Dialysis", "Government", 2000, "HD Dedicated", "HD Acute & Permcath", "Tier 1 Major"],
    ["East Africa", "Tanzania", "Muhimbili National Hospital", "Government", 1500, "HD Dedicated", "HD Acute & Permcath", "Tier 1 Major"],
    ["East Africa", "Sudan", "Ibn Sina Hospital - Kidney Care ( Khartoum/Red Sea )", "Government", 300, "HD Dedicated", "HD Acute & Permcath", "Tier 1 Major"],
    ["North Africa", "Morocco", "CHU Ibn Rochd Casablanca - Nephrologie", "Government", 1000, "HD / PD", "HD Acute & Permcath", "Tier 1 Major"]
]

for row in hospitals_data:
    ws1.append(row)

# ----------------------------------------------------
# Sheet 2: Distributors Pipeline
# ----------------------------------------------------
ws2 = wb.create_sheet(title="Distributors_Pipeline")
headers2 = [
    "Country", "Distributor Name", "Specialty Focus", 
    "Market Coverage", "Tendering Capability", "Pipeline Status"
]
ws2.append(headers2)

distributors_data = [
    ["Saudi Arabia", "Attieh Medico", "Dialysis & ICU Consumables", "National", "Yes", "Target Partner"],
    ["Saudi Arabia", "Al-Ewan Medical Company", "Nephrology & Urology", "National", "Yes", "Target Partner"],
    ["UAE", "Zahrawi Group", "Dialysis, Vascular & ICU", "Regional (GCC)", "Yes", "Target Partner"],
    ["Qatar", "Intercol / Local Partner", "Medical Devices", "National", "Yes", "Prospect"],
    ["Kuwait", "Bader Sultan & Bros", "Medical Equipment & Renal", "National", "Yes", "Target Partner"],
    ["Oman", "Muscat Pharmacy - Medical Div", "Pharma & Devices", "National", "Yes", "Prospect"],
    ["Bahrain", "Y.K. Almoayyed Medical", "Hospital Consumables", "National", "Yes", "Prospect"],
    ["South Africa", "Adcock Ingram / Local Partner", "Renal & Hospital Care", "National", "Yes", "Target Partner"],
    ["Kenya", "Harleys Pharma / Medical", "Hospital Supplies", "National", "Yes", "Target Partner"],
    ["Nigeria", "Drugfield / Local Partner", "Medical Consumables", "National", "Yes", "Prospect"],
    ["Ghana", "Tobbinco Medical", "Hospital Consumables", "National", "Yes", "Prospect"],
    ["Tanzania", "Astra Pharma / Medical", "Medical Devices", "National", "Yes", "Prospect"],
    ["Sudan", "To Be Verified (Post-Stability)", "Medical Supplies", "National", "Under Evaluation", "Under Evaluation"],
    ["Morocco", "Promamec", "Medical Devices & Dialysis", "National", "Yes", "Target Partner"]
]

for row in distributors_data:
    ws2.append(row)

# ----------------------------------------------------
# Sheet 3: Regulatory & Registration Timelines
# ----------------------------------------------------
ws3 = wb.create_sheet(title="Regulatory_Timelines")
headers3 = [
    "Country", "Target Authority", "Required Certificates", 
    "Compliance Route", "Estimated Access Timeline (Months)"
]
ws3.append(headers3)

regulatory_data = [
    ["Saudi Arabia", "SFDA (Saudi Food & Drug Authority)", "MDMA Approval via GHAD portal", "CE Mark + ISO 13485 + SFDA", 8],
    ["UAE", "MoHAP / DHA / DOH", "MoHAP Medical Device Registration", "CE Mark + ISO 13485", 4],
    ["Qatar", "MoPH Qatar", "MoPH Device Registration", "CE Mark + FSC", 4],
    ["Kuwait", "Ministry of Health (MoH)", "MoH Licensing", "CE Mark + ISO 13485", 6],
    ["Oman", "MoH Oman", "MoH Device Registration", "CE Mark + ISO 13485", 5],
    ["Bahrain", "NHRA Bahrain", "NHRA Listing", "CE Mark + ISO 13485", 4],
    ["South Africa", "SAHPRA", "Medical Device Establishment License", "CE Mark + ISO 13485", 6],
    ["Kenya", "Pharmacy & Poisons Board (PPB)", "PPB Device Import License", "CE Mark + ISO 13485", 5],
    ["Nigeria", "NAFDAC", "NAFDAC Product Registration", "CE Mark + ISO 13485", 9],
    ["Ghana", "FDA Ghana", "FDA Device Registration", "CE Mark + ISO 13485", 6],
    ["Tanzania", "TMDA", "TMDA Listing", "CE Mark + ISO 13485", 6],
    ["Sudan", "NMPB Sudan", "NMPB Special Import Permit", "CE Mark + ISO 13485", 12],
    ["Morocco", "DMP / MoH Morocco", "DMP Registration Certificate", "CE Mark + ISO 13485", 7]
]

for row in regulatory_data:
    ws3.append(row)

# ----------------------------------------------------
# Sheet 4: Financial & Patient Volume Assumptions
# ----------------------------------------------------
ws4 = wb.create_sheet(title="Financial_Model_Data")
headers4 = [
    "Region", "Country", "Strategic Tier", "Population", 
    "Metric Basis", "Active HD Patients", "Active PD Patients (GCC)", 
    "Est. Annual HD Catheter Units", "Est. Annual PD Catheter Units", 
    "Blended Price USD", "Projected Revenue USD"
]
ws4.append(headers4)

# بيانات المرضى وتوقعات المبيعات
financial_data = [
    ["GCC", "Saudi Arabia", "Tier 1", 36839707, "Treated ESRD", 31900, 2500, "=F2*2", "=G2*1.5", 85, "=(H2+I2)*J2"],
    ["GCC", "UAE", "Tier 2", 9516871, "Treated ESRD", 7060, 600, "=F3*2", "=G3*1.5", 85, "=(H3+I3)*J3"],
    ["GCC", "Qatar", "Tier 1", 2712499, "Treated ESRD", 941, 150, "=F4*2", "=G4*1.5", 85, "=(H4+I4)*J4"],
    ["GCC", "Kuwait", "Tier 1", 4962358, "Treated ESRD", 4312, 350, "=F5*2", "=G5*1.5", 85, "=(H5+I5)*J5"],
    ["GCC", "Oman", "Tier 1", 4649855, "Treated ESRD", 4650, 300, "=F6*2", "=G6*1.5", 85, "=(H6+I6)*J6"],
    ["GCC", "Bahrain", "Tier 1", 1477469, "Treated ESRD", 739, 80, "=F7*2", "=G7*1.5", 85, "=(H7+I7)*J7"],
    ["East Africa", "Kenya", "Tier 2", 55100586, "Treated ESRD", 11020, 0, "=F8*2", "=G8*1.5", 45, "=(H8+I8)*J8"],
    ["West Africa", "Nigeria", "Tier 2", 223804632, "Treated ESRD", 22380, 0, "=F9*2", "=G9*1.5", 45, "=(H9+I9)*J9"],
    ["West Africa", "Ghana", "Tier 2", 34494307, "Treated ESRD", 5174, 0, "=F10*2", "=G10*1.5", 45, "=(H10+I10)*J10"],
    ["East Africa", "Tanzania", "Tier 2", 67438106, "Treated ESRD", 8093, 0, "=F11*2", "=G11*1.5", 45, "=(H11+I11)*J11"],
    ["Southern Africa", "South Africa", "Tier 1", 60414495, "Treated ESRD", 72497, 0, "=F12*2", "=G12*1.5", 55, "=(H12+I12)*J12"],
    ["East Africa", "Sudan", "Tier 1", 48396555, "Treated ESRD", 7259, 0, "=F13*2", "=G13*1.5", 45, "=(H13+I13)*J13"],
    ["North Africa", "Morocco", "Tier 1", 37404874, "Treated ESRD", 22443, 0, "=F14*2", "=G14*1.5", 50, "=(H14+I14)*J14"]
]

for row in financial_data:
    ws4.append(row)

# ----------------------------------------------------
# Formatting & Styling Loop (تنسيق كل الشيتات)
# ----------------------------------------------------
for ws in wb.worksheets:
    # تنسيق الهيدر
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    # تنسيق صفوف البيانات وتعديل العرض تلقائياً
    for row in range(2, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = data_font
            cell.border = thin_border
            if isinstance(cell.value, (int, float)):
                cell.alignment = right_align
            else:
                cell.alignment = left_align

    # ضبط عرض الأعمدة تلقائياً
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# حفظ الملف النهائي
file_name = "MEA_Master_Intelligence_Workbook.xlsx"
wb.save(file_name)
print(f"✅ Executed Successfully! File saved as: {file_name}")
