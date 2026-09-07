from pathlib import Path

pdf_code = '''import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable

class PDFScheduleExporter:
    @staticmethod
    def generate_pdf(schedule_data: dict, project_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0f172a')
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#475569')
        )
        day_header_style = ParagraphStyle(
            'DayHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0284c7')
        )
        day_sub_style = ParagraphStyle(
            'DaySub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )
        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0f172a')
        )
        cell_normal = ParagraphStyle(
            'CellNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#334155')
        )

        story = []

        # Header Title Banner
        story.append(Paragraph(f"{project_data.get('name', 'Film Production')} — Production Shooting Schedule", title_style))
        sub_text = f"Director: {project_data.get('director', 'N/A')} | Company: {project_data.get('production_company', 'N/A')} | Version: {schedule_data.get('name', 'Schedule V1')} | Quality Score: {schedule_data.get('quality_score', 0):.0f}/100"
        story.append(Paragraph(sub_text, subtitle_style))
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0ea5e9'), spaceAfter=15))

        # Shooting Days
        days = schedule_data.get("shooting_days", [])
        for day in days:
            day_title = f"DAY {day['day_number']:02d} — {day['date']} ({day.get('primary_location_name', 'Location')})"
            story.append(Paragraph(day_title, day_header_style))

            day_meta = f"Call Time: {day['call_time']} | Wrap Time: {day['wrap_time']} | Sunrise: {day.get('sunrise_time', 'N/A')} | Sunset: {day.get('sunset_time', 'N/A')} | Weather: {day.get('weather_summary', 'N/A')}"
            story.append(Paragraph(day_meta, day_sub_style))
            story.append(Spacer(1, 8))

            # Table of Scenes for this day
            table_data = [
                [
                    Paragraph("Time", cell_bold),
                    Paragraph("Scene #", cell_bold),
                    Paragraph("Heading / Location", cell_bold),
                    Paragraph("Dur", cell_bold),
                    Paragraph("Cast", cell_bold),
                    Paragraph("Notes / Equipment", cell_bold)
                ]
            ]

            for item in day.get("items", []):
                sc = item.get("scene", {})
                time_range = f"{item['planned_start_time']}-{item['planned_end_time']}"
                code = sc.get("scene_code", f"SC{item['order_in_day']}")
                heading = f"{sc.get('scene_heading', item.get('location_name', 'Scene'))}"
                dur = f"{item['duration_minutes']}m"
                cast_str = ", ".join(sc.get("character_names", [])) or "—"
                notes = item.get("notes") or ""
                if item.get("company_move_before"):
                    notes = f"[Company Move: {item.get('travel_time_minutes_before', 30)}m] " + notes

                table_data.append([
                    Paragraph(time_range, cell_normal),
                    Paragraph(code, cell_bold),
                    Paragraph(heading, cell_normal),
                    Paragraph(dur, cell_normal),
                    Paragraph(cast_str, cell_normal),
                    Paragraph(notes, cell_normal)
                ])

            col_widths = [65, 45, 170, 35, 110, 115]
            day_table = Table(table_data, colWidths=col_widths)
            day_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ]))

            story.append(day_table)
            story.append(Spacer(1, 15))

        doc.build(story)
        return buffer.getvalue()
'''
Path("backend/app/services/pdf_export_service.py").write_text(pdf_code, encoding="utf-8")
print("PDFScheduleExporter created.")
