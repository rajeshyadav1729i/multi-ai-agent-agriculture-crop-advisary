import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from typing import Dict, Any

def generate_advisory_pdf(advisory_data: Dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#064e3b'), # Dark Emerald
        alignment=TA_CENTER
    )
    
    sub_header_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#047857'),
        alignment=TA_CENTER
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#065f46'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1f2937'),
        alignment=TA_JUSTIFY
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#111827')
    )

    elements = []

    # 1. Header
    elements.append(Paragraph("AGRICULTURAL ADVISORY CONTROL ROOM", header_title_style))
    elements.append(Paragraph("GROUP 20 – MULTI-AGENT COLLABORATIVE AI SYSTEM | OFFICIAL FARMER ADVISORY", sub_header_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=2, spaceAfter=10))

    # 2. Farmer & Request Meta Table
    req_id = advisory_data.get("id", "ADV-2024")
    crop = advisory_data.get("crop_name", "Wheat")
    loc = advisory_data.get("location", "Ludhiana, Punjab")
    stage = advisory_data.get("crop_stage", "Flowering")
    farmer = advisory_data.get("farmer_name") or "Progressive Farmer"
    land = f"{advisory_data.get('land_area', 'N/A')} Acres" if advisory_data.get('land_area') else "General Holding"
    date_str = advisory_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))[:16].replace("T", " ")

    meta_table_data = [
        [
            Paragraph(f"<b>Farmer Name:</b> {farmer}", body_style),
            Paragraph(f"<b>Crop & Stage:</b> {crop} ({stage})", body_style),
            Paragraph(f"<b>Advisory ID:</b> {req_id[:12]}", body_style)
        ],
        [
            Paragraph(f"<b>Location:</b> {loc}", body_style),
            Paragraph(f"<b>Land Area:</b> {land}", body_style),
            Paragraph(f"<b>Issued Date:</b> {date_str}", body_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[175, 175, 175])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bbf7d0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dcfce7')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    final_adv = advisory_data.get("final_advisory") or {}
    risk_info = final_adv.get("risk_alert") or {}
    risk_level = (risk_info.get("risk_level") or advisory_data.get("risk_level") or "LOW").upper()

    # 3. Prominent Risk Alert Banner
    risk_bg = '#fef2f2' if risk_level in ('CRITICAL', 'HIGH') else ('#fffbeb' if risk_level == 'MEDIUM' else '#f0fdf4')
    risk_border = '#ef4444' if risk_level in ('CRITICAL', 'HIGH') else ('#f59e0b' if risk_level == 'MEDIUM' else '#10b981')
    risk_text_color = '#b91c1c' if risk_level in ('CRITICAL', 'HIGH') else ('#b45309' if risk_level == 'MEDIUM' else '#047857')

    risk_msg = risk_info.get("warning") or risk_info.get("primary_threat") or "Standard seasonal conditions observed."
    preventive = risk_info.get("preventive_action") or "Follow routine agronomic calendar."

    risk_banner_data = [
        [
            Paragraph(f"<font color='{risk_text_color}'><b>CRITICAL RISK ALERT: LEVEL {risk_level}</b></font>", bold_label),
        ],
        [
            Paragraph(f"<b>Threat Identified:</b> {risk_msg}", body_style)
        ],
        [
            Paragraph(f"<b>Urgent Action:</b> {preventive}", body_style)
        ]
    ]
    risk_table = Table(risk_banner_data, colWidths=[525])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(risk_bg)),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(risk_border)),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 10))

    # 4. Section 1: Weather Overview
    weather_info = final_adv.get("weather_overview") or {}
    elements.append(Paragraph("1. Meteorological & Weather Forecast", section_title_style))
    w_temp = weather_info.get("temperature", "24°C")
    w_hum = weather_info.get("humidity", "60%")
    w_cond = weather_info.get("condition", "Partly Cloudy")
    w_rain = weather_info.get("max_rain_prob_next_5_days", "15%")
    w_source = weather_info.get("data_source", "Open-Meteo Weather API")

    w_summary = f"Current temperature is <b>{w_temp}°C</b> with <b>{w_hum}%</b> relative humidity and <b>{w_cond}</b>. The highest rain probability over the upcoming 5 days is <b>{w_rain}%</b>. Data source: {w_source}."
    elements.append(Paragraph(w_summary, body_style))
    elements.append(Spacer(1, 8))

    # 5. Section 2: Recommended Field Actions
    field_actions = final_adv.get("field_actions") or {}
    elements.append(Paragraph("2. Agronomic & Crop Field Actions", section_title_style))
    irrigation_act = field_actions.get("irrigation_action") or "Maintain standard moisture level."
    fert_act = field_actions.get("fertilizer_action") or "Apply balanced NPK as per recommendation."
    crop_protection = field_actions.get("crop_protection") or "Scout crop regularly for signs of foliar blight or rust."

    field_data = [
        [Paragraph("<b>Irrigation Management:</b>", bold_label), Paragraph(irrigation_act, body_style)],
        [Paragraph("<b>Nutrient & Fertilizer:</b>", bold_label), Paragraph(fert_act, body_style)],
        [Paragraph("<b>Plant Protection:</b>", bold_label), Paragraph(crop_protection, body_style)],
    ]
    field_table = Table(field_data, colWidths=[140, 385])
    field_table.setStyle(TableStyle([
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(field_table)
    elements.append(Spacer(1, 8))

    # 6. Section 3: Mandi Market Analysis & Sell/Hold Recommendation
    market_info = final_adv.get("mandi_analysis") or {}
    mkt_rec = final_adv.get("market_recommendation") or {}
    elements.append(Paragraph("3. APMC Mandi Market Analysis & Recommendation", section_title_style))

    modal_p = market_info.get("modal_price", 2400)
    msp_val = market_info.get("msp", 2275)
    rec_sig = mkt_rec.get("action") or market_info.get("recommendation", "HOLD")
    mkt_reason = mkt_rec.get("reasoning") or market_info.get("reasoning", "Market prices stable.")
    mandi_name = market_info.get("mandi_name", "Local APMC Market")

    mkt_table_data = [
        [
            Paragraph(f"<b>Market:</b> {mandi_name}", body_style),
            Paragraph(f"<b>Modal Price:</b> Rs. {modal_p}/qtl", body_style),
            Paragraph(f"<b>MSP Benchmark:</b> Rs. {msp_val}/qtl", body_style),
            Paragraph(f"<b>Signal:</b> <font color='#059669'><b>{rec_sig}</b></font>", bold_label)
        ]
    ]
    mkt_table = Table(mkt_table_data, colWidths=[180, 115, 115, 115])
    mkt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9fafb')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(mkt_table)
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Advisory Note:</b> {mkt_reason}", body_style))
    elements.append(Spacer(1, 8))

    # 7. Section 4: Government Scheme (RAG Knowledge Base)
    scheme_info = final_adv.get("recommended_scheme") or {}
    elements.append(Paragraph("4. Government Scheme & Direct Benefits (RAG Knowledge Base)", section_title_style))
    s_title = scheme_info.get("title", "Pradhan Mantri Fasal Bima Yojana (PMFBY)")
    s_benefit = scheme_info.get("benefits") or scheme_info.get("description", "Comprehensive crop risk protection and subsidized credit.")
    s_portal = scheme_info.get("portal", "https://pmfby.gov.in")
    s_ref = scheme_info.get("source", "Ministry of Agriculture & Farmers Welfare")

    s_data = [
        [Paragraph(f"<b>Selected Scheme:</b> {s_title}", bold_label)],
        [Paragraph(f"<b>Financial Benefits:</b> {s_benefit}", body_style)],
        [Paragraph(f"<b>Official Source:</b> {s_ref} | Portal: {s_portal}", body_style)],
    ]
    s_table = Table(s_data, colWidths=[525])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#86efac')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(s_table)
    elements.append(Spacer(1, 8))

    # 8. Section 5: Practical Next Steps & Farmer Summary
    elements.append(Paragraph("5. Practical Farmer Action Plan", section_title_style))
    next_steps = final_adv.get("next_steps") or [
        "1. Inspect field drainage channels before potential rainfall.",
        "2. Keep crop registration documents and land records updated for DBT benefits.",
        "3. Check APMC daily rates before transporting produce to mandi."
    ]
    for step in next_steps:
        elements.append(Paragraph(f"• {step}", body_style))
        elements.append(Spacer(1, 2))

    summary_lang = final_adv.get("summary_farmer_language")
    if summary_lang:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("<b>Summary for the Farmer:</b>", bold_label))
        elements.append(Paragraph(f"<i>\"{summary_lang}\"</i>", body_style))

    # Footer note
    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#9ca3af'), spaceBefore=2, spaceAfter=6))
    elements.append(Paragraph(
        "Generated autonomously by Agricultural Advisory Control Room | Powered by Semantic Kernel Multi-Agent Architecture & Groq LLM | Group 20 Academic Demonstration",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
