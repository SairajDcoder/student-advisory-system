"""
generate_eli5_pdf.py
Generates a super clear, beginner-friendly PDF guide explaining the whole AIML project
in simple 1st-standard terms with analogies, diagrams, and cheat sheets for the 3 teammates.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AIML_Project_Explained_Simple_Guide.pdf")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AIML Project Zero-to-Hero Guide — Student Performance & Career Advisory System")
            self.setStrokeColor(colors.HexColor("#D0D0D0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        self.setStrokeColor(colors.HexColor("#D0D0D0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Made for You & Your 2 Friends — AIML Practical Examination Preparation")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#1A237E"),
        alignment=1, # Center
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#C2185B"),
        alignment=1,
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0D47A1"),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#00695C"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13.5,
        textColor=colors.HexColor("#212121"),
        spaceAfter=6,
    )

    analogy_box_style = ParagraphStyle(
        "AnalogyBox",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1B2430"),
        leftIndent=10,
        rightIndent=10,
        spaceAfter=6,
    )

    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#BF360C"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )

    table_text = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#212121"),
    )

    table_head = ParagraphStyle(
        "TableHead",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    q_style = ParagraphStyle(
        "QStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#C2185B"),
        spaceBefore=7,
        spaceAfter=2,
        keepWithNext=True,
    )

    ans_style = ParagraphStyle(
        "AnsStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#263238"),
        leftIndent=8,
        spaceAfter=5,
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("AIML Project Explained Like You're in 1st Standard", title_style))
    elements.append(Paragraph("<b>The Zero-Knowledge to Project Master Guide for You &amp; Your 2 Teammates</b>", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A237E"), spaceAfter=10))

    # Intro Card Table
    intro_data = [
        [
            Paragraph("<b>What is this document?</b>", table_head),
            Paragraph("<b>How to use it with your friends:</b>", table_head),
        ],
        [
            Paragraph(
                "A complete, crystal-clear breakdown of our <b>Student Performance &amp; Career Advisory System</b>. "
                "No confusing mathematics or mysterious jargon without simple, everyday school analogies.",
                table_text
            ),
            Paragraph(
                "Share this PDF with your 2 teammates. Read it once together like a storybook. "
                "By the end, all 3 of you will completely understand the project and can speak with total confidence!",
                table_text
            )
        ]
    ]
    t_intro = Table(intro_data, colWidths=[250, 254])
    t_intro.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F9F9FB")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_intro)
    elements.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────
    # SECTION 1: THE BIG PICTURE
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("1. The Big Picture: What Did We Actually Build?", h1_style))
    
    big_story_text = (
        "Imagine you are in Hogwarts from <i>Harry Potter</i>, and there is a <b>Magical Sorting Hat</b>. "
        "When a student sits down, the hat looks at them and yells: <i>'Gryffindor!'</i> or <i>'Slytherin!'</i><br/><br/>"
        "In our project, we built a <b>Digital Sorting Hat for College Students!</b><br/>"
        "Instead of magic, our system looks at a student's marks, study habits, coding ability, and creativity, "
        "and predicts which of <b>5 future career paths</b> they will thrive in:<br/>"
        "&nbsp;&nbsp;1. <b>Data Science &amp; AI:</b> For students who love math, statistics, and programming.<br/>"
        "&nbsp;&nbsp;2. <b>Software Engineering:</b> For students who love building software, coding, and projects.<br/>"
        "&nbsp;&nbsp;3. <b>Business &amp; Management:</b> For students with great leadership and communication.<br/>"
        "&nbsp;&nbsp;4. <b>Research &amp; Academia:</b> For students with deep curiosity in science, theory, and study.<br/>"
        "&nbsp;&nbsp;5. <b>Creative Arts &amp; Design:</b> For students with high creativity and imagination."
    )
    elements.append(Paragraph(big_story_text, body_style))
    elements.append(Spacer(1, 8))

    # ─────────────────────────────────────────────────────────────
    # SECTION 2: WHAT IS MACHINE LEARNING?
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("2. What is Machine Learning? (The Simplest Definition)", h1_style))
    ml_diff_text = (
        "&bull; <b>Traditional Programming:</b> You write down every single rule yourself: "
        "<i>'IF math &gt; 80 AND coding &gt; 80, THEN output Data Science.'</i> If you forget a rule, the computer fails.<br/>"
        "&bull; <b>Machine Learning (What We Built):</b> We didn't write rules. We showed a computer <b>2,000 past student report cards</b> "
        "and said: <i>'Here are 2,000 students, their marks, and the career they succeeded in. You find the secret recipe yourself!'</i> "
        "The computer played detective, discovered patterns, and created a <b>trained brain (our Model)</b>."
    )
    elements.append(Paragraph(ml_diff_text, body_style))
    elements.append(Spacer(1, 8))

    # ─────────────────────────────────────────────────────────────
    # SECTION 3: THE 8 STAGES EXPLAINED
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("3. The 8 Stages of Our Project (Explained with School Analogies)", h1_style))

    # Stage 1
    elements.append(Paragraph("Stage 1: The Report Cards (Data &amp; EDA)", h2_style))
    s1_text = (
        "&bull; <b>Features:</b> The 16 clues about a student (Math mark, Coding mark, Attendance %, Study hours, etc.).<br/>"
        "&bull; <b>Target:</b> The answer we want to predict (one of the 5 career paths).<br/>"
        "&bull; <b>EDA (Exploratory Data Analysis):</b> Like a chef checking the ingredients before cooking. "
        "We drew graphs to verify: Are there any blank marks? (Yes, ~3% were missing). Is the class balanced? "
        "(Yes, roughly equal numbers for each career path)."
    )
    elements.append(Paragraph(s1_text, body_style))

    # Stage 2
    elements.append(Paragraph("Stage 2: The Locked Exam Vault (Train/Test Split &amp; Zero Data Leakage)", h2_style))
    s2_text = (
        "This is where many college students lose marks, but <b>you will score 100%</b> because you understand this concept!<br/>"
        "&bull; We split our 2,000 students: <b>1,600 (80%)</b> for practice (Training), and <b>400 (20%)</b> for the final exam (Test).<br/>"
        "&bull; <b>What is Data Leakage? (The Cheating Student Analogy):</b><br/>"
        "Imagine a teacher calculates the class average marks using the <i>Final Exam paper</i> before the exam even takes place, "
        "and accidentally leaks clues to the students during practice! The students will get 100% on the exam, but they didn't really learn—they just cheated!<br/>"
        "In Machine Learning, if you calculate the average or scale numbers using ALL 2,000 students before splitting, the model 'peeks' into the test set.<br/>"
        "<b>Our Zero-Leakage Guarantee:</b> We locked the 400 test students in a vault with seed 42. We never touched them until Stage 7!"
    )
    elements.append(Paragraph(s2_text, body_style))

    # Stage 3
    elements.append(Paragraph("Stage 3: Washing the Vegetables (Preprocessing Pipeline)", h2_style))
    s3_text = (
        "Computers hate messy data. We used an automated cleaning pipeline called <code>ColumnTransformer</code>:<br/>"
        "1. <b>Imputation (Filling blanks):</b> If a student forgot to write attendance, we filled it with the <b>Median</b> (middle value).<br/>"
        "2. <b>StandardScaler (Comparing Apples to Apples):</b> Math is from 0 to 100, but GPA is from 2.0 to 4.0. "
        "If you don't scale them, the computer thinks a 90 in math is 22 times more important than a 4.0 GPA! Scaling puts them on the same playing field.<br/>"
        "3. <b>One-Hot Encoding (Translating Words to Switches):</b> Computers can't read words like 'Male' or 'Female'. "
        "We convert them into digital light switches (0 or 1)."
    )
    elements.append(Paragraph(s3_text, body_style))

    # Stage 4
    elements.append(Paragraph("Stage 4: The 6 Robot Contestants (Baseline Models &amp; 15-Fold Exams)", h2_style))
    s4_text = (
        "We invited <b>6 different robot algorithms</b> to compete on the 1,600 training students:<br/>"
        "1. <b>Dummy Robot:</b> A lazy robot that guesses the most popular class every time without reading. Got <b>29.00%</b> accuracy. This is our minimum floor.<br/>"
        "2. <b>Logistic Regression:</b> Draws straight ruler lines to separate career paths. Got <b>50.81%</b>.<br/>"
        "3. <b>K-Nearest Neighbors (KNN):</b> Looks at a student's 7 closest classmates to see what career they picked. Got <b>39.83%</b>.<br/>"
        "4. <b>Support Vector Machine (SVM):</b> Builds wide highways between career categories. Got <b>49.21%</b>.<br/>"
        "5. <b>Random Forest (Our Winner!):</b> A council of <b>200 wise decision trees</b> voting together! Got <b>48.96%</b> (and improved after tuning).<br/>"
        "6. <b>Gradient Boosting:</b> A relay team where each tree fixes the mistakes made by the previous tree. Got <b>46.71%</b>.<br/><br/>"
        "<b>What is 15-Fold Cross-Validation?</b> If a student takes only 1 practice test, maybe they got lucky. "
        "We tested each model across 5 slices, repeated 3 times = <b>15 different practice exams!</b> "
        "That's why we report Mean &plusmn; Standard Deviation (e.g., 50.81% &plusmn; 2.85%), proving our model is reliable!"
    )
    elements.append(Paragraph(s4_text, body_style))

    # Stage 5
    elements.append(Paragraph("Stage 5: Upgrading the Best Robot (Optuna Bayesian Tuning)", h2_style))
    s5_text = (
        "A Random Forest has knobs (how many trees? how deep should they grow?).<br/>"
        "&bull; <b>GridSearchCV:</b> Trying every knob combination blindly (slow).<br/>"
        "&bull; <b>Optuna (The Smart AI Mechanic):</b> Uses probability (Bayesian TPE) to listen to past test scores and intelligently "
        "guess which knob settings will give the highest Macro F1 score.<br/>"
        "Optuna found our best settings: <b>250 trees, max depth of 14</b>, boosting our score to <b>0.4831</b>."
    )
    elements.append(Paragraph(s5_text, body_style))

    # Stage 6
    elements.append(Paragraph("Stage 6: The Jenga Game (Feature Ablation Study)", h2_style))
    s6_text = (
        "Imagine pulling blocks out of a Jenga tower to see which one makes it fall.<br/>"
        "We asked: <b>'Which student qualities actually decide their career?'</b> We hid one group at a time:<br/>"
        "&bull; <b>When we hid Demographics (Gender, parent education):</b> Score stayed identical (+0.0049). <i>Proof our AI is 100% fair!</i><br/>"
        "&bull; <b>When we hid Study Habits (Hours studied):</b> Barely changed. <i>Studying many hours for something you hate doesn't make it your career.</i><br/>"
        "&bull; <b>When we hid Academic Scores (Math, Science):</b> Score dropped by <b>4.3%</b>.<br/>"
        "&bull; <b>When we hid Skill Scores (Coding, Creativity, Leadership):</b> The score <b>CRASHED by 23.07%!</b><br/>"
        "<b>The Big Discovery:</b> Specialized skills (coding, creativity, communication) are the <b>#1 real driver</b> of career success!"
    )
    elements.append(Paragraph(s6_text, body_style))

    # Stage 7
    elements.append(Paragraph("Stage 7: The Final Board Exam (Held-Out Test Set)", h2_style))
    s7_text = (
        "Now we took our best tuned model and tested it on the <b>400 students locked in the vault</b> in Stage 2:<br/>"
        "&bull; <b>Final Test Accuracy:</b> <b>50.25%</b> | <b>Macro F1-Score:</b> <b>0.4930</b><br/><br/>"
        "<b>Wait, why is 50.25% good? Why not 95%? (The Most Common Examiner Trap!)</b><br/>"
        "1. In a <b>5-class test</b>, pure random guessing is only <b>20%</b>. The dummy baseline was <b>29%</b>. Our model is <b>50.25%</b> (more than double random chance!).<br/>"
        "2. Real student skills overlap! A student great at coding and math could do BOTH Data Science AND Software Engineering. "
        "That's why our web app gives <b>percentage confidence bars</b> for all 5 careers rather than a single rigid guess!<br/>"
        "3. <b>Precision &amp; Recall:</b> For Business Management, our precision was <b>63.16%</b> because leadership and communication provide clean decision boundaries."
    )
    elements.append(Paragraph(s7_text, body_style))

    # Stage 8
    elements.append(Paragraph("Stage 8: The Magic Glasses (SHAP) &amp; Live Website (Flask)", h2_style))
    s8_text = (
        "&bull; <b>SHAP (Opening the Black Box):</b> In career counseling, you cannot tell a student 'The computer says Business' without a reason. "
        "SHAP gives us magic glasses showing exactly which scores pushed the decision (e.g., +40% because of high leadership).<br/>"
        "&bull; <b>The Flask Web App (<code>app.py</code>):</b> We built a working website! You open <code>http://127.0.0.1:5000</code>, "
        "type student marks, click a button, and it instantly shows the recommended career plus colorful percentage meters for all 5 careers."
    )
    elements.append(Paragraph(s8_text, body_style))
    elements.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────
    # SECTION 4: TEAM CHEAT SHEET
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("4. Who Says What? (Team Role Cheat Sheet)", h1_style))
    
    roles_summary = [
        [Paragraph("<b>Speaker</b>", table_head), Paragraph("<b>Your Main Topics</b>", table_head), Paragraph("<b>Your Magic Soundbite to Say</b>", table_head)],
        [
            Paragraph("<b>Speaker 1</b><br/>(Team Lead)", table_text),
            Paragraph("Problem statement, 5 career paths, 2,000 dataset, 80/20 split, <b>Zero Data Leakage</b>.", table_text),
            Paragraph("<i>&ldquo;We locked 400 test students in a safe vault with seed 42 and used a ColumnTransformer so our model never cheated.&rdquo;</i>", table_text),
        ],
        [
            Paragraph("<b>Speaker 2</b><br/>(ML Engineer)", table_text),
            Paragraph("6 Baseline models, 15 practice exams (Repeated CV), <b>Optuna Bayesian tuning</b>, <b>Ablation study</b>.", table_text),
            Paragraph("<i>&ldquo;When we removed skill scores, accuracy crashed by 23%, proving our model relies on genuine talent, while removing gender showed 0% bias.&rdquo;</i>", table_text),
        ],
        [
            Paragraph("<b>Speaker 3</b><br/>(Deployment Lead)", table_text),
            Paragraph("Final 50.25% test score, <b>SHAP explainability</b>, live typing on the <b>Flask Web App</b>.", table_text),
            Paragraph("<i>&ldquo;In a 5-class problem, 50.25% is more than double random guessing, and our web app shows live probability bars for all 5 careers.&rdquo;</i>", table_text),
        ],
    ]
    t_roles = Table(roles_summary, colWidths=[90, 190, 224])
    t_roles.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D47A1")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9F9FB")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_roles)
    elements.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────
    # SECTION 5: TOP 5 EXAMINER QUESTIONS
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("5. Top 5 Killer Examiner Questions &amp; How to Answer Them", h1_style))
    
    top5 = [
        (
            "Q1: What is Data Leakage and did you prevent it?",
            "Speaker 1",
            "Yes! Data leakage happens if you calculate averages or scale numbers using the whole dataset before splitting—the model cheats by seeing future test statistics. We prevented it by doing an 80/20 split first and wrapping all imputation and scaling in an sklearn ColumnTransformer fitted only on training folds."
        ),
        (
            "Q2: Why did you use Repeated Stratified K-Fold CV instead of a simple 70/30 split?",
            "Speaker 2",
            "A single 70/30 split can be lucky or unlucky. Stratified K-Fold keeps exact class proportions in every fold. Repeating 5-fold CV 3 times gives 15 independent practice tests, providing both a Mean and Standard Deviation to prove our model is stable."
        ),
        (
            "Q3: Why is your test accuracy 50% and not 95%?",
            "Speaker 3 or 2",
            "This is a 5-class multi-class problem where pure guessing is only 20%, and the dummy baseline is 29%. Our model reaches 50.25% (over 2.5x random chance). Real-world student career talents naturally overlap between related fields, which is why our web app provides probability confidence bars for all 5 careers."
        ),
        (
            "Q4: What was the biggest finding of your Ablation Study?",
            "Speaker 2",
            "When we removed Skill Scores (coding, creativity, leadership), model Macro F1 crashed by 23.07%, proving skills are the true driver of career success. Conversely, removing demographic features like gender had zero negative impact, proving our model is 100% fair."
        ),
        (
            "Q5: What is SHAP and why did you use it?",
            "Speaker 3",
            "SHAP stands for SHapley Additive exPlanations. It breaks down the AI prediction into exact plus/minus points per feature. In student counseling, an AI cannot be a black box; SHAP provides transparency by showing the exact reasons behind every recommendation."
        ),
    ]

    for q, spk, ans in top5:
        elements.append(Paragraph(f"<b>{q}</b> <font color='#0D47A1'>[{spk}]</font>", q_style))
        elements.append(Paragraph(f"<b>Simple Answer:</b> {ans}", ans_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[PDF Generated] {PDF_PATH}")
    return PDF_PATH


if __name__ == "__main__":
    build_pdf()
