
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)


def generate_digest_pdf(digest, country="News"):
    """
    Convert a Markdown-style news digest into a PDF.
    Returns the PDF as bytes for Streamlit downloads.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"{country} Daily News Digest",
        author="AI News Assistant",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DigestTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "DigestHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "DigestBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )

    story = [
        Paragraph(
            escape(f"{country} Daily News Digest"),
            title_style,
        ),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#4472C4"),
        ),
        Spacer(1, 12),
    ]

    for line in digest.splitlines():

        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            story.append(
                Paragraph(escape(heading), heading_style)
            )

        elif line.startswith(("- ", "* ")):
            item = escape(line[2:])
            story.append(
                Paragraph(f"&bull; {item}", body_style)
            )

        else:
            story.append(
                Paragraph(escape(line), body_style)
            )

    document.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data
