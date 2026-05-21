import os
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf_report(test_name, steps):
    """
    steps = [
        {
            "name": "Open Page",
            "status": "PASS",
            "image": "path",
            "reason": ""
        },
        ...
    ]
    """

    os.makedirs("reports", exist_ok=True)
    file_name = f"reports/{test_name}.pdf"

    doc = SimpleDocTemplate(file_name, pagesize=A4)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"Test Report: {test_name}", styles["Title"]))
    content.append(Spacer(1, 20))

    for step in steps:
        status = step.get("status", "UNKNOWN")
        step_title = f"{step.get('name', 'Unnamed Step')} - {status}"

        content.append(Paragraph(step_title, styles["Heading2"]))
        content.append(Spacer(1, 8))

        if step.get("reason"):
            content.append(
                Paragraph(
                    f"<b>Reason:</b> {step['reason']}",
                    styles["Normal"]
                )
            )
            content.append(Spacer(1, 10))

        if step.get("image"):
            img = Image(step["image"], width=400, height=250)
            content.append(img)

        content.append(Spacer(1, 20))

    doc.build(content)
    return file_name