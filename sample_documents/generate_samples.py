"""Script to generate realistic sample policy PDFs for demonstration and testing."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_sample_pdfs():
    os.makedirs("sample_documents", exist_ok=True)
    pdf_v1_path = os.path.join("sample_documents", "policy_v1.pdf")
    pdf_v2_path = os.path.join("sample_documents", "policy_v2.pdf")

    # Document 1: 2024 Policy v1.2
    c1 = canvas.Canvas(pdf_v1_path, pagesize=letter)
    # Page 1
    c1.setFont("Helvetica-Bold", 16)
    c1.drawString(50, 750, "TechCorp Remote Work and Equipment Policy (2024)")
    c1.setFont("Helvetica", 10)
    c1.drawString(50, 735, "Document Version: 1.2 | Effective Date: January 1, 2024 | Author: HR Operations")
    c1.line(50, 725, 550, 725)

    c1.setFont("Helvetica-Bold", 12)
    c1.drawString(50, 700, "1. Purpose & Scope")
    c1.setFont("Helvetica", 10)
    p1_lines = [
        "This policy establishes the guidelines and responsibilities for employees approved for remote work.",
        "TechCorp is committed to providing a flexible work environment while maintaining operational security",
        "and productivity standards across all distributed global teams.",
    ]
    y = 685
    for line in p1_lines:
        c1.drawString(50, y, line)
        y -= 15

    c1.setFont("Helvetica-Bold", 12)
    c1.drawString(50, y - 10, "2. Eligibility Criteria")
    y -= 30
    c1.setFont("Helvetica", 10)
    p2_lines = [
        "- Eligibility is limited strictly to full-time permanent employees who have completed at least 6 months of tenure.",
        "- Contract employees, seasonal workers, and interns are not eligible for remote work allowances.",
        "- Candidates must receive formal written approval from their department manager prior to commencing remote work.",
    ]
    for line in p2_lines:
        c1.drawString(50, y, line)
        y -= 15

    c1.setFont("Helvetica-Bold", 12)
    c1.drawString(50, y - 10, "3. Working Hours & Availability")
    y -= 30
    c1.setFont("Helvetica", 10)
    p3_lines = [
        "- Core working hours are mandatory from 10:00 AM to 4:00 PM EST, Monday through Friday.",
        "- Employees must remain accessible on Slack and respond to company emails within 2 hours during core hours.",
        "- Total weekly commitment is 40 hours standard for all salaried staff.",
    ]
    for line in p3_lines:
        c1.drawString(50, y, line)
        y -= 15

    c1.setFont("Helvetica-Oblique", 9)
    c1.drawString(50, 50, "TechCorp Remote Work Policy 2024 - Page 1 of 2")
    c1.showPage()

    # Page 2
    c1.setFont("Helvetica-Bold", 14)
    c1.drawString(50, 750, "TechCorp Remote Work and Equipment Policy (2024) - Continued")
    c1.line(50, 740, 550, 740)

    c1.setFont("Helvetica-Bold", 12)
    c1.drawString(50, 715, "4. Equipment Allowance & Reimbursement")
    c1.setFont("Helvetica", 10)
    p4_lines = [
        "- Eligible employees receive a one-time home office equipment stipend of $500.00 USD.",
        "- Reimbursable items include ergonomic chairs, external monitors, keyboards, and mice.",
        "- Expense claims must be submitted with original receipts within 30 days of purchase.",
        "- All company-purchased IT assets remain property of TechCorp and must be returned upon separation.",
    ]
    y = 700
    for line in p4_lines:
        c1.drawString(50, y, line)
        y -= 15

    c1.setFont("Helvetica-Bold", 12)
    c1.drawString(50, y - 10, "5. Information Security & Compliance")
    y -= 30
    c1.setFont("Helvetica", 10)
    p5_lines = [
        "- Remote employees must always connect through the secure company VPN when accessing internal services.",
        "- System passwords must be updated every 90 days following enterprise complexity standards.",
        "- Storing confidential customer data on unencrypted personal storage media is strictly prohibited.",
    ]
    for line in p5_lines:
        c1.drawString(50, y, line)
        y -= 15

    c1.setFont("Helvetica-Bold", 12)
    c1.drawString(50, y - 10, "6. Annual Policy Review")
    y -= 30
    c1.setFont("Helvetica", 10)
    c1.drawString(50, y, "This policy is scheduled for formal review and governance audit on December 15, 2024.")

    c1.setFont("Helvetica-Oblique", 9)
    c1.drawString(50, 50, "TechCorp Remote Work Policy 2024 - Page 2 of 2")
    c1.showPage()
    c1.save()

    # Document 2: 2025 Policy v2.0
    c2 = canvas.Canvas(pdf_v2_path, pagesize=letter)
    # Page 1
    c2.setFont("Helvetica-Bold", 16)
    c2.drawString(50, 750, "TechCorp Remote Work and Equipment Policy (2025)")
    c2.setFont("Helvetica", 10)
    c2.drawString(50, 735, "Document Version: 2.0 | Effective Date: January 1, 2025 | Author: HR Operations & People Team")
    c2.line(50, 725, 550, 725)

    c2.setFont("Helvetica-Bold", 12)
    c2.drawString(50, 700, "1. Purpose & Scope")
    c2.setFont("Helvetica", 10)
    p1_lines_v2 = [
        "This policy establishes the guidelines and responsibilities for employees approved for remote work.",
        "TechCorp is committed to providing a flexible work environment while maintaining operational security",
        "and productivity standards across all distributed global teams.",
    ]
    y = 685
    for line in p1_lines_v2:
        c2.drawString(50, y, line)
        y -= 15

    c2.setFont("Helvetica-Bold", 12)
    c2.drawString(50, y - 10, "2. Eligibility Criteria")
    y -= 30
    c2.setFont("Helvetica", 10)
    p2_lines_v2 = [
        "- Eligibility is extended to full-time permanent employees who have completed at least 3 months of tenure.",
        "- Engineering and design interns are eligible for a 50% remote equipment stipend upon manager approval.",
        "- Contract employees and seasonal workers remain ineligible for remote equipment allowances.",
        "- Candidates must receive formal written approval from their department manager prior to commencing remote work.",
    ]
    for line in p2_lines_v2:
        c2.drawString(50, y, line)
        y -= 15

    c2.setFont("Helvetica-Bold", 12)
    c2.drawString(50, y - 10, "3. Working Hours & Availability")
    y -= 30
    c2.setFont("Helvetica", 10)
    p3_lines_v2 = [
        "- Core working hours are mandatory from 10:00 AM to 3:00 PM EST, Monday through Friday.",
        "- Employees must remain accessible on Slack and respond to company emails within 2 hours during core hours.",
        "- Total weekly commitment is 40 hours standard for all salaried staff.",
    ]
    for line in p3_lines_v2:
        c2.drawString(50, y, line)
        y -= 15

    c2.setFont("Helvetica-Oblique", 9)
    c2.drawString(50, 50, "TechCorp Remote Work Policy 2025 - Page 1 of 2")
    c2.showPage()

    # Page 2
    c2.setFont("Helvetica-Bold", 14)
    c2.drawString(50, 750, "TechCorp Remote Work and Equipment Policy (2025) - Continued")
    c2.line(50, 740, 550, 740)

    c2.setFont("Helvetica-Bold", 12)
    c2.drawString(50, 715, "4. Equipment Allowance & Reimbursement")
    c2.setFont("Helvetica", 10)
    p4_lines_v2 = [
        "- Eligible employees receive a one-time home office equipment stipend of $750.00 USD.",
        "- Reimbursable items include ergonomic chairs, standing desks, external monitors, keyboards, and mice.",
        "- Expense claims must be submitted with original receipts within 15 days of purchase.",
        "- All company-purchased IT assets remain property of TechCorp and must be returned upon separation.",
    ]
    y = 700
    for line in p4_lines_v2:
        c2.drawString(50, y, line)
        y -= 15

    c2.setFont("Helvetica-Bold", 12)
    c2.drawString(50, y - 10, "5. Information Security & Compliance")
    y -= 30
    c2.setFont("Helvetica", 10)
    p5_lines_v2 = [
        "- Remote employees must always connect through the secure company VPN when accessing internal services.",
        "- Mandatory multi-factor authentication (MFA) with FIDO2 hardware security keys is now strictly required.",
        "- System passwords must be updated every 90 days following enterprise complexity standards.",
        "- Storing confidential customer data on unencrypted personal storage media is strictly prohibited.",
    ]
    for line in p5_lines_v2:
        c2.drawString(50, y, line)
        y -= 15

    c2.setFont("Helvetica-Bold", 12)
    c2.drawString(50, y - 10, "6. Annual Policy Review")
    y -= 30
    c2.setFont("Helvetica", 10)
    c2.drawString(50, y, "This policy is scheduled for formal review and governance audit on December 15, 2025.")

    c2.setFont("Helvetica-Oblique", 9)
    c2.drawString(50, 50, "TechCorp Remote Work Policy 2025 - Page 2 of 2")
    c2.showPage()
    c2.save()


if __name__ == "__main__":
    create_sample_pdfs()
    print("Sample PDFs successfully created.")

