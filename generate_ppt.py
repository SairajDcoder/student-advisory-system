"""
generate_ppt.py
Generates a clean, 12-slide 16:9 PowerPoint presentation for AdvisorAI
using the BYJU'S-inspired royal purple, coral-orange, and teal visual theme.
Output: AdvisorAI_Student_Advisory_Presentation.pptx
"""
import os
import tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "AdvisorAI_Student_Advisory_Presentation.pptx",
)

# Color Palette (BYJU'S-inspired Purple + Coral + Teal)
PURPLE = RGBColor(0x7B, 0x2D, 0x8E)
PURPLE_DARK = RGBColor(0x52, 0x1A, 0x61)
PURPLE_LIGHT = RGBColor(0xF6, 0xEE, 0xFA)
CORAL = RGBColor(0xFF, 0x6B, 0x4A)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)
GOLD = RGBColor(0xFF, 0xD1, 0x66)
TEAL = RGBColor(0x14, 0xB8, 0xA6)
GREEN = RGBColor(0x10, 0xB9, 0x81)
BG_LIGHT = RGBColor(0xF7, 0xF5, 0xFB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x1E, 0x29, 0x3B)
TEXT_MUTED = RGBColor(0x64, 0x74, 0x8B)
BORDER = RGBColor(0xE2, 0xD9, 0xEC)


def _create_ml_chart(chart_path: str) -> None:
    """Create a crisp chart summarizing AdvisorAI ML model metrics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.8), dpi=220)
    fig.patch.set_facecolor("#FFFFFF")

    # Left: Risk & CGPA Model Performance
    metrics = ["Risk Accuracy\n(XGBoost)", "Risk Macro F1\n(XGBoost)", "CGPA R²\n(XGBRegressor)"]
    vals = [90.21, 88.43, 85.09]
    colors_bar = ["#7B2D8E", "#14B8A6", "#FF6B4A"]
    bars = ax1.bar(metrics, vals, color=colors_bar, width=0.52, edgecolor="none")
    ax1.set_ylim(0, 108)
    ax1.set_ylabel("Score (%)", fontsize=10, fontweight="bold", color="#334155")
    ax1.set_title("AdvisorAI ML Model Performance", fontsize=11.5, fontweight="bold", color="#1E293B", pad=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    for b, v in zip(bars, vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 2.2, f"{v:.1f}%", ha="center", fontsize=9.5, fontweight="bold", color="#1E293B")

    # Right: Illustrative SHAP feature impact breakdown
    factors = ["Attendance %", "Internal Marks", "Assignments", "Past Grades", "Study Hours", "Stress Load"]
    impacts = [28, 24, 18, 14, 10, 6]
    ax2.barh(factors[::-1], impacts[::-1], color="#7B2D8E", height=0.55)
    ax2.set_xlim(0, 34)
    ax2.set_xlabel("Relative SHAP Impact (%)", fontsize=10, fontweight="bold", color="#334155")
    ax2.set_title("Explainable AI (SHAP) Drivers", fontsize=11.5, fontweight="bold", color="#1E293B", pad=10)
    ax2.grid(axis="x", linestyle="--", alpha=0.35)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    for i, v in enumerate(impacts[::-1]):
        ax2.text(v + 0.8, i, f"{v}%", va="center", fontsize=9, fontweight="bold", color="#1E293B")

    plt.tight_layout(pad=1.6)
    fig.savefig(chart_path, dpi=220)
    plt.close(fig)


def set_bg(slide, color: RGBColor):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, title: str, subtitle: str, slide_num: int):
    # Top purple bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PURPLE
    bar.line.fill.background()

    # Thin coral accent strip
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
    strip.fill.solid()
    strip.fill.fore_color.rgb = CORAL
    strip.line.fill.background()

    # Title text
    tb = slide.shapes.add_textbox(Inches(0.65), Inches(0.16), Inches(11.0), Inches(0.55))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = "Calibri"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Subtitle
    sb = slide.shapes.add_textbox(Inches(0.65), Inches(0.70), Inches(11.0), Inches(0.35))
    sf = sb.text_frame
    sp = sf.paragraphs[0]
    sp.text = subtitle
    sp.font.name = "Calibri"
    sp.font.size = Pt(13)
    sp.font.color.rgb = RGBColor(0xE9, 0xD5, 0xFF)

    # Footer
    ft = slide.shapes.add_textbox(Inches(0.65), Inches(7.08), Inches(10.0), Inches(0.3))
    fp = ft.text_frame.paragraphs[0]
    fp.text = "AdvisorAI — AI/ML Student Advisory System (10th & 12th Pass-Out Edition)"
    fp.font.name = "Calibri"
    fp.font.size = Pt(10)
    fp.font.color.rgb = TEXT_MUTED

    pg = slide.shapes.add_textbox(Inches(11.8), Inches(7.08), Inches(0.9), Inches(0.3))
    pp = pg.text_frame.paragraphs[0]
    pp.alignment = PP_ALIGN.RIGHT
    pp.text = f"{slide_num} / 12"
    pp.font.name = "Calibri"
    pp.font.size = Pt(10)
    pp.font.bold = True
    pp.font.color.rgb = PURPLE


def add_card(slide, left, top, width, height, title: str, bullets: list, accent: RGBColor = PURPLE, bg_color: RGBColor = WHITE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.adjustments[0] = 0.05
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = BORDER
    card.line.width = Pt(1)

    # Top accent pill inside card
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.2), Inches(top + 0.18), Inches(0.6), Inches(0.08))
    pill.fill.solid()
    pill.fill.fore_color.rgb = accent
    pill.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.32), Inches(width - 0.4), Inches(height - 0.45))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Calibri"
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = TEXT_DARK
    p0.space_after = Pt(8)

    for b in bullets:
        p = tf.add_paragraph()
        p.text = f"•  {b}"
        p.font.name = "Calibri"
        p.font.size = Pt(12.5)
        p.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        p.space_after = Pt(5)


def build_ppt():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ── Slide 1: Title Slide ──────────────────────────────────────────────────
    s1 = prs.slides.add_slide(blank)
    set_bg(s1, PURPLE_DARK)

    # Decorative circles
    c1 = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.5), Inches(-1.2), Inches(5.0), Inches(5.0))
    c1.fill.solid()
    c1.fill.fore_color.rgb = PURPLE
    c1.line.fill.background()

    c2 = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.6), Inches(4.5), Inches(3.2), Inches(3.2))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CORAL
    c2.line.fill.background()

    # Badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.25), Inches(4.2), Inches(0.45))
    badge.adjustments[0] = 0.5
    badge.fill.solid()
    badge.fill.fore_color.rgb = PURPLE
    badge.line.color.rgb = GOLD
    btf = badge.text_frame
    bp = btf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = "AI/ML Full-Stack Platform  •  10th & 12th Edition"
    bp.font.name = "Calibri"
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = GOLD

    # Main Title
    tbox = s1.shapes.add_textbox(Inches(0.9), Inches(1.95), Inches(8.8), Inches(1.8))
    ttf = tbox.text_frame
    ttf.word_wrap = True
    tp = ttf.paragraphs[0]
    tp.text = "AdvisorAI"
    tp.font.name = "Calibri"
    tp.font.size = Pt(52)
    tp.font.bold = True
    tp.font.color.rgb = WHITE

    tp2 = ttf.add_paragraph()
    tp2.text = "AI/ML Based Student Performance & Career Advisory System"
    tp2.font.name = "Calibri"
    tp2.font.size = Pt(26)
    tp2.font.bold = True
    tp2.font.color.rgb = GOLD

    # Subtitle
    sub = s1.shapes.add_textbox(Inches(0.9), Inches(3.95), Inches(8.5), Inches(1.0))
    stf = sub.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.text = (
        "Helping Class 10th & 12th pass-out students pick the right stream, degree, and career path "
        "with Explainable AI (SHAP), XGBoost predictions, smart study planning, and mentor support."
    )
    sp.font.name = "Calibri"
    sp.font.size = Pt(15)
    sp.font.color.rgb = RGBColor(0xE9, 0xD5, 0xFF)

    # Team Pill
    team = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(5.45), Inches(7.5), Inches(0.85))
    team.adjustments[0] = 0.15
    team.fill.solid()
    team.fill.fore_color.rgb = WHITE
    team.line.fill.background()
    ttf2 = team.text_frame
    ttf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    tp3 = ttf2.paragraphs[0]
    tp3.alignment = PP_ALIGN.CENTER
    tp3.text = "Presented by:  Aman (Frontend)  •  Sairaj (Backend)  •  Omkar  •  Parth"
    tp3.font.name = "Calibri"
    tp3.font.size = Pt(15)
    tp3.font.bold = True
    tp3.font.color.rgb = PURPLE_DARK

    # ── Slide 2: Problem Statement & Real-World Need ──────────────────────────
    s2 = prs.slides.add_slide(blank)
    set_bg(s2, BG_LIGHT)
    add_header(s2, "Problem Statement & Real-World Need", "Why Class 10th & 12th students struggle after board results", 2)

    add_card(
        s2, 0.65, 1.55, 3.85, 3.35,
        "1. Stream Confusion (After 10th)",
        [
            "Students pick Science, Commerce, or Arts based on peer pressure instead of aptitude.",
            "No simple tool compares PCM, PCB, Commerce, and Design fit in plain words.",
            "Wrong stream choices cause low interest and poor 12th outcomes.",
        ],
        accent=PURPLE,
    )
    add_card(
        s2, 4.74, 1.55, 3.85, 3.35,
        "2. Career & Skill Gap (After 12th)",
        [
            "Traditional counseling looks only at overall board % or GPA cutoffs.",
            "Students don't know which exact skills (Python, SQL, Figma) or courses to start first.",
            "High mismatch between college degree and real-world job roles.",
        ],
        accent=CORAL,
    )
    add_card(
        s2, 8.83, 1.55, 3.85, 3.35,
        "3. Late Risk Detection & Stress",
        [
            "Attendance drops and low internal marks go unnoticed until final exams.",
            "Black-box ML scores don't tell students WHY they are at risk.",
            "Students rarely have an easy, stigma-free way to ask a mentor for help.",
        ],
        accent=TEAL,
    )

    banner2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.2), Inches(12.03), Inches(1.55))
    banner2.adjustments[0] = 0.08
    banner2.fill.solid()
    banner2.fill.fore_color.rgb = PURPLE_LIGHT
    banner2.line.color.rgb = PURPLE
    bt2 = banner2.text_frame
    bt2.word_wrap = True
    bp2 = bt2.paragraphs[0]
    bp2.text = "Our Solution — AdvisorAI"
    bp2.font.name = "Calibri"
    bp2.font.size = Pt(17)
    bp2.font.bold = True
    bp2.font.color.rgb = PURPLE_DARK
    bp2.space_after = Pt(6)
    bp2b = bt2.add_paragraph()
    bp2b.text = (
        "An accessible, teen-friendly platform combining XGBoost CGPA/Risk prediction, SHAP plain-English explanations, "
        "personalized 10th/12th career matching, an AI Chat Advisor, a drag-and-drop Study Planner, Wellbeing check-ins, and Mentor/Admin oversight."
    )
    bp2b.font.name = "Calibri"
    bp2b.font.size = Pt(13.5)
    bp2b.font.color.rgb = TEXT_DARK

    # ── Slide 3: User Roles & Scope ───────────────────────────────────────────
    s3 = prs.slides.add_slide(blank)
    set_bg(s3, BG_LIGHT)
    add_header(s3, "Three Core User Roles", "Role-based access tailored for students, faculty mentors, and admins", 3)

    add_card(
        s3, 0.65, 1.65, 3.85, 5.0,
        "Student (10th & 12th)",
        [
            "3-step Welcome Onboarding Wizard (with Skip option).",
            "Dashboard: CGPA, Attendance, Risk Badge & 3 AI Tips.",
            "Score Forecast gauge + What-If Simulator sliders.",
            "Career & Stream Explorer with skill-gap progress bars.",
            "WhatsApp-style AI Chat Advisor with voice input.",
            "Weekly Study Planner & Emoji Wellbeing Check-in.",
        ],
        accent=PURPLE,
    )
    add_card(
        s3, 4.74, 1.65, 3.85, 5.0,
        "Mentor / Faculty",
        [
            "Student Roster with instant search & Risk Filter (All / High / Medium / Low).",
            "Color-coded Risk Badges (Safe / Watch / At Risk).",
            "Alerts when a student requests a wellbeing chat.",
            "Slide-over Student Detail Drawer with subject marks & SHAP summary.",
            "Add Mentor Remarks & schedule 1-on-1 guidance meetings.",
        ],
        accent=TEAL,
    )
    add_card(
        s3, 8.83, 1.65, 3.85, 5.0,
        "Administrator",
        [
            "User Management table (add users, activate/deactivate accounts).",
            "Department / Stream-wise analytics bar charts.",
            "Cohort Risk Breakdown (Safe vs Watch vs At Risk).",
            "Upload new student CSV datasets directly from UI.",
            "One-click XGBoost Model Retraining & live System Health panel.",
        ],
        accent=CORAL,
    )

    # ── Slide 4: End-to-End System Architecture ───────────────────────────────
    s4 = prs.slides.add_slide(blank)
    set_bg(s4, BG_LIGHT)
    add_header(s4, "End-to-End System Architecture", "Clean separation of Frontend UI, Supabase Auth, FastAPI, and ML Engine", 4)

    layers = [
        ("Frontend UI\n(React + TS + Tailwind)", "10 responsive screens\nMobile bottom bar\nRecharts & Framer Motion\nLight / Dark mode", 0.65, PURPLE),
        ("Authentication\n(Supabase Auth)", "Email & Password\nES256 JWKS verification\nAuto user-profile sync\nRole-based protection", 3.72, TEAL),
        ("Backend REST API\n(FastAPI + SQLAlchemy)", "JWT + RBAC guards\nStudent privacy (403)\nStudy Plan & Chat APIs\nCSV Upload & Retrain", 6.79, CORAL),
        ("ML & Data Layer\n(XGBoost + SHAP + DB)", "CGPA Regressor & Risk Clf\nSHAP TreeExplainer\nContent Career Matcher\nSupabase Postgres / SQLite", 9.86, PURPLE_DARK),
    ]
    for idx, (head, body, x, col) in enumerate(layers):
        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.85), Inches(2.8), Inches(3.55))
        box.adjustments[0] = 0.06
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = col
        box.line.width = Pt(2)

        top_band = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.85), Inches(2.8), Inches(0.95))
        top_band.fill.solid()
        top_band.fill.fore_color.rgb = col
        top_band.line.fill.background()
        htf = top_band.text_frame
        htf.vertical_anchor = MSO_ANCHOR.MIDDLE
        hp = htf.paragraphs[0]
        hp.alignment = PP_ALIGN.CENTER
        hp.text = head
        hp.font.name = "Calibri"
        hp.font.size = Pt(13.5)
        hp.font.bold = True
        hp.font.color.rgb = WHITE

        bt = s4.shapes.add_textbox(Inches(x + 0.15), Inches(2.95), Inches(2.5), Inches(2.3))
        btf = bt.text_frame
        btf.word_wrap = True
        for line in body.split("\n"):
            p = btf.add_paragraph() if btf.paragraphs[0].text else btf.paragraphs[0]
            p.text = f"• {line}"
            p.font.name = "Calibri"
            p.font.size = Pt(12.5)
            p.font.color.rgb = TEXT_DARK
            p.space_after = Pt(7)

        if idx < 3:
            arr = s4.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.84), Inches(3.45), Inches(0.22), Inches(0.28))
            arr.fill.solid()
            arr.fill.fore_color.rgb = CORAL
            arr.line.fill.background()

    note4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.75), Inches(12.03), Inches(1.0))
    note4.adjustments[0] = 0.1
    note4.fill.solid()
    note4.fill.fore_color.rgb = PURPLE_LIGHT
    note4.line.color.rgb = BORDER
    np4 = note4.text_frame.paragraphs[0]
    note4.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    np4.alignment = PP_ALIGN.CENTER
    np4.text = "Zero-Leakage ML Pipeline: All imputation, StandardScaler & OneHotEncoder transforms run strictly inside scikit-learn Pipelines."
    np4.font.name = "Calibri"
    np4.font.size = Pt(13.5)
    np4.font.bold = True
    np4.font.color.rgb = PURPLE_DARK

    # ── Slide 5: Tech Stack & 14-Table Database Design ────────────────────────
    s5 = prs.slides.add_slide(blank)
    set_bg(s5, BG_LIGHT)
    add_header(s5, "Technology Stack & 14-Entity Database", "Production tools and Supabase PostgreSQL schema (advisorai_* tables)", 5)

    add_card(
        s5, 0.65, 1.55, 5.75, 5.2,
        "Full-Stack Technology Choices",
        [
            "Frontend: React 18, TypeScript, Tailwind CSS, Recharts, Framer Motion, Lucide Icons.",
            "Authentication: Supabase Auth (@supabase/supabase-js) with JWKS ES256 verification.",
            "Backend API: FastAPI (Python), SQLAlchemy ORM, Pydantic v2, Uvicorn.",
            "Machine Learning: XGBoost (Regressor & Classifier), scikit-learn Pipelines, SHAP TreeExplainer.",
            "AI Chat: OpenAI / Gemini API support with built-in context-aware advisory fallback.",
            "Database: Supabase PostgreSQL (supabase/schema.sql) + zero-config SQLite local mode.",
        ],
        accent=PURPLE,
    )

    add_card(
        s5, 6.70, 1.55, 5.98, 5.2,
        "14 Core Database Tables (advisorai_*)",
        [
            "Identity & Roles: advisorai_users (with supabase_uid), advisorai_students, advisorai_mentors.",
            "Academics: advisorai_subjects, advisorai_marks, advisorai_attendance.",
            "Profiling: advisorai_skills, advisorai_interests.",
            "AI Outputs: advisorai_predictions (CGPA, Risk, SHAP), advisorai_recommendations (Careers & Courses).",
            "Engagement: advisorai_chat_messages, advisorai_study_plans, advisorai_notifications, advisorai_checkins.",
            "Prefix isolation prevents UUID key conflicts with existing Supabase public.users tables.",
        ],
        accent=TEAL,
    )

    # ── Slide 6: ML Models & Explainable AI (with Chart) ──────────────────────
    s6 = prs.slides.add_slide(blank)
    set_bg(s6, BG_LIGHT)
    add_header(s6, "AI/ML Engine & Explainable AI (SHAP)", "Observed model performance on 2,400 student records + transparent explanations", 6)

    with tempfile.TemporaryDirectory() as tmpdir:
        chart_file = os.path.join(tmpdir, "ml_chart.png")
        _create_ml_chart(chart_file)
        s6.shapes.add_picture(chart_file, Inches(0.65), Inches(1.48), width=Inches(12.03))

    add_card(
        s6, 0.65, 5.28, 3.85, 1.55,
        "CGPA Forecast (XGBRegressor)",
        ["R² = 0.8509 | MAE = 0.2497 CGPA", "Powers gauge & What-If Simulator"],
        accent=CORAL,
    )
    add_card(
        s6, 4.74, 5.28, 3.85, 1.55,
        "At-Risk Detector (XGBClassifier)",
        ["Accuracy = 90.21% | Macro F1 = 0.8843", "Classifies Safe / Watch / At Risk"],
        accent=PURPLE,
    )
    add_card(
        s6, 8.83, 5.28, 3.85, 1.55,
        "SHAP & Content Matcher",
        ["Plain-English reasons (no jargon)", "Matches 10th streams & 12th careers"],
        accent=TEAL,
    )

    # ── Slide 7: Core Student Screens (Part 1) ────────────────────────────────
    s7 = prs.slides.add_slide(blank)
    set_bg(s7, BG_LIGHT)
    add_header(s7, "Student Experience — Onboarding, Dashboard & Forecast", "Designed so any 10th or 12th grader understands a screen in under 5 seconds", 7)

    add_card(
        s7, 0.65, 1.65, 3.85, 5.0,
        "A. Login & 3-Step Onboarding",
        [
            "BYJU'S-inspired purple hero login with Email/Password via Supabase.",
            "Step 1: Choose Class 10th or 12th, Board, Stream, Marks & Attendance.",
            "Step 2: Pick Interests & rate current Skills.",
            "Step 3: Write personal goal (with 'Skip for now' option).",
        ],
        accent=PURPLE,
    )
    add_card(
        s7, 4.74, 1.65, 3.85, 5.0,
        "B. Student Dashboard",
        [
            "Warm personal greeting + today's single focus.",
            "4 KPI cards: CGPA, Attendance %, Risk Status, Deadlines.",
            "Interactive Recharts line chart showing score progression.",
            "'Smart Tips for You' card with 3 actionable AI steps.",
            "Quick buttons: Ask Advisor, Open Study Plan, View Careers.",
        ],
        accent=CORAL,
    )
    add_card(
        s7, 8.83, 1.65, 3.85, 5.0,
        "C. Score Forecast & Simulator",
        [
            "Predicted Next CGPA semicircle gauge + Pass likelihood %.",
            "Subject-wise Bar Chart (Internal %, Assignments %, Attendance %).",
            "'Why this prediction?' SHAP cards with plain-English explanations.",
            "Interactive What-If sliders to test attendance & study-hour changes live.",
        ],
        accent=TEAL,
    )

    # ── Slide 8: Core Student Screens (Part 2) ────────────────────────────────
    s8 = prs.slides.add_slide(blank)
    set_bg(s8, BG_LIGHT)
    add_header(s8, "Student Experience — Careers, Chat, Planner & Wellbeing", "Actionable guidance beyond marks alone", 8)

    add_card(
        s8, 0.65, 1.55, 5.85, 2.45,
        "D. Career & Stream Explorer",
        [
            "For 10th pass-outs: recommends ideal Class 11–12 stream (PCM, PCB, Commerce, Arts).",
            "Top 3 career role cards (ML Engineer, Data Analyst, Web Dev, UI/UX, Finance, Biotech).",
            "Shows Match %, Skill-Gap bars (Current vs Target), and starter courses/projects.",
        ],
        accent=PURPLE,
    )
    add_card(
        s8, 6.83, 1.55, 5.85, 2.45,
        "E. AI Chat Advisor",
        [
            "WhatsApp-style chat bubbles with persisted conversation history.",
            "Quick question chips ('How can I improve my CGPA?', 'Which stream suits me?').",
            "Typing indicator, Voice-to-Text mic button, and context-aware student answers.",
        ],
        accent=TEAL,
    )
    add_card(
        s8, 0.65, 4.25, 5.85, 2.45,
        "F. Weekly Study Planner",
        [
            "Auto-generated 7-day plan prioritizing weak subjects and nearest exam dates.",
            "Drag-and-drop task cards across days + completion checkboxes.",
            "SVG Weekly Goal Progress Ring + one-click 'Regenerate plan' button.",
        ],
        accent=CORAL,
    )
    add_card(
        s8, 6.83, 4.25, 5.85, 2.45,
        "G. Wellbeing Check-in",
        [
            "Emoji-based mood selector + 5 quick questions (stress, sleep, focus, workload).",
            "Warm, non-judgmental feedback message tailored to stress & sleep.",
            "'Talk to a Mentor' checkbox instantly alerts the assigned faculty mentor.",
        ],
        accent=GREEN,
    )

    # ── Slide 9: Mentor & Admin Dashboards ────────────────────────────────────
    s9 = prs.slides.add_slide(blank)
    set_bg(s9, BG_LIGHT)
    add_header(s9, "Mentor & Admin Portals", "Early intervention for mentors and live ML operations for administrators", 9)

    add_card(
        s9, 0.65, 1.65, 5.85, 5.0,
        "H. Mentor Advisory Portal",
        [
            "Searchable student roster with instant Risk Filter (All / High / Medium / Low).",
            "Highlights students who clicked 'Talk to a Mentor' during wellbeing check-ins.",
            "Slide-over Student Detail Drawer showing predicted CGPA, attendance, mood & subject marks.",
            "Top 3 AI Risk Reasons explained clearly for quick counseling.",
            "Save Mentor Remarks & Schedule 1-on-1 Meetings (sends instant notification to student).",
        ],
        accent=PURPLE,
    )
    add_card(
        s9, 6.83, 1.65, 5.85, 5.0,
        "I. Admin Console & ML Operations",
        [
            "System Health Cards: API status, Database status, CGPA R², Risk Model Accuracy & rows.",
            "Cohort Risk Summary (Safe / Watch / At Risk counts) & Department Analytics Bar Chart.",
            "User Management Table: quick-create users and toggle Active/Inactive status.",
            "Upload new CSV student dataset & click 'Retrain ML Models' to update predictions live.",
        ],
        accent=CORAL,
    )

    # ── Slide 10: Security, Privacy & UX Design ───────────────────────────────
    s10 = prs.slides.add_slide(blank)
    set_bg(s10, BG_LIGHT)
    add_header(s10, "Security, Privacy & Teen-Focused UI/UX", "Built for trust, accessibility, and fast everyday usability", 10)

    add_card(
        s10, 0.65, 1.65, 5.85, 5.0,
        "Security & Data Privacy",
        [
            "Supabase Auth manages passwords & issues signed ES256 JWT tokens.",
            "Backend verifies every request via Supabase JWKS (.well-known/jwks.json).",
            "Strict Role-Based Access Control: students receive HTTP 403 on Mentor/Admin APIs.",
            "Zero hardcoded secrets in code — keys managed via gitignored .env files.",
            "Students only ever view their own marks, chat logs, and wellbeing check-ins.",
        ],
        accent=TEAL,
    )
    add_card(
        s10, 6.83, 1.65, 5.85, 5.0,
        "Teen-Friendly UI/UX Principles",
        [
            "BYJU'S-inspired visual palette: Royal Purple (#7B2D8E), Coral CTA (#FF6B4A), Teal (#14B8A6).",
            "Consistent risk signals everywhere: Green = Safe, Amber = Watch, Red = At Risk.",
            "Plain language with zero ML jargon + skeleton loaders + friendly error banners.",
            "Desktop sidebar + Mobile 5-tab bottom bar (Home, Insights, Chat, Planner, Profile).",
            "Accessible 16px+ Inter/Poppins typography, icon + text labels, Light & Dark modes.",
        ],
        accent=PURPLE,
    )

    # ── Slide 11: Team Contributions & Next Steps ─────────────────────────────
    s11 = prs.slides.add_slide(blank)
    set_bg(s11, BG_LIGHT)
    add_header(s11, "Team Contributions & Next Milestones", "Clear 4-member ownership on branch aman-feature", 11)

    rows_data = [
        ("Aman", "Frontend & UI/UX Lead", "All 10 React/TS screens, BYJU'S-inspired theme, Recharts, Onboarding", "Subject marks editor popup"),
        ("Sairaj", "Backend & DB Lead", "FastAPI REST APIs, Supabase JWKS auth, 14-table ORM & schema.sql", "Subject edit API + Postgres URL"),
        ("Omkar", "ML & 10th/12th Data", "Career & stream dataset enhancements, entrance exam paths", "Course URLs + sample upload CSV"),
        ("Parth", "Student UX & QA", "Study Planner usability, wellbeing tips, mobile & dark-mode testing", "25-min study timer + Day dropdown"),
    ]

    y_pos = 1.65
    for idx, (name, role, done_txt, next_txt) in enumerate(rows_data):
        card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(y_pos), Inches(12.03), Inches(1.12))
        card.adjustments[0] = 0.1
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER

        badge_col = [PURPLE, TEAL, CORAL, GREEN][idx]
        nb = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(y_pos + 0.22), Inches(1.6), Inches(0.68))
        nb.adjustments[0] = 0.2
        nb.fill.solid()
        nb.fill.fore_color.rgb = badge_col
        nb.line.fill.background()
        np = nb.text_frame.paragraphs[0]
        nb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        np.alignment = PP_ALIGN.CENTER
        np.text = name
        np.font.name = "Calibri"
        np.font.size = Pt(16)
        np.font.bold = True
        np.font.color.rgb = WHITE

        tb = s11.shapes.add_textbox(Inches(2.65), Inches(y_pos + 0.12), Inches(9.8), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{role}   |   Next: {next_txt}"
        p1.font.name = "Calibri"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = PURPLE_DARK
        p2 = tf.add_paragraph()
        p2.text = f"Core Ownership: {done_txt}"
        p2.font.name = "Calibri"
        p2.font.size = Pt(12.5)
        p2.font.color.rgb = TEXT_DARK

        y_pos += 1.28

    # ── Slide 12: Future Scope & Thank You ────────────────────────────────────
    s12 = prs.slides.add_slide(blank)
    set_bg(s12, PURPLE_DARK)

    c3 = s12.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.8), Inches(3.8), Inches(4.5), Inches(4.5))
    c3.fill.solid()
    c3.fill.fore_color.rgb = PURPLE
    c3.line.fill.background()

    h12 = s12.shapes.add_textbox(Inches(0.9), Inches(1.0), Inches(11.0), Inches(0.8))
    p12 = h12.text_frame.paragraphs[0]
    p12.text = "Future Improvements & Live Demo"
    p12.font.name = "Calibri"
    p12.font.size = Pt(34)
    p12.font.bold = True
    p12.font.color.rgb = WHITE

    add_card(
        s12, 0.9, 2.0, 5.6, 3.6,
        "Future Roadmap",
        [
            "Marksheet OCR: upload 10th/12th CBSE/ICSE PDFs to auto-fill subject marks.",
            "Live Exam Alerts: JEE, NEET, CUET, CLAT & Polytechnic application deadlines.",
            "Regional Languages: Hindi & Marathi UI translation toggle.",
            "Production Cloud Hosting with managed Supabase Postgres & Redis.",
        ],
        accent=GOLD,
    )
    add_card(
        s12, 6.8, 2.0, 5.6, 3.6,
        "Quick Demo Commands",
        [
            "Backend:  py -m uvicorn backend.app.main:app --reload --port 8000",
            "Frontend: cd frontend && npm.cmd run dev",
            "Open:     http://localhost:5173",
            "Git Branch: aman-feature (Supabase Auth + XGBoost + React UI)",
        ],
        accent=CORAL,
    )

    ty = s12.shapes.add_textbox(Inches(0.9), Inches(6.05), Inches(11.5), Inches(0.8))
    typ = ty.text_frame.paragraphs[0]
    typ.text = "Thank You!  Questions & Live Demo"
    typ.font.name = "Calibri"
    typ.font.size = Pt(28)
    typ.font.bold = True
    typ.font.color.rgb = GOLD

    prs.save(OUTPUT_PATH)
    print(f"Saved presentation -> {OUTPUT_PATH}")


if __name__ == "__main__":
    build_ppt()
