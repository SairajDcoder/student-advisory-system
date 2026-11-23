"""
generate_pdf.py
Generates a professional, publication-quality PDF presentation script
for 3 team members explaining the project to the external examiner.
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

PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Project_Presentation_Script_3_Members.pdf")


class NumberedCanvas(canvas.Canvas):
    """Adds page numbers and running headers/footers to all pages."""
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
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Student Performance & Career Advisory System — 3-Member Presentation Script")
            self.setStrokeColor(colors.HexColor("#D0D0D0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        self.setStrokeColor(colors.HexColor("#D0D0D0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential — AIML Practical Examination Project Script")
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
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A237E"),
        alignment=1, # Center
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#455A64"),
        alignment=1,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0D47A1"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#263238"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#212121"),
        spaceAfter=6,
    )

    dialogue_style = ParagraphStyle(
        "Dialogue_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1B2430"),
        leftIndent=12,
        spaceAfter=8,
    )

    stage_direction_style = ParagraphStyle(
        "StageDirection",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#00695C"),
        leftIndent=12,
        spaceAfter=6,
    )

    speaker_badge_1 = ParagraphStyle(
        "Speaker1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#004D40"), # Teal Dark
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    speaker_badge_2 = ParagraphStyle(
        "Speaker2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#B71C1C"), # Red Dark
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    speaker_badge_3 = ParagraphStyle(
        "Speaker3",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#4A148C"), # Purple Dark
        spaceBefore=10,
        spaceAfter=4,
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
        "QuestionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#C2185B"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    ans_style = ParagraphStyle(
        "AnswerStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#263238"),
        leftIndent=10,
        spaceAfter=6,
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("Student Performance &amp; Career Advisory System", title_style))
    elements.append(Paragraph("<b>AIML Practical Examination — 3-Member Presentation Script &amp; Viva Voce Guide</b>", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A237E"), spaceAfter=12))

    # Team Role Card Table
    role_data = [
        [
            Paragraph("<b>Member</b>", table_head),
            Paragraph("<b>Designated Role</b>", table_head),
            Paragraph("<b>Core Topics Owned</b>", table_head),
            Paragraph("<b>Timing</b>", table_head),
        ],
        [
            Paragraph("<b>Speaker 1</b><br/>(Team Lead)", table_text),
            Paragraph("Problem &amp; Data Pipeline Lead", table_text),
            Paragraph("Motivation, 5 Career Domains, 2,000 Dataset Features, <b>Zero Data Leakage Guarantee</b> &amp; ColumnTransformer.", table_text),
            Paragraph("~2.5 mins", table_text),
        ],
        [
            Paragraph("<b>Speaker 2</b><br/>(ML Engineer)", table_text),
            Paragraph("Modeling &amp; Tuning Lead", table_text),
            Paragraph("6 Baseline Models, 15-Fold Repeated Stratified CV, <b>Optuna Bayesian Tuning (TPE)</b>, and <b>Ablation Study</b>.", table_text),
            Paragraph("~3.0 mins", table_text),
        ],
        [
            Paragraph("<b>Speaker 3</b><br/>(Deployment Lead)", table_text),
            Paragraph("Evaluation &amp; System Lead", table_text),
            Paragraph("Single-Pass Test Evaluation (Confusion Matrix &amp; ROC), <b>SHAP Explainability</b>, and <b>Live Flask Web Demo</b>.", table_text),
            Paragraph("~2.5 mins", table_text),
        ],
    ]
    role_table = Table(role_data, colWidths=[80, 110, 240, 74])
    role_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(role_table)
    elements.append(Spacer(1, 14))

    # ─────────────────────────────────────────────────────────────
    # PART 1: SPEAKER 1
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("PART 1: THE FOUNDATION &amp; DATA PIPELINE", h1_style))
    elements.append(Paragraph("🎤 <b>Speaker 1 (Team Lead)</b> — <i>Opening, Problem Definition, Dataset, Preprocessing</i>", speaker_badge_1))
    
    s1_text = (
        "&ldquo;Good morning / afternoon Respected External Examiner and Faculty. Today, our team is demonstrating our "
        "Artificial Intelligence &amp; Machine Learning practical project: <b>'Student Performance and Career Advisory System'</b>.<br/><br/>"
        "I am <b>[Speaker 1 Name]</b>, and alongside my teammates <b>[Speaker 2 Name]</b> and <b>[Speaker 3 Name]</b>, we have engineered "
        "this project in strict adherence to the <b>8-Stage Machine Learning Implementation Pipeline</b> and IEEE evaluation rubrics.<br/><br/>"
        "<b>The Problem We Solve:</b> In higher education, students frequently struggle to identify professional trajectories that match their "
        "multidimensional strengths. Traditional counseling relies on subjective opinions or simple GPA thresholds. But GPA alone cannot determine "
        "whether a student is suited for Software Engineering, Data Science, or Corporate Management.<br/><br/>"
        "<b>Our Objective:</b> To create an objective, predictive Machine Learning system that guides students into <b>5 distinct career trajectories</b>:<br/>"
        "&nbsp;&nbsp;&bull; <b>Data Science &amp; AI</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Software Engineering</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Business &amp; Management</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Research &amp; Academia</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Creative Arts &amp; Design</b><br/><br/>"
        "<b>Dataset Architecture:</b> We structured a dataset of <b>2,000 student records</b> across <b>16 multidimensional features</b> spanning "
        "Academic Scores (Math, Science, English), Academic Habits (weekly study hours, attendance %, prior GPA), Cognitive Aptitudes "
        "(Programming, Creativity), Soft Skills (Communication, Leadership), Experience (Internships, Projects, Extracurriculars), and Demographics.<br/><br/>"
        "<b>Zero Data Leakage Guarantee:</b> One of the most critical aspects evaluated in our rubric is <i>data integrity</i>. "
        "Many student projects make the mistake of scaling data or filling missing values before splitting. That leaks future test information into training.<br/>"
        "In our project, we enforced strict isolation:<br/>"
        "1. First, we performed an <b>80/20 Stratified Split</b> with a fixed random seed of 42. Exactly <b>400 student instances were vaulted untouched</b> as our held-out test set.<br/>"
        "2. Second, we built a modular <code>ColumnTransformer</code>. We applied <b>Median Imputation</b> and <b>StandardScaler</b> for numerical features, and <b>Mode Imputation</b> with <b>OneHotEncoder</b> for categoricals.<br/>"
        "3. Crucially, all transformations were fitted exclusively on training folds and merely transformed on test data.<br/><br/>"
        "Now, I hand over to <b>[Speaker 2 Name]</b> to discuss our baseline benchmarking, Bayesian hyperparameter tuning, and ablation experiments.&rdquo;"
    )
    elements.append(Paragraph(s1_text, dialogue_style))
    elements.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────
    # PART 2: SPEAKER 2
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("PART 2: MODEL BENCHMARKING, BAYESIAN TUNING &amp; ABLATION", h1_style))
    elements.append(Paragraph("🎤 <b>Speaker 2 (ML Engineer)</b> — <i>Baselines, 15-Fold Repeated CV, Optuna TPE, Feature Ablation</i>", speaker_badge_2))

    s2_text = (
        "&ldquo;Thank you, [Speaker 1 Name]. Good morning/afternoon, Examiner. I am <b>[Speaker 2 Name]</b>, and I will explain how we "
        "trained, tuned, and empirically validated our models.<br/><br/>"
        "<b>Stage 4: Baseline Models &amp; Repeated Stratified CV:</b><br/>"
        "Rather than picking an arbitrary algorithm, Stage 4 required training 3+ models plus an empirical baseline. We benchmarked <b>6 classifiers</b>:<br/>"
        "&nbsp;&nbsp;1. <b>Dummy Baseline Classifier:</b> Predicts the most frequent class, setting our lower-bound baseline at <b>29.00%</b>.<br/>"
        "&nbsp;&nbsp;2. <b>Multinomial Logistic Regression</b><br/>"
        "&nbsp;&nbsp;3. <b>K-Nearest Neighbors (k=7)</b><br/>"
        "&nbsp;&nbsp;4. <b>Support Vector Machine (RBF Kernel)</b><br/>"
        "&nbsp;&nbsp;5. <b>Random Forest (200 Trees)</b><br/>"
        "&nbsp;&nbsp;6. <b>Gradient Boosting</b><br/><br/>"
        "To ensure high statistical reliability, we utilized <b>Repeated Stratified 5-Fold Cross-Validation with 3 repeats</b> — meaning each algorithm was evaluated across <b>15 independent validation folds</b>. We recorded both the <b>Mean and Standard Deviation</b>.&rdquo;"
    )
    elements.append(Paragraph(s2_text, dialogue_style))

    # Baseline Table in PDF
    elements.append(Paragraph("<i>Table 1: Baseline Comparison Results (15-Fold Cross-Validation, Mean &plusmn; Std)</i>", stage_direction_style))
    base_data = [
        [Paragraph("<b>Model</b>", table_head), Paragraph("<b>Accuracy</b>", table_head), Paragraph("<b>Macro F1</b>", table_head), Paragraph("<b>Macro Precision</b>", table_head), Paragraph("<b>Macro Recall</b>", table_head)],
        [Paragraph("Dummy (Baseline)", table_text), Paragraph("0.2900 &plusmn; 0.0013", table_text), Paragraph("0.0899 &plusmn; 0.0003", table_text), Paragraph("0.0580 &plusmn; 0.0003", table_text), Paragraph("0.2000 &plusmn; 0.0000", table_text)],
        [Paragraph("Logistic Regression", table_text), Paragraph("<b>0.5081 &plusmn; 0.0285</b>", table_text), Paragraph("<b>0.4908 &plusmn; 0.0294</b>", table_text), Paragraph("0.4965 &plusmn; 0.0307", table_text), Paragraph("0.4922 &plusmn; 0.0282", table_text)],
        [Paragraph("Random Forest", table_text), Paragraph("0.4896 &plusmn; 0.0242", table_text), Paragraph("0.4714 &plusmn; 0.0227", table_text), Paragraph("0.4951 &plusmn; 0.0223", table_text), Paragraph("0.4662 &plusmn; 0.0227", table_text)],
        [Paragraph("Support Vector Machine", table_text), Paragraph("0.4921 &plusmn; 0.0194", table_text), Paragraph("0.4712 &plusmn; 0.0202", table_text), Paragraph("0.4886 &plusmn; 0.0236", table_text), Paragraph("0.4717 &plusmn; 0.0189", table_text)],
        [Paragraph("Gradient Boosting", table_text), Paragraph("0.4671 &plusmn; 0.0248", table_text), Paragraph("0.4586 &plusmn; 0.0250", table_text), Paragraph("0.4665 &plusmn; 0.0254", table_text), Paragraph("0.4550 &plusmn; 0.0248", table_text)],
        [Paragraph("K-Nearest Neighbors", table_text), Paragraph("0.3983 &plusmn; 0.0231", table_text), Paragraph("0.3685 &plusmn; 0.0215", table_text), Paragraph("0.3857 &plusmn; 0.0273", table_text), Paragraph("0.3736 &plusmn; 0.0205", table_text)],
    ]
    base_table = Table(base_data, colWidths=[120, 100, 95, 95, 94])
    base_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D47A1")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(base_table)
    elements.append(Spacer(1, 8))

    s2_text_pt2 = (
        "&ldquo;<b>Stage 5: Bayesian Hyperparameter Tuning with Optuna:</b><br/>"
        "In Stage 5, we utilized <b>Optuna</b> using the <b>Tree-structured Parzen Estimator (TPE)</b> for 40 trials to tune our Random Forest model. "
        "Unlike exhaustive GridSearch which tests combinations blindly, Optuna builds a probability model over the parameter space. "
        "The optimal configuration found was: <code>n_estimators=250, max_depth=14, min_samples_split=11, min_samples_leaf=3</code>, "
        "achieving a validation Macro F1 of <b>0.4831</b>.<br/><br/>"
        "<b>Stage 6: Feature Ablation Study:</b><br/>"
        "To investigate which features genuinely drive career predictions, we conducted a systematic ablation study by removing one feature group at a time:&rdquo;"
    )
    elements.append(Paragraph(s2_text_pt2, dialogue_style))

    # Ablation Table in PDF
    ablation_data = [
        [Paragraph("<b>Removed Feature Group</b>", table_head), Paragraph("<b>CV Macro F1</b>", table_head), Paragraph("<b>Impact (&Delta; F1)</b>", table_head), Paragraph("<b>Key Insight</b>", table_head)],
        [Paragraph("None (Full Model Baseline)", table_text), Paragraph("<b>0.4741</b>", table_text), Paragraph("0.0000", table_text), Paragraph("Reference standard", table_text)],
        [Paragraph("Demographics (Gender, Background)", table_text), Paragraph("0.4789", table_text), Paragraph("<b>+0.0049</b>", table_text), Paragraph("<b>Fairness proof:</b> No demographic bias", table_text)],
        [Paragraph("Study Habits (Hours, Attendance)", table_text), Paragraph("0.4765", table_text), Paragraph("+0.0025", table_text), Paragraph("General habits do not decide specific careers", table_text)],
        [Paragraph("Practical Experience", table_text), Paragraph("0.4656", table_text), Paragraph("-0.0085", table_text), Paragraph("Projects assist fine-grained career separation", table_text)],
        [Paragraph("Academic Scores (Math, Science)", table_text), Paragraph("0.4309", table_text), Paragraph("-0.0432", table_text), Paragraph("Core subjects provide foundational filtering", table_text)],
        [Paragraph("<b>Skill Scores (Programming, Creative, Lead)</b>", table_text), Paragraph("<b>0.2434</b>", table_text), Paragraph("<b>-0.2307 (-23.1%)</b>", table_text), Paragraph("<b>CRITICAL DRIVER:</b> Defines 48% of system accuracy", table_text)],
    ]
    ablation_table = Table(ablation_data, colWidths=[150, 75, 75, 204])
    ablation_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B71C1C")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(ablation_table)
    elements.append(Spacer(1, 8))

    s2_text_pt3 = (
        "&ldquo;<i>Key Takeaway:</i> Removing skill scores collapsed model Macro F1 by <b>23.07%</b>! This proves our system relies on genuine "
        "aptitude rather than demographic shortcuts. Now, <b>[Speaker 3 Name]</b> will present our final test evaluation, explainability, and live software demo.&rdquo;"
    )
    elements.append(Paragraph(s2_text_pt3, dialogue_style))
    elements.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────
    # PART 3: SPEAKER 3
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("PART 3: TEST EVALUATION, SHAP EXPLAINABILITY &amp; LIVE DEMO", h1_style))
    elements.append(Paragraph("🎤 <b>Speaker 3 (Evaluation &amp; Deployment Lead)</b> — <i>Held-Out Test Results, SHAP, Live Flask Web App</i>", speaker_badge_3))

    s3_text = (
        "&ldquo;Thank you, [Speaker 2 Name]. Respected Examiner, I am <b>[Speaker 3 Name]</b>, and I will conclude with our final held-out test evaluation, "
        "model explainability, and our interactive software demonstration.<br/><br/>"
        "<b>Stage 7: Held-Out Test Evaluation (Single-Pass):</b><br/>"
        "Following Stage 7 of our rubric, we evaluated our best Optuna-tuned Random Forest model <b>exactly once</b> on our held-out test set of <b>400 students</b>.<br/>"
        "&nbsp;&nbsp;&bull; <b>Overall Test Accuracy:</b> <b>50.25%</b> (vs. 20% random guessing and 29% dummy baseline)<br/>"
        "&nbsp;&nbsp;&bull; <b>Macro F1-Score:</b> <b>0.4930</b> | <b>Weighted F1-Score:</b> <b>0.4997</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Macro Precision:</b> <b>50.79%</b> | <b>Macro Recall:</b> <b>48.71%</b><br/><br/>"
        "<b>Class-Wise Insights:</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Business / Management</b> achieved our highest precision of <b>63.16%</b> (F1: 0.58), driven by clean leadership &amp; communication separation.<br/>"
        "&nbsp;&nbsp;&bull; <b>Creative Arts / Design</b> achieved <b>54.69% recall</b> and <b>0.54 F1</b>.<br/>"
        "&nbsp;&nbsp;&bull; <b>Data Science &amp; Research</b> achieved <b>0.47</b> and <b>0.53 F1</b>.<br/>"
        "&nbsp;&nbsp;&bull; The primary confusion was between Software Engineering and Data Science, which share similar high math and coding profiles.<br/><br/>"
        "<b>Stage 8: Model Explainability with SHAP:</b><br/>"
        "In educational counseling, an algorithm cannot be an unaccountable 'black box'. We implemented <b>SHAP (SHapley Additive exPlanations)</b>.<br/>"
        "Our SHAP beeswarm and feature importance curves revealed that <code>programming_score</code>, <code>creativity_score</code>, <code>communication_score</code>, "
        "and <code>math_score</code> exert the highest magnitude Shapley values, transparently proving to students why a specific career was recommended.<br/><br/>"
        "<b>Interactive Live Demonstration:</b><br/>"
        "We packaged our pipeline into a responsive <b>Flask Web Application</b> and a <b>RESTful API</b>.<br/>"
        "<i>[Speaker 3 opens browser to http://127.0.0.1:5000 and conducts live demo]</i><br/>"
        "As you observe on the screen:<br/>"
        "1. We input student scores (e.g. Programming: 95, Math: 90, GPA: 3.8).<br/>"
        "2. Upon clicking <b>'Get Career Recommendation'</b>, Flask transforms the features through our saved <code>preprocessor.pkl</code>, queries <code>best_model_rf.pkl</code>, "
        "and renders the result: <b>'Data Science / AI'</b>.<br/>"
        "3. Crucially, the UI renders <b>live probability confidence bars</b> (e.g., Data Science: 59.2%, Research: 22.8%, Software Engineering: 13.2%). "
        "This gives counselors full probabilistic visibility rather than an opaque decision.<br/>"
        "4. Furthermore, our REST API endpoint at <code>/api/predict</code> allows university portals to query predictions programmatically.<br/><br/>"
        "In conclusion, our project demonstrates a rigorous, leakage-free, thoroughly tuned, and explainable Machine Learning solution. "
        "We are now eager to answer your questions. Thank you!&rdquo;"
    )
    elements.append(Paragraph(s3_text, dialogue_style))
    elements.append(Spacer(1, 14))

    # ─────────────────────────────────────────────────────────────
    # PART 4: VIVA VOCE CHEAT SHEET
    # ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("PART 4: VIVA VOCE &amp; EXAMINER Q&amp;A DEFENSE CHEAT SHEET", h1_style))
    elements.append(Paragraph("<i>Categorized by designated speaker for crisp, confident answers during external examination:</i>", stage_direction_style))
    elements.append(Spacer(1, 4))

    qa_list = [
        (
            "Q1: Why did you use Repeated Stratified K-Fold CV instead of a simple 70/30 split?",
            "Speaker 2",
            "A single split can yield misleadingly high or low scores due to a lucky or unlucky random partition. Stratified K-Fold ensures that every fold preserves identical class ratios to the original population. By repeating 5-Fold CV 3 times (15 total folds), we compute both a Mean and a Standard Deviation (e.g. 50.81% ± 2.85%), proving our model is robust and not overfitting."
        ),
        (
            "Q2: How exactly did you prevent Data Leakage?",
            "Speaker 1",
            "Data leakage occurs when test data characteristics (like mean, variance, or median) leak into the training process before model training. We prevented this by first isolating the 20% test set with seed 42. All preprocessing (median imputation, standard scaling, one-hot encoding) was bundled inside an sklearn ColumnTransformer fitted strictly on training folds and merely transformed on test sets."
        ),
        (
            "Q3: Isn't 50.25% test accuracy low compared to typical 90% claims?",
            "Speaker 3 or Speaker 2",
            "Not at all, Sir/Ma'am! Many 90% accuracy claims occur in binary classification (50% random chance) or suffer from data leakage. Our project is a 5-class multi-class problem where random guessing is only 20%, and the dummy baseline is 29.00%. Our model achieves 50.25% (over 2.5x random chance). Real-world student aptitudes naturally overlap between related fields, which is why our system outputs probabilistic confidence distributions."
        ),
        (
            "Q4: Why Optuna instead of manual tuning or standard GridSearchCV?",
            "Speaker 2",
            "GridSearchCV performs a brute-force sweep over predefined values, wasting compute evaluating bad combinations. Optuna uses Bayesian Optimization with Tree-structured Parzen Estimators (TPE). It builds a probability distribution of past trial results and strategically chooses hyperparameter values that are most likely to improve the objective metric (Macro F1)."
        ),
        (
            "Q5: What is an Ablation Study and what was your biggest insight?",
            "Speaker 2",
            "An ablation study removes one component at a time to measure its isolated impact. Our biggest discovery was that dropping Skill Scores (programming, creativity, leadership) caused the Macro F1 to crash by 23.07% (from 0.4741 to 0.2434). Conversely, dropping demographic variables had no negative impact (+0.0049), demonstrating that our system makes decisions based on genuine merit rather than demographic bias."
        ),
        (
            "Q6: What is SHAP and why did you include it in Stage 8?",
            "Speaker 3",
            "SHAP (SHapley Additive exPlanations) is based on cooperative game theory. It calculates the marginal contribution of each feature toward the final prediction. In student counseling, an AI model cannot be a black box; SHAP provides transparency by showing exactly which positive or negative scores pushed a student toward a particular recommendation."
        ),
        (
            "Q7: Why optimize for Macro F1 rather than overall Accuracy?",
            "Speaker 2",
            "Standard accuracy counts total correct predictions, which can mask terrible performance on minority classes. Macro F1 calculates the unweighted harmonic mean of Precision and Recall across all 5 classes individually. It forces the model to perform fairly and reliably across all career paths."
        ),
        (
            "Q8: How does the Flask web app connect to the trained model?",
            "Speaker 3",
            "During Stage 7, we serialized our fitted preprocessor.pkl and best_model_rf.pkl using Joblib. When the Flask server starts, it loads these into memory. When a user submits the web form, Flask converts the input into a single-row DataFrame, transforms it using preprocessor.transform(), runs model.predict_proba(), and dynamically renders the prediction and confidence meters in HTML."
        ),
    ]

    for q, speaker, ans in qa_list:
        elements.append(Paragraph(f"<b>{q}</b> <font color='#0D47A1'>[{speaker}]</font>", q_style))
        elements.append(Paragraph(f"<b>Answer:</b> {ans}", ans_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[PDF Generated] {PDF_PATH}")
    return PDF_PATH


if __name__ == "__main__":
    build_pdf()
