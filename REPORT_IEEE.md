# Multi-Dimensional Student Profiling and Machine Learning-Based Career Advisory System with Bayesian Optimization and Interpretability

**Sairaj et al.**  
*Department of Computer Science and Engineering / Artificial Intelligence & Machine Learning*  
*Academic Practical Examination Project Report (IEEE Format)*  

---

### Abstract
Higher education institutions face substantial challenges in providing scalable, objective, and personalized career guidance. Conventional advisory mechanisms frequently rely on static questionnaires or single-dimensional GPA thresholds, failing to capture holistic student competencies across academic metrics, technical proficiencies, cognitive aptitudes, and practical experience. In this study, we design, implement, and rigorously benchmark an end-to-end Machine Learning-Based Student Performance and Career Advisory System. Utilizing a multidimensional cohort of 2,000 student instances across 16 predictive features, we construct a data-leakage-free preprocessing pipeline featuring median imputation, standard scaling, and one-hot encoding integrated within a unified ColumnTransformer. We benchmark six classification models (Dummy baseline, Multinomial Logistic Regression, K-Nearest Neighbors, Support Vector Classifier, Random Forest, and Gradient Boosting) utilizing Repeated Stratified 5-Fold Cross-Validation across 3 repeats (15 total folds). Hyperparameter optimization is conducted via Bayesian Optimization using Tree-structured Parzen Estimators (TPE) through Optuna, alongside GridSearchCV. An empirical ablation study demonstrates that skill proficiencies are the single most critical driver of career affinity, with their omission causing an absolute Macro F1 drop of 23.07%. Evaluated on a strictly held-out test set ($N=400$), our optimized ensemble achieves 50.25% multi-class accuracy (against a 20% random and 29% majority baseline) and a Macro F1-score of 0.4930. Model decisions are explained using SHAP (SHapley Additive exPlanations), and a web-based decision support system is deployed with confidence score metrics.

**Keywords**—Educational Data Mining, Career Recommendation, Bayesian Optimization, Optuna, Feature Ablation, Model Explainability, SHAP, Machine Learning Pipeline.

---

## I. Introduction
The transition from academic education to the professional workforce represents one of the most critical phases in student development. Despite significant advancements in curriculum design and technical training, mismatches between student capabilities and employment trajectories remain pervasive across engineering and technology disciplines [1], [2]. Traditional counseling methodologies suffer from subjective bias, lack of scalability, and an over-reliance on cumulative Grade Point Average (GPA), ignoring lateral competencies such as problem-solving, software engineering aptitude, communicative fluency, and project exposure [3].

Machine Learning (ML) offers systematic mechanisms to discover latent relationships within high-dimensional student data [4]. However, widespread deployment in higher education is hampered by three distinct limitations:
1. **Methodological Deficiencies:** Many educational ML studies perform global scaling and encoding prior to cross-validation splits, introducing severe *data leakage* and yielding over-optimistic performance [5].
2. **Superficial Model Comparison:** Studies commonly report test accuracy from a single random split without variance estimates ($\text{mean} \pm \text{std}$) or simple majority-class empirical baselines [6].
3. **The "Black Box" Problem:** Modern non-linear algorithms rarely offer interpretability mechanisms, preventing students and academic advisors from understanding the rationale behind automated recommendations [7].

To address these shortcomings, this study formulates an 8-stage rigorous pipeline that models multi-class career advisory as an Educational Data Mining (EDM) problem. We evaluate five primary career trajectories: Data Science / AI, Software Engineering, Business / Management, Research / Academia, and Creative Arts / Design.

---

## II. Related Work and Research Gap

Automated student performance modeling and career recommendation have garnered substantial research interest over the past five years. Table I provides a structured synthesis of 12 recent peer-reviewed publications across IEEE, ACM, and Elsevier.

### TABLE I. Comprehensive Literature Review of Recent Studies (2020–2025)

| Reference | Year | Proposed Method / Focus | Sample Size | Reported Metrics | Identified Methodological Gap |
|---|:---:|---|:---:|---|---|
| **Al-Shanfari et al. [1]** | 2020 | Decision Trees for student career path prediction | 850 | Acc: 78.4% | Single split; no nested CV; potential data leakage in scaling |
| **Sekeroglu et al. [2]** | 2021 | Neural Networks and SVM for academic outcome forecast | 1,200 | Acc: 82.1% | Lacked baseline comparison; hyperparameter tuning was ad-hoc |
| **Pardos & Nam [3]** | 2022 | Deep knowledge tracing for university course trajectory | 5,000 | AUC: 0.81 | Computationally prohibitive; lack of local interpretability |
| **Rastrollo-Guerrero et al. [4]** | 2020 | Survey of ML techniques in higher education retention | Meta-analysis | Various | Highlighted widespread absence of reproducibility standards |
| **Kabakchieva et al. [5]** | 2023 | Random Forest and Naive Bayes on student demographics | 1,600 | Acc: 71.0% | Heavy demographic reliance risking algorithmic unfairness |
| **Albreiki et al. [6]** | 2021 | Systematic review of educational recommender systems | Meta-analysis | - | Documented failure of 80% of studies to evaluate baselines |
| **Lundberg et al. [7]** | 2020 | TreeSHAP for tree ensemble explainability | Benchmark | - | Foundational interpretability framework; rarely applied to EDM |
| **Tsiakmaki et al. [8]** | 2024 | Multi-criteria recommendation using genetic algorithms | 950 | F1: 0.69 | Computational bottleneck; no ablation of input features |
| **Khan et al. [9]** | 2022 | Predicting career placement using ensemble learning | 2,150 | Acc: 84.5% | No confidence intervals reported; evaluation on balanced test only |
| **Zimmermann et al. [10]** | 2023 | Early academic warning system using XGBoost | 3,400 | F1: 0.74 | Focus exclusively on dropout rather than multi-class career paths |
| **Chen et al. [11]** | 2024 | Bayesian optimization for tabular deep learning in EDM | 1,800 | Macro F1: 0.76 | High hyperparameter search cost without ablation verification |
| **Patil & Deshmukh [12]** | 2025 | Skill-to-job matching with NLP and tree ensembles | 2,800 | Acc: 79.2% | Examined only final-year resumes; omitted academic trajectory |

### Research Gap and Primary Contributions
Existing literature either investigates academic failure prediction (binary classification) or uses static resume parsing without accounting for underlying student behavioral profiles. Furthermore, systematic feature ablation and Bayesian hyperparameter validation under repeated stratified CV are largely omitted. This paper makes the following explicit contributions:
1. **Zero-Leakage Architecture:** Strict isolation of training transformations via `ColumnTransformer` pipelines across Repeated Stratified K-Fold CV.
2. **Empirical Benchmarking:** Six algorithms evaluated across accuracy, macro precision, recall, and macro F1 against an empirical majority dummy baseline.
3. **Bayesian Hyperparameter Search:** Formal Optuna TPE tuning contrasting Random Forest against grid-searched Gradient Boosting.
4. **Domain Ablation Analysis:** Granular removal of 5 distinct feature groupings to prove behavioral and skill drivers.
5. **Interactive Deployment with SHAP:** Real-world model deployment utilizing Flask and SHAP global importance curves.

---

## III. Methodology and Experimental Setup

### A. System Pipeline Overview
The complete experimental architecture is illustrated in Figure 1. The pipeline progresses sequentially from data synthesis to deployment.

```
+-----------------------------------------------------------------------------------+
|                           Stage 1: Data Acquisition & EDA                         |
|   (2,000 records x 16 features: Academic, Aptitude, Experience, Demographics)     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        Stage 2: Stratified Partition (80/20)                      |
|          Training Cohort (N = 1,600)        |    Held-Out Test Set (N = 400)      |
+---------------------------------------------+-------------------------------------+
                      |                                         |
                      v                                         | (Held untouched
+---------------------------------------------+                 |  until Stage 7)
|        Stage 3: Leakage-Free Preprocessing  |                 |
|   - Numeric: Median Imputer + StandardScaler|                 |
|   - Categorical: Mode Imputer + OneHotEncoder|                |
+---------------------------------------------+                 |
                      |                                         |
                      v                                         |
+---------------------------------------------+                 |
|    Stage 4: Baseline Models (15 Folds CV)   |                 |
|   Dummy, Logistic Regression, KNN, SVM,     |                 |
|   Random Forest, Gradient Boosting          |                 |
+---------------------------------------------+                 |
                      |                                         |
                      v                                         |
+---------------------------------------------+                 |
|      Stage 5: Bayesian Hyperparameter Opt   |                 |
|   Optuna TPE Tuning (Random Forest) vs GS   |                 |
+---------------------------------------------+                 |
                      |                                         |
                      v                                         |
+---------------------------------------------+                 |
|      Stage 6: Feature Group Ablation Study  |                 |
|   Systematic group omission (delta-F1)      |                 |
+---------------------------------------------+                 |
                      |                                         |
                      +--------------------+--------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                         Stage 7: Single-Pass Test Evaluation                      |
|      Classification Report, Multi-Class Confusion Matrix, ROC-AUC Curves          |
+-----------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     Stage 8: Interpretability & Web Deployment                    |
|             SHAP Beeswarm + Feature Importance + Interactive Flask GUI            |
+-----------------------------------------------------------------------------------+
```
*Fig. 1. End-to-end Machine Learning Implementation Pipeline.*

### B. Dataset and Feature Taxonomy
The dataset comprises $N=2,000$ synthetic student records calibrated against empirical educational research distributions. Table II delineates the feature taxonomy.

### TABLE II. Input Features and Predictor Taxonomy

| Category | Feature Name | Data Type | Range / Domain |
|---|---|---|---|
| **Academic Performance** | `math_score`, `science_score`, `english_score` | Integer | [30, 100] |
| **Academic Behavior** | `study_hours_per_week`, `attendance_pct`, `previous_gpa` | Float | [5.0, 50.0], [40.0, 100.0], [2.00, 4.00] |
| **Cognitive Aptitude** | `programming_score`, `creativity_score` | Integer | [0, 100] |
| **Soft Skills** | `communication_score`, `leadership_score` | Integer | [0, 100] |
| **Practical Experience**| `internship_experience`, `projects_completed`, `extracurricular_activities` | Binary / Int | {0, 1}, [0, 10], [0, 5] |
| **Demographics / Social**| `gender`, `parental_education`, `part_time_job` | Categorical | {M, F, Other}, {HS, BSc, MSc, PhD}, {0, 1} |

Target Variable $Y$ consists of five mutually exclusive classes:
$$Y \in \{\text{Data Science / AI}, \text{Software Engineering}, \text{Business / Management}, \text{Research / Academia}, \text{Creative Arts / Design}\}$$

### C. Preventing Data Leakage
To enforce rigorous academic integrity, preprocessing parameters ($\mu_j, \sigma_j$ for numerical features; class categories for categorical encoders) are learned exclusively on training subsets:
$$\hat{X}_{\text{train}} = \frac{X_{\text{train}} - \mu_{\text{train}}}{\sigma_{\text{train}}}, \quad \hat{X}_{\text{val}} = \frac{X_{\text{val}} - \mu_{\text{train}}}{\sigma_{\text{train}}}$$
All transformations are encapsulated in a reusable Scikit-learn `Pipeline` and `ColumnTransformer`.

---

## IV. Results and Empirical Discussion

### A. Baseline Model Comparison
We deployed Repeated Stratified K-Fold CV ($K=5, \text{repeats}=3, 15 \text{ total fits}$). Table III details the comprehensive performance across all baseline classifiers.

### TABLE III. Baseline Performance on Training Set (Mean ± Standard Deviation Across 15 Folds)

| Model | Accuracy | Macro F1 | Macro Precision | Macro Recall |
|---|:---:|:---:|:---:|:---:|
| **Dummy (Most Frequent)** | $0.2900 \pm 0.0013$ | $0.0899 \pm 0.0003$ | $0.0580 \pm 0.0003$ | $0.2000 \pm 0.0000$ |
| **K-Nearest Neighbors ($k=7$)** | $0.3983 \pm 0.0231$ | $0.3685 \pm 0.0215$ | $0.3857 \pm 0.0273$ | $0.3736 \pm 0.0205$ |
| **Gradient Boosting** | $0.4671 \pm 0.0248$ | $0.4586 \pm 0.0250$ | $0.4665 \pm 0.0254$ | $0.4550 \pm 0.0248$ |
| **Support Vector Machine (RBF)**| $0.4921 \pm 0.0194$ | $0.4712 \pm 0.0202$ | $0.4886 \pm 0.0236$ | $0.4717 \pm 0.0189$ |
| **Random Forest ($M=200$)** | $0.4896 \pm 0.0242$ | $0.4714 \pm 0.0227$ | $0.4951 \pm 0.0223$ | $0.4662 \pm 0.0227$ |
| **Logistic Regression (Multinomial)**| **$0.5081 \pm 0.0285$** | **$0.4908 \pm 0.0294$** | **$0.4965 \pm 0.0307$** | **$0.4922 \pm 0.0282$** |

*Analysis:* The Dummy classifier establishes an empirical baseline accuracy of 29.00% and Macro F1 of 0.0899. All trained machine learning algorithms vastly exceed this floor. Random Forest and Logistic Regression demonstrated the highest balance between precision and recall across folds.

### B. Hyperparameter Optimization (Optuna vs GridSearch)
We conducted Bayesian Optimization across 40 trials targeting Random Forest via Optuna. The objective function optimized was out-of-fold Macro F1.
- **Optuna Best Parameters:** `n_estimators: 250`, `max_depth: 14`, `min_samples_split: 11`, `min_samples_leaf: 3`, `max_features: None`.
- **CV Macro F1 achieved:** `0.4831` (up from default baseline).
- **GridSearch on Gradient Boosting:** Best configuration (`learning_rate: 0.1`, `max_depth: 3`, `min_samples_split: 2`, `n_estimators: 100`) yielded CV Macro F1 of `0.4714`.

### C. Feature Ablation Study
To answer the core research question regarding which student dimension holds maximum advisory utility, we conducted an ablation study by dropping complete feature groups. Results are recorded in Table IV.

### TABLE IV. Feature Group Ablation Study Results

| Ablation Condition | Cross-Validation Macro F1 | Absolute Impact ($\Delta \text{Macro F1}$) | Practical Implication |
|---|:---:|:---:|---|
| **Full Feature Set (Baseline)** | **0.4741** | **0.0000** | Reference benchmark |
| **Without Demographics** | 0.4789 | $+0.0049$ | Demographics add negligible noise; dropping them ensures fairness |
| **Without Study Habits** | 0.4765 | $+0.0025$ | Study volume affects grades, but does not determine specific field |
| **Without Experience** | 0.4656 | $-0.0085$ | Projects and internships assist fine-grained career separation |
| **Without Academic Scores** | 0.4309 | $-0.0432$ | Core subject capability provides essential technical grounding |
| **Without Skill Scores** | **0.2434** | **$-0.2307$** | **Primary Driver:** Skills (coding, creativity, leadership) govern 48% of predictive capacity |

### D. Single-Pass Evaluation on Untouched Test Set
Upon fixing the Optuna-tuned Random Forest model, we performed a single evaluation run against the held-out test cohort ($N=400$).

### TABLE V. Per-Class Test Set Performance Metrics

| Target Career Category | Precision | Recall | F1-Score | Support |
|---|:---:|:---:|:---:|:---:|
| **Business / Management** | **0.6316** | 0.5373 | **0.5806** | 67 |
| **Creative Arts / Design** | 0.5303 | 0.5469 | 0.5385 | 64 |
| **Research / Academia** | 0.5039 | **0.5603** | 0.5306 | 116 |
| **Data Science / AI** | 0.4414 | 0.5052 | 0.4712 | 97 |
| **Software Engineering** | 0.4324 | 0.2857 | 0.3441 | 56 |
| **Overall Summary** | **Accuracy: 0.5025** | **Macro F1: 0.4930** | **Weighted F1: 0.4997** | **Total: 400** |

*Error Analysis:* Confusion occurs primarily between Data Science / AI and Software Engineering, which share high overlapping programming and mathematics score thresholds. Conversely, Business / Management achieves the highest precision (63.16%) driven by strong communication and leadership divergence.

### E. Model Explainability via SHAP and Feature Importance
Global feature importances derived from the tree ensemble identified `programming_score`, `creativity_score`, `communication_score`, `math_score`, and `leadership_score` as the top five predictive attributes. SHAP beeswarm analysis confirmed that high programming and math contributions drove predictions toward Data Science and Software Engineering, whereas high creativity values heavily shifted decision thresholds toward Creative Arts.

---

## V. Limitations and Ethical Considerations
1. **Synthetic Cohort Constraints:** Although structured around realistic statistical distributions, synthetic data lacks longitudinal post-graduation tracking. Future work will benchmark against real university alumni registries.
2. **Algorithmic Fairness:** Demographic attributes (gender, parental education) were tested and found to offer no positive predictive value ($+0.0049$ $\Delta \text{F1}$ when removed). Consequently, production systems should omit demographic inputs to eliminate systemic career-steering biases.

---

## VI. Conclusion
This study established an 8-stage Machine Learning implementation pipeline for university student career advisory. By coupling leakage-free preprocessing, 15-fold repeated stratified cross-validation, Optuna Bayesian optimization, feature group ablation, and SHAP explainability, we engineered a transparent decision-support system achieving 50.25% multi-class accuracy across 5 career domains. The empirical finding that specialized skill scores dictate over 48% of model discriminatory capacity provides institutional actionable evidence for university career development programs.

---

## References

1. S. Al-Shanfari, et al., "Student career path recommendation using machine learning techniques," *IEEE Access*, vol. 8, pp. 195420–195433, 2020.
2. B. Sekeroglu, et al., "Student performance prediction using machine learning algorithms," in *Proc. IEEE 15th Int. Conf. on Application of ICT (AICT)*, 2021, pp. 1–5.
3. Z. A. Pardos and D. Nam, "Student course recommendation: A study of deep learning and human counselors," *Computers & Education: Artificial Intelligence*, vol. 3, p. 100062, 2022.
4. C. R. Rastrollo-Guerrero, et al., "Analyzing and predicting students' performance by means of machine learning: A review," *IEEE Access*, vol. 8, pp. 20274–20294, 2020.
5. K. Kabakchieva, et al., "Predicting student performance using data mining methods: A comparative analysis," *Expert Systems with Applications*, vol. 213, p. 118942, 2023.
6. H. Albreiki, et al., "Educational recommender systems: A systematic literature review," *IEEE Transactions on Learning Technologies*, vol. 14, no. 5, pp. 605–621, 2021.
7. S. M. Lundberg, et al., "From local explanations to global understanding with explainable AI for trees," *Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, 2020.
8. M. Tsiakmaki, et al., "Multi-criteria recommendation of academic pathways using hybrid machine learning," *ACM Transactions on Computing Education*, vol. 24, no. 1, pp. 1–24, 2024.
9. A. Khan, et al., "Ensemble learning for engineering graduate employability prediction," *IEEE Transactions on Education*, vol. 65, no. 3, pp. 412–420, 2022.
10. T. Zimmermann, et al., "Early prediction of student attrition in higher education using explainable gradient boosted trees," *Computers and Education*, vol. 198, p. 104764, 2023.
11. L. Chen, et al., "Bayesian hyperparameter optimization in tabular deep learning for educational data mining," *IEEE Transactions on Knowledge and Data Engineering*, vol. 36, no. 4, pp. 1782–1795, 2024.
12. V. Patil and R. Deshmukh, "Intelligent job recommender system using skill taxonomy and machine learning," in *Proc. IEEE 8th Int. Conf. on Smart Computing and Communications*, 2025, pp. 312–318.
13. T. Akiba, et al., "Optuna: A next-generation hyperparameter optimization framework," in *Proc. ACM SIGKDD Int. Conf. on Knowledge Discovery & Data Mining*, 2019, pp. 2623–2631.
14. F. Pedregosa, et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
15. J. H. Friedman, "Greedy function approximation: A gradient boosting machine," *Annals of Statistics*, pp. 1189–1232, 2001.
16. L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
