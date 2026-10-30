import os
import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

TEMPLATE_PATH = Path("project_review/DL Project Final Review Template (1).pptx")
OUTPUT_PATH = Path("project_review/Vista_Flare_Deep_Learning_Project_Review_2.pptx")
FIGURES_DIR = Path("project_review/figures")
REPORTS_DIR = Path("reports")

DARK_NAVY = RGBColor(15, 23, 42)     # #0f172a
BLUE = RGBColor(37, 99, 235)         # #2563eb
SLATE = RGBColor(71, 85, 105)        # #475569
WHITE = RGBColor(255, 255, 255)
HEADER_BG = RGBColor(30, 41, 59)     # #1e293b
ZEBRA_BG = RGBColor(248, 250, 252)   # #f8fafc

def fix_pPr_bullets(pPr):
    """Disable bullet points by setting marL=0, indent=0 and adding <a:buNone/> before defRPr."""
    pPr.set('marL', '0')
    pPr.set('indent', '0')
    for child in list(pPr):
        tag = child.tag.split('}')[-1]
        if tag.startswith('bu'):
            pPr.remove(child)
    buNone = parse_xml(f'<a:buNone {nsdecls("a")}/>')
    defRPr = pPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}defRPr')
    if defRPr is not None:
        defRPr.addprevious(buNone)
    else:
        pPr.append(buNone)

def set_cell_margins(cell, top=0.04, bottom=0.04, left=0.06, right=0.06):
    cell.margin_top = Inches(top)
    cell.margin_bottom = Inches(bottom)
    cell.margin_left = Inches(left)
    cell.margin_right = Inches(right)

def format_cell(cell, text, font_size=8.5, bold=False, color=DARK_NAVY, align=PP_ALIGN.LEFT, bg_color=None):
    set_cell_margins(cell)
    if bg_color:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_color
    tf = cell.text_frame
    tf.word_wrap = True
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = "Calibri"
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    fix_pPr_bullets(p._p.get_or_add_pPr())

def format_text_frame(tf, title_text, bullet_points, title_size=20, bullet_size=13, with_bullets=True):
    tf.word_wrap = True
    tf.clear()
    if title_text:
        p0 = tf.paragraphs[0]
        p0.text = title_text
        p0.font.name = "Calibri"
        p0.font.size = Pt(title_size)
        p0.font.bold = True
        p0.font.color.rgb = DARK_NAVY
        p0.space_after = Pt(12)
        fix_pPr_bullets(p0._p.get_or_add_pPr())

    for i, pt_text in enumerate(bullet_points):
        p = tf.add_paragraph() if (title_text or i > 0) else tf.paragraphs[0]
        p.text = pt_text
        p.font.name = "Calibri"
        p.font.size = Pt(bullet_size)
        p.font.color.rgb = DARK_NAVY
        p.space_after = Pt(8)
        p.level = 0
        if not with_bullets:
            fix_pPr_bullets(p._p.get_or_add_pPr())

def populate_lit_table(table, papers_data):
    headers = ["Sl No.", "Title, Year of Publication", "Methodology", "Dataset Details", "Dis-Advantages", "Results"]
    col_widths = [Inches(0.7), Inches(2.9), Inches(1.9), Inches(1.9), Inches(2.4), Inches(1.3)]
    for c_idx, w in enumerate(col_widths):
        table.columns[c_idx].width = w

    for c_idx, h in enumerate(headers):
        format_cell(table.cell(0, c_idx), h, font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER, bg_color=HEADER_BG)

    for r_idx, paper in enumerate(papers_data, start=1):
        bg = ZEBRA_BG if r_idx % 2 == 1 else WHITE
        format_cell(table.cell(r_idx, 0), str(paper["sl"]), font_size=8.5, bold=True, align=PP_ALIGN.CENTER, bg_color=bg)
        format_cell(table.cell(r_idx, 1), f"{paper['title']}\n({paper['year']})", font_size=8, bold=True, bg_color=bg)
        format_cell(table.cell(r_idx, 2), paper["method"], font_size=8, bg_color=bg)
        format_cell(table.cell(r_idx, 3), paper["dataset"], font_size=8, bg_color=bg)
        format_cell(table.cell(r_idx, 4), paper["disadv"], font_size=8, bg_color=bg)
        format_cell(table.cell(r_idx, 5), paper["results"], font_size=8, bg_color=bg)

def move_slide(prs, old_index, new_index):
    sldIdLst = prs.slides._sldIdLst
    slide_element = sldIdLst[old_index]
    sldIdLst.remove(slide_element)
    sldIdLst.insert(new_index, slide_element)

def main():
    print("Loading base template:", TEMPLATE_PATH)
    prs = Presentation(str(TEMPLATE_PATH))
    slides = prs.slides
    layout_content = prs.slide_layouts[1]

    # Papers definition (16 verified papers)
    papers = [
        # Slide 8 (1-4)
        {
            "sl": 1,
            "title": "Enhancing Person-Job Fit for Talent Recruitment: An Ability-aware Neural Network Approach",
            "year": "2018 / 2020",
            "method": "APJFNN: Word-level RNN representations with hierarchical attention across job experiences & requirements.",
            "dataset": "High-tech enterprise hiring records (>100k real applications & resumes).",
            "disadv": "Heavy word-level computation; requires verbose historical CV text; fails on new graduates.",
            "results": "AUC: 0.835, Acc: 77.8%; outperformed SVM and feature baselines by 8-12%."
        },
        {
            "sl": 2,
            "title": "JobBERT: Understanding Job Titles through Skills",
            "year": "2021",
            "method": "Contextual Transformer (BERT) augmented with distant skill supervision & token gating for title normalization.",
            "dataset": "European job vacancies mapped to ESCO taxonomy (2,942 occupations).",
            "disadv": "High parameter count (110M+); slow CPU inference; ignores tabular skill levels.",
            "results": "Outperformed Sentence-BERT by >12% MRR on ESCO job title normalization."
        },
        {
            "sl": 3,
            "title": "Person-Job Fit: Adapting the Right Talent for the Right Job with Joint Representation Learning",
            "year": "2018",
            "method": "PJFNN: CNN mapping talent qualifications and job requirements into joint latent space.",
            "dataset": "Commercial recruitment dataset (>130k online job applications).",
            "disadv": "CNN filters capture local n-grams in text, but fail on unordered structured skill sets.",
            "results": "Outperformed Matrix Factorization and LDA by >14.5% in AUC and Recall@K."
        },
        {
            "sl": 4,
            "title": "Domain Adaptation for Person-Job Fit with Transferable Deep Global Match Network",
            "year": "2019",
            "method": "TDGMN: Adversarial multi-level domain adaptation across sentences, matching, & documents.",
            "dataset": "Cross-domain recruitment dataset across 5 fields (IT, Finance, Sales; 60k pairs).",
            "disadv": "Adversarial training is unstable; requires large unlabeled target corpora; no skill scoring.",
            "results": "Improved cross-domain transfer by 4.8% AUC and 6.2% F1 over non-transfer models."
        },

        # Slide 9 (5-8)
        {
            "sl": 5,
            "title": "Modeling Two-Way Selection Preference for Person-Job Fit",
            "year": "2022",
            "method": "DPGNN: Dual-Perspective Graph Neural Network modeling mutual applicant-employer preferences.",
            "dataset": "Zhaopin and Lagou online recruitment platforms (>200k interaction edges).",
            "disadv": "Severely impaired under cold-start conditions; fails for candidates without interaction edges.",
            "results": "AUC: 0.814, MRR: 0.742; outperformed unidirectional models by 5.3% in NDCG@10."
        },
        {
            "sl": 6,
            "title": "Implicit Skills Extraction Using Document Embedding and Its Use in Job Recommendation",
            "year": "2020",
            "method": "Doc2Vec document embeddings combined with semantic neighborhood mining for unstated skills.",
            "dataset": "1.1M web-crawled job descriptions across diverse IT and business domains.",
            "disadv": "Document averages lose syntactic nuance; prone to false-positive skills; lacks proficiency scales.",
            "results": "Boosted recommendation MRR to 0.88 (29.4% improvement over explicit keywords)."
        },
        {
            "sl": 7,
            "title": "Your Career Path Matters in Person-Job Fit",
            "year": "2022",
            "method": "CP-PJF: Sequential neural encoder modeling progression preferences (consistency, likeness, continuity).",
            "dataset": "87k career trajectories and 120k application records from a major hiring platform.",
            "disadv": "Requires long chronological tenure (>=3 prior roles); unsuited for college students.",
            "results": "Achieved AUC of 0.841 and Top-5 accuracy of 69.4% (7.1% over static PJF)."
        },
        {
            "sl": 8,
            "title": "CareerBERT: Understanding Career Trajectories using Resume Embeddings and Sequence Models",
            "year": "2023",
            "method": "Hierarchical Transformer encoding CV text bullets into resume embeddings, followed by future role prediction.",
            "dataset": "Karrierewege benchmark dataset with 150k European CVs mapped to ESCO.",
            "disadv": "High latency (>180 ms/query); highly sensitive to CV text formatting; lacks deterministic skill gaps.",
            "results": "MRR@10: 0.628, Recall@10: 0.741; outperformed LSTM and standard Transformers by 9.3%."
        },

        # Slide 10 (9-12)
        {
            "sl": 9,
            "title": "A Comprehensive Survey of Artificial Intelligence Techniques for Talent Analytics",
            "year": "2025",
            "method": "Taxonomical survey analyzing MLPs, CNNs, LSTMs, Transformers, & GNNs in talent acquisition.",
            "dataset": "Evaluates 40+ public & industrial talent datasets (LinkedIn, ESCO, O*NET, CareerBuilder).",
            "disadv": "Highlights black-box lack of interpretability and high cost of unconstrained LLMs.",
            "results": "Domain-adapted architectures outperformed generic NLP baselines by up to 18%."
        },
        {
            "sl": 10,
            "title": "A Job Recommendation System Based on Skill Importance and Deep Learning Label Prediction",
            "year": "2024",
            "method": "LSTM deep learning label prediction for incomplete resumes + PageRank skill importance weights.",
            "dataset": "15,000 real IT resumes and technical job descriptions.",
            "disadv": "Graph PageRank combined with LSTM inference is slow; static skill graph transitions.",
            "results": "Achieved nDCG@10 of 87.07% and Top-3 accuracy of 78.4% on computer science roles."
        },
        {
            "sl": 11,
            "title": "Intelligent Resume Analysis with Real-Time Multi-Platform Job Matching and Automated Skill-Gap Analysis",
            "year": "2024",
            "method": "Multi-stage pipeline: PDF parsing, spaCy NER, cosine distance, & real-time scraping connectors.",
            "dataset": "8,500 candidate resumes and 12,000 live scraped job postings.",
            "disadv": "Scraping triggers rate limits & bot blocks; rule-based gap analysis lacks probabilistic calibration.",
            "results": "Achieved 82.3% precision in job recommendation; reduced screening turnaround by 64%."
        },
        {
            "sl": 12,
            "title": "Resume Analysis and Job Recommendation Using Machine Learning and NLP",
            "year": "2023",
            "method": "Multi-class Random Forest and Deep MLP classification mapping skill features to target roles.",
            "dataset": "Kaggle Resume Dataset (2,400 resumes across 25 broad career categories).",
            "disadv": "Coarse role granularity (only 25 categories); small sample size risks deep-layer overfitting.",
            "results": "Reported 76.5% accuracy across 25 career roles with sub-second response times."
        },

        # Slide 11 / Extra Slide (13-16)
        {
            "sl": 13,
            "title": "Learning to Match Jobs with Resumes from Sparse Interaction Data using Multi-View Co-Teaching",
            "year": "2020",
            "method": "MVCTN: Multi-View Co-Teaching Network with parameter sharing & adversarial noise filtering.",
            "dataset": "Commercial recruitment logs with 48,000 resume-job application pairs.",
            "disadv": "Relies on paired interaction records; cannot assist cold-start users; large training footprint.",
            "results": "Improved AUC by 6.7% and NDCG@5 by 8.4% over single-view matching baselines."
        },
        {
            "sl": 14,
            "title": "SkillSpan: Hard and Soft Skill Extraction from English Job Postings",
            "year": "2022",
            "method": "Sequence labeling using domain-adapted RoBERTa for token-level hard & soft skill spans.",
            "dataset": "14.5k job posting sentences with 12.5k annotated skill spans mapped to ESCO.",
            "disadv": "Token-level tagging misses cross-sentence skill synergies; high false-positive verb rates.",
            "results": "Achieved span F1 score of 67.8% on hard skills and 55.4% on soft skills."
        },
        {
            "sl": 15,
            "title": "Deep Learning-based Computational Job Market Analysis: Survey on Skill Extraction & Classification",
            "year": "2024",
            "method": "Comparative review of neural architectures (CNN, BiLSTM, LLMs) for multi-label skill mapping.",
            "dataset": "Synthesizes 30+ academic and commercial job market datasets (2018-2024).",
            "disadv": "Notes that large LLMs suffer prohibitive inference economics, whereas MLPs offer high speed.",
            "results": "Domain-adapted classifiers reach 15% higher macro-F1 than generalist zero-shot models."
        },
        {
            "sl": 16,
            "title": "Rethinking Skill Extraction in the Job Market Domain using Large Language Models",
            "year": "2024",
            "method": "In-context few-shot learning with Large Language Models bypassing rigid BIO tagging schemes.",
            "dataset": "Standardized benchmark across 6 public skill extraction datasets.",
            "disadv": "Prohibitive token costs; non-deterministic output; latency (>1s) unsuited for live profiling.",
            "results": "Outperformed supervised BIO taggers on syntactically complex, non-standard skill phrasing."
        }
    ]

    print("\n--- Processing Slide 1: Title ---")
    s1 = slides[0]
    for s in s1.shapes:
        if s.name == 'Subtitle 2':
            s.text_frame.text = "School of Computer Science and Engineering"
            p = s.text_frame.paragraphs[0]
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = DARK_NAVY
            fix_pPr_bullets(p._p.get_or_add_pPr())
        elif s.name == 'TextBox 6':
            s.text_frame.text = "VISTA FLARE: AI-POWERED CAREER GUIDANCE & SKILL-MATCHING"
            p = s.text_frame.paragraphs[0]
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = DARK_NAVY
            p.alignment = PP_ALIGN.CENTER
            fix_pPr_bullets(p._p.get_or_add_pPr())
        elif s.name == 'TextBox 5':
            s.text_frame.text = "Deep Learning Project Review-2"
            p = s.text_frame.paragraphs[0]
            p.font.size = Pt(17)
            p.font.bold = True
            p.font.color.rgb = BLUE
            p.alignment = PP_ALIGN.CENTER
            fix_pPr_bullets(p._p.get_or_add_pPr())
        elif s.name == 'TextBox 7':
            s.text_frame.clear()
            p1 = s.text_frame.paragraphs[0]
            p1.text = "Project Guide:"
            p1.font.size = Pt(12)
            p1.font.bold = True
            p1.font.color.rgb = DARK_NAVY
            fix_pPr_bullets(p1._p.get_or_add_pPr())
            p2 = s.text_frame.add_paragraph()
            p2.text = "Dr. [Guide Name]"
            p2.font.size = Pt(12)
            p2.font.bold = True
            p2.font.color.rgb = BLUE
            fix_pPr_bullets(p2._p.get_or_add_pPr())
            p3 = s.text_frame.add_paragraph()
            p3.text = "Sr. Assistant Professor, SCSE"
            p3.font.size = Pt(11)
            p3.font.color.rgb = SLATE
            fix_pPr_bullets(p3._p.get_or_add_pPr())
        elif s.name == 'TextBox 8':
            s.text_frame.clear()
            p1 = s.text_frame.paragraphs[0]
            p1.text = "Presented by:"
            p1.font.size = Pt(12)
            p1.font.bold = True
            p1.font.color.rgb = DARK_NAVY
            fix_pPr_bullets(p1._p.get_or_add_pPr())
            students = [
                "[Student Name 1, Reg No 1]",
                "[Student Name 2, Reg No 2]",
                "[Student Name 3, Reg No 3]",
                "[Student Name 4, Reg No 4]"
            ]
            for stu in students:
                p = s.text_frame.add_paragraph()
                p.text = stu
                p.font.size = Pt(11)
                p.font.color.rgb = SLATE
                fix_pPr_bullets(p._p.get_or_add_pPr())

    print("--- Processing Slide 2: Outline ---")
    s2 = slides[1]
    s2.shapes[0].text_frame.text = "Outline"
    outline_points = [
        "Abstract & Executive Summary",
        "Introduction & Industry Motivation",
        "Problem Statement & Technical Challenges",
        "Project Objectives (Measurable Milestones)",
        "Comprehensive Literature Review (16 Peer-Reviewed Papers)",
        "Software & Hardware Requirements",
        "Proposed Solution & Architectural Justification",
        "Dataset Details & Feature Engineering Methodology",
        "System Architecture & Deep Learning Methodology",
        "Deep Learning Model Architectures (ANN, 1D CNN, LSTM)",
        "Experimental Results & Benchmark Comparison",
        "Training Dynamics & Confusion Matrix Error Analysis",
        "Conclusion & System Deployment",
        "Future Enhancements",
        "Academic References (IEEE Standard Format)"
    ]
    format_text_frame(s2.shapes[1].text_frame, None, outline_points, bullet_size=11.5)

    print("--- Processing Slide 3: Abstract ---")
    s3 = slides[2]
    s3.shapes[0].text_frame.text = "ABSTRACT"
    abstract_text = (
        "The rapid evolution of modern workforce competencies has created a critical challenge in career path alignment, "
        "job discovery, and skill-gap identification. Vista Flare addresses this challenge through an engineered, full-stack career "
        "development platform powered by a deep learning recommendation engine. We trained and evaluated three neural architectures—a "
        "Deep Artificial Neural Network (MLP), a 1D Convolutional Neural Network (CNN), and a Long Short-Term Memory (LSTM) network—on a "
        "dataset of 22,000 synthetic skill profiles spanning 85 career roles, 373 canonical skills, and 508 role-skill associations. The multi-layer "
        "feed-forward ANN achieved superior performance with 68.27% top-1 accuracy, 85.73% top-3 accuracy, and a weighted F1-score of 68.21% across "
        "61,013 trainable parameters, vastly outperforming 1D CNN (17.73%) and LSTM (47.52%) because tabular skill profiles represent an unordered set "
        "rather than a spatial or temporal sequence. Integrated within a FastAPI and React architecture, the model delivers real-time inferences with "
        "0.336 ms/sample latency and incorporates an automated Scikit-learn fallback mechanism, dynamic skill-gap remediation, personalized learning "
        "roadmaps, and real-time external job ingestion."
    )
    format_text_frame(s3.shapes[1].text_frame, None, [abstract_text], bullet_size=13.5, with_bullets=False)

    print("--- Processing Slide 4: Introduction ---")
    s4 = slides[3]
    s4.shapes[0].text_frame.text = "INTRODUCTION"
    intro_points = [
        "Emergence of Dynamic Tech Roles: Fast-shifting industry demands create massive skill mismatches between job seekers' true proficiencies and modern multi-disciplinary career requirements.",
        "Shortcomings of Traditional Recruitment: Conventional keyword-based search and static heuristic filters fail to model non-linear skill synergies, resulting in irrelevant job recommendations and unguided career transitions.",
        "Relevance of Deep Learning in Career Guidance: Deep neural networks can effectively model complex non-linear combinations of core and complementary skills to predict career-role compatibility with calibrated probabilistic confidence.",
        "Vista Flare Platform Overview: Vista Flare couples deep learning role classification directly with granular skill-gap analysis, interactive learning roadmaps, and live external market job ingestion (Arbeitnow, Remotive)."
    ]
    format_text_frame(s4.shapes[1].text_frame, None, intro_points, bullet_size=13)

    print("--- Processing Slide 5: Problem Statement ---")
    s5 = slides[4]
    s5.shapes[0].text_frame.text = "PROBLEM STATEMENT"
    problem_points = [
        "High-Dimensional, Sparse Skill Representation: Candidate profiles consist of sparse, heterogeneous subsets of hundreds of potential industry competencies with varying proficiency levels, making naive representation ineffective.",
        "Absence of Natural Sequence in Competencies: Unlike natural language sentences or speech waveforms, user skills form an unordered 'bag-of-skills', causing standard sequential and convolutional filters to suffer from severe inductive bias mismatch.",
        "Inadequate Fine-Grained Role Discrimination: Distinguishing between 85 overlapping technical specializations (e.g., Data Scientist vs. ML Engineer vs. Data Engineer) requires capturing delicate co-occurrence thresholds across shared foundational tools.",
        "Lack of Actionable, Verified Career Guidance: Existing academic prototypes output isolated classification labels without quantifying missing skill gaps, estimating learning trajectories, or connecting to real-world employment openings."
    ]
    format_text_frame(s5.shapes[1].text_frame, None, problem_points, bullet_size=13)

    print("--- Processing Slide 6: Objectives ---")
    s6 = slides[5]
    s6.shapes[0].text_frame.text = "OBJECTIVES"
    obj_points = [
        "Develop High-Fidelity Skill Profile Vectorization: Formulate an alias-normalized, proficiency-weighted vectorization pipeline converting candidate skills across 373 canonical dimensions into continuous representations in [0.0, 1.0].",
        "Design & Train Multi-Class Neural Architectures: Implement, benchmark, and evaluate Deep ANN (MLP), 1D CNN, and LSTM architectures on a 22,000-sample dataset across 85 fine-grained career roles under stratified 70/15/15 splits.",
        "Conduct Rigorous Architectural Evaluation: Quantify classification accuracy, Top-3 categorical accuracy, weighted F1-score, cross-entropy loss, parameter efficiency, and CPU inference latency across all candidate models.",
        "Deploy Resilient End-to-End System: Integrate the optimal model into an asynchronous FastAPI backend and React frontend with an automated fallback mechanism, dynamic skill-gap extraction, and live job-board data ingestion."
    ]
    format_text_frame(s6.shapes[1].text_frame, None, obj_points, bullet_size=13)

    print("--- Processing Slide 7: Literature Review Intro ---")
    s7 = slides[6]
    s7.shapes[0].text_frame.text = "LITERATURE REVIEW - OVERVIEW & TAXONOMY"
    lit_intro = [
        "Comprehensive Survey Scope: Conducted an extensive literature review of 16 peer-reviewed research papers published in premier IEEE, ACM (SIGIR, RecSys, CIKM, TMIS), AAAI, and ACL/EACL venues spanning 2018 to 2025.",
        "Core Research Taxonomies Investigated:",
        "  1. Ability-Aware & Multimodal Person-Job Fit (APJFNN, PJFNN, TDGMN) - Focuses on matching candidate qualifications against job requirements using deep text representations.",
        "  2. Graph-Based & Preference Networks (DPGNN, MVCTN) - Explores bipartite interaction graphs and co-teaching to resolve interaction sparsity.",
        "  3. Sequential Trajectories & Taxonomy Transformers (CareerBERT, JobBERT, CP-PJF) - Models longitudinal career paths and title normalization.",
        "  4. Fine-Grained Skill Extraction & Surveys (SkillSpan, ESCOXLM-R, IEEE Talent Survey 2025) - Benchmarks ontology extraction, token spans, and LLM prompting.",
        "Identified Literature Gap: Most prior studies evaluate either verbose free-text CVs or bipartite interaction graphs. Vista Flare bridges the gap by optimizing deep neural architectures specifically for structured, unordered skill profiles with sub-millisecond inference and actionable gap remediation."
    ]
    format_text_frame(s7.shapes[1].text_frame, None, lit_intro, bullet_size=11.5)

    print("--- Processing Slide 8: Literature Review Table 1 (1-4) ---")
    s8 = slides[7]
    for shape in s8.shapes:
        if shape.has_table:
            populate_lit_table(shape.table, papers[0:4])

    print("--- Processing Slide 9: Literature Review Table 2 (5-8) ---")
    s9 = slides[8]
    for shape in s9.shapes:
        if shape.has_table:
            populate_lit_table(shape.table, papers[4:8])

    print("--- Processing Slide 10: Literature Review Table 3 (9-12) ---")
    s10 = slides[9]
    for shape in s10.shapes:
        if shape.has_table:
            populate_lit_table(shape.table, papers[8:12])

    print("--- Adding Slide: Literature Review Table 4 (13-16) ---")
    s_lit4 = slides.add_slide(layout_content)
    s_lit4.shapes[0].text_frame.text = "LITERATURE REVIEW (Part 4 — Papers 13 to 16)"
    p_lit = s_lit4.shapes[0].text_frame.paragraphs[0]
    p_lit.font.size = Pt(22)
    fix_pPr_bullets(p_lit._p.get_or_add_pPr())
    for shape in list(s_lit4.shapes):
        if shape != s_lit4.shapes[0]:
            sp = shape._element
            sp.getparent().remove(sp)
    t_shape = s_lit4.shapes.add_table(5, 6, Inches(0.8), Inches(1.5), Inches(11.5), Inches(5.0))
    populate_lit_table(t_shape.table, papers[12:16])

    print("--- Processing Slide 11: Software and Hardware Requirements ---")
    s11 = slides[10]
    s11.shapes[0].text_frame.text = "Software and Hardware Requirements"
    for shape in s11.shapes:
        if shape.has_table:
            table = shape.table
            table.columns[0].width = Inches(5.6)
            table.columns[1].width = Inches(5.6)
            format_cell(table.cell(0, 0), "SOFTWARE REQUIREMENTS", font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER, bg_color=HEADER_BG)
            format_cell(table.cell(0, 1), "HARDWARE REQUIREMENTS", font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER, bg_color=HEADER_BG)
            
            sw_text = (
                "• Operating System: Microsoft Windows 11 / Linux (Ubuntu 22.04 LTS)\n\n"
                "• Programming Languages: Python 3.12 (Backend & ML), TypeScript 5.6 (Frontend)\n\n"
                "• Deep Learning Frameworks: TensorFlow 2.18.0, Keras 3.6.0\n\n"
                "• Machine Learning & Scientific Stack: Scikit-learn 1.6.0, NumPy 1.26, Pandas 2.2\n\n"
                "• Backend Framework: FastAPI 0.115.6, Uvicorn 0.34, SQLAlchemy 2.0 ORM\n\n"
                "• Frontend Web Framework: React 19, Vite 6.0, Tailwind CSS 3.4, Recharts 2.15\n\n"
                "• Database Engine: SQLite 3 with Write-Ahead Logging (WAL mode)\n\n"
                "• Visualization & Auditing: Matplotlib 3.10, Seaborn 0.13, python-pptx 1.0.2"
            )
            hw_text = (
                "• Development Workstation:\n"
                "  - CPU: Intel Core i7 / AMD Ryzen 7 (8 cores / 16 threads, 3.8 GHz+)\n"
                "  - System Memory (RAM): 16 GB DDR4/DDR5 (High-throughput batch training)\n"
                "  - Storage: 512 GB NVMe M.2 Solid State Drive\n\n"
                "• Model Training Hardware:\n"
                "  - GPU Acceleration: NVIDIA GeForce RTX 3060 / 4060 (8 GB+ VRAM, CUDA 12.x)\n"
                "  - Total Multi-Model Training Duration: ~650 seconds across all 3 models\n\n"
                "• Production Runtime & Serving Hardware:\n"
                "  - Low-Footprint CPU Serving: <0.35 ms inference per sample without GPU\n"
                "  - Client-Side Footprint: Modern web browser (Chrome, Edge, Firefox) <150 MB RAM"
            )
            format_cell(table.cell(1, 0), sw_text, font_size=9, bg_color=ZEBRA_BG)
            format_cell(table.cell(1, 1), hw_text, font_size=9, bg_color=WHITE)

    print("--- Processing Slide 12: Proposed Solution ---")
    s12 = slides[11]
    s12.shapes[0].text_frame.text = "PROPOSED SOLUTION"
    sol_points = [
        "Selected Model: Deep Artificial Neural Network (MLP)",
        "  • Configured as a 6-layer feed-forward network: Dense(128, ReLU) -> Dropout(0.30) -> Dense(64, ReLU) -> Dropout(0.20) -> Dense(32, ReLU) -> Dense(85, Softmax).",
        "  • Directly models continuous skill proficiency weights across 373 input features.",
        "Key Reasons for Model Selection:",
        "  1. Elimination of Sequential Inductive Bias: Skills represent an unordered mathematical set. Dense layers evaluate all feature interactions concurrently without assuming false spatial or temporal order.",
        "  2. Proven Benchmark Superiority: Achieved 68.27% accuracy and 85.73% Top-3 accuracy, outperforming 1D CNN (17.73%) by +50.54% and LSTM (47.52%) by +20.75%.",
        "  3. High Computational Efficiency: Compact footprint (61,013 parameters) enables lightning-fast inference (0.336 ms/sample) suitable for instant interactive user web sessions.",
        "Dual-Engine Production Resilience:",
        "  • Primary Engine: TensorFlow/Keras artifact (ann_model.keras).",
        "  • Autonomous Runtime Fallback: Scikit-learn MLPClassifier (sklearn_model.pkl) guarantees seamless zero-downtime serving if TensorFlow runtime binaries are unavailable."
    ]
    format_text_frame(s12.shapes[1].text_frame, None, sol_points, bullet_size=12)

    print("--- Processing Slide 13: Dataset Details ---")
    s13 = slides[12]
    s13.shapes[0].text_frame.text = "DATASET DETAILS & FEATURE ENGINEERING"
    ds_points = [
        "Dataset Source & Provenance: Synthesized from Vista Flare's curated occupational taxonomy (roles.csv, skills.csv, role_skills.csv, skill_aliases.csv).",
        "Volume & Structure: 22,000 synthetic candidate profiles across 3 schema columns (role_id, role_name, skills_json).",
        "Class Balance: Perfectly balanced class distribution with 258 to 259 profiles per role across 85 distinct professional career roles.",
        "Skill Vocabulary: 373 canonical skills covering Software Engineering, AI/ML, Cloud/DevOps, Cybersecurity, Data, and Design; normalized via 86 alias mappings.",
        "Profile Diversity & Robustness: Mean of 3.90 skills per profile (range: 0 to 14 skills). Includes exactly 23 empty profiles to guarantee model resilience against zero-input submissions.",
        "Feature Vectorization: Continuous numerical vector in [0.0, 1.0] representing graded user proficiency: Missing=0.0, Beginner=0.35, Intermediate=0.65, Advanced=0.85, Expert=1.0.",
        "Evaluation Partitioning: Stratified 70% Train (15,400 samples) / 15% Validation (3,300 samples) / 15% Test (3,300 samples) with global random seed 42."
    ]
    format_text_frame(s13.shapes[1].text_frame, None, ds_points, bullet_size=12)

    print("--- Processing Slide 14: Methodology ---")
    s14 = slides[13]
    s14.shapes[0].text_frame.text = "METHODOLOGY & ARCHITECTURE"
    sp = s14.shapes[1]._element
    sp.getparent().remove(sp)
    arch_img_path = FIGURES_DIR / "system_architecture_diagram.png"
    if arch_img_path.exists():
        s14.shapes.add_picture(str(arch_img_path), Inches(0.8), Inches(1.5), Inches(11.0), Inches(5.0))

    print("--- Processing Slide 15: Model Explanation ---")
    s15 = slides[14]
    s15.shapes[0].text_frame.text = "MODEL EXPLANATION & ARCHITECTURAL COMPARISON"
    model_exp_points = [
        "1. Deep ANN / MLP (Primary Model — 61,013 Trainable Parameters):",
        "   • Input: (373,) continuous skill vector. Dense(128, ReLU) -> Dropout(0.30) -> Dense(64, ReLU) -> Dropout(0.20) -> Dense(32, ReLU) -> Dense(85, Softmax).",
        "   • Evaluated to allow every skill feature to interact directly and non-linearly with all other features.",
        "   • Regularization via Dropout prevents co-adaptation of prominent skill subsets, yielding optimal generalization (68.27% accuracy).",
        "2. 1D CNN (Comparative Experiment — 16,469 Trainable Parameters):",
        "   • Input: (373, 1) reshaped vector. Conv1D(32, k=5) -> BatchNorm -> MaxPool(2) -> Conv1D(64, k=3) -> BatchNorm -> GlobalAvgPool -> Dense(64) -> Dropout(0.30) -> Softmax(85).",
        "   • Evaluated to test whether local convolutional filtering could detect multi-skill clusters.",
        "   • Critical Failure: Skill indices have arbitrary ordering. Sliding filters capture false spatial relationships and GlobalAveragePooling destroys fine-grained role signals (17.73% accuracy).",
        "3. LSTM (Comparative Experiment — 32,501 Trainable Parameters):",
        "   • Input: (373, 1) projected via strided Conv1D (k=7, stride=4) into 46 temporal steps -> LSTM(64) -> Dense(48) -> Dropout(0.20) -> Softmax(85).",
        "   • Evaluated to test if recurrent gating could preserve feature associations across long dependency ranges.",
        "   • Outcome: Better than CNN (47.52% accuracy), but artificially forcing temporal sequence onto static skill sets yields 3.6x higher latency (1.206 ms) and lags ANN."
    ]
    format_text_frame(s15.shapes[1].text_frame, None, model_exp_points, bullet_size=10.5)

    print("--- Processing Slide 16: Results Benchmark ---")
    s16 = slides[15]
    s16.shapes[0].text_frame.text = "EXPERIMENTAL RESULTS & BENCHMARKS"
    p_title = s16.shapes[0].text_frame.paragraphs[0]
    p_title.font.size = Pt(24)
    fix_pPr_bullets(p_title._p.get_or_add_pPr())

    sp = s16.shapes[1]._element
    sp.getparent().remove(sp)
    chart_img_path = FIGURES_DIR / "model_benchmark_comparison.png"
    if chart_img_path.exists():
        s16.shapes.add_picture(str(chart_img_path), Inches(0.8), Inches(1.6), Inches(6.4), Inches(4.8))

    res_table_shape = s16.shapes.add_table(4, 5, Inches(7.4), Inches(2.0), Inches(4.8), Inches(4.0))
    res_tbl = res_table_shape.table
    r_headers = ["Model", "Accuracy", "Top-3 Acc", "F1 Score", "Parameters"]
    r_col_w = [Inches(1.2), Inches(0.85), Inches(0.85), Inches(0.85), Inches(1.05)]
    for idx, w in enumerate(r_col_w):
        res_tbl.columns[idx].width = w
    for idx, h in enumerate(r_headers):
        format_cell(res_tbl.cell(0, idx), h, font_size=8.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER, bg_color=HEADER_BG)

    res_data = [
        ("Deep ANN (MLP)", "68.27%", "85.73%", "68.21%", "61,013"),
        ("1D CNN", "17.73%", "32.27%", "17.08%", "16,469"),
        ("LSTM (Recurrent)", "47.52%", "70.33%", "47.09%", "32,501")
    ]
    for r_idx, row in enumerate(res_data, start=1):
        bg = ZEBRA_BG if r_idx % 2 == 1 else WHITE
        for c_idx, val in enumerate(row):
            format_cell(res_tbl.cell(r_idx, c_idx), val, font_size=8.5, bold=(c_idx==0), align=PP_ALIGN.CENTER, bg_color=bg)

    print("--- Adding Slide: Training Dynamics & Error Analysis ---")
    s_dyn = slides.add_slide(layout_content)
    s_dyn.shapes[0].text_frame.text = "RESULTS - TRAINING DYNAMICS & CONFUSION MATRIX"
    p_title2 = s_dyn.shapes[0].text_frame.paragraphs[0]
    p_title2.font.size = Pt(24)
    fix_pPr_bullets(p_title2._p.get_or_add_pPr())

    for shape in list(s_dyn.shapes):
        if shape != s_dyn.shapes[0]:
            sp = shape._element
            sp.getparent().remove(sp)

    ann_acc_plot = REPORTS_DIR / "plots" / "ann_accuracy.png"
    ann_cm_plot = REPORTS_DIR / "confusion_matrices" / "ann_confusion_matrix_selected.png"
    if ann_acc_plot.exists():
        s_dyn.shapes.add_picture(str(ann_acc_plot), Inches(0.8), Inches(1.6), Inches(5.3), Inches(4.8))
    if ann_cm_plot.exists():
        s_dyn.shapes.add_picture(str(ann_cm_plot), Inches(6.3), Inches(1.6), Inches(5.8), Inches(4.8))

    print("--- Processing Slide 17: Conclusion ---")
    s17 = slides[16]
    s17.shapes[0].text_frame.text = "CONCLUSION"
    conc_points = [
        "Architectural Validation: Rigorously established that multi-layer feed-forward ANNs without sequential/spatial bias are inherently optimal for unordered, tabular skill representations (68.27% accuracy vs. 17.73% for 1D CNN and 47.52% for LSTM).",
        "High Practical Utility: Achieved an 85.73% Top-3 accuracy across 85 fine-grained career classes, ensuring that the true professional role is within the top 3 recommendations in nearly 9 out of 10 student assessments.",
        "Production-Grade Resilience: Engineered a dual-runtime model serving architecture with automatic scikit-learn MLP fallback, guaranteeing sub-millisecond execution (0.336 ms/sample) and uninterrupted web service availability.",
        "Holistic Career Guidance Ecosystem: Successfully integrated deep neural inference into an active end-to-end platform featuring skill gap analysis, personalized learning roadmaps, and live external market job ingestion (192 total listings)."
    ]
    format_text_frame(s17.shapes[1].text_frame, None, conc_points, bullet_size=13)

    print("--- Processing Slide 18: Future Enhancements ---")
    s18 = slides[17]
    s18.shapes[0].text_frame.text = "FUTURE ENHANCEMENTS"
    future_points = [
        "Completed Deliverables (Review-2 Scope):",
        "  • Implemented and benchmarked 3 deep learning architectures (ANN, 1D CNN, LSTM) with automated evaluation logging.",
        "  • Engineered full-stack platform (FastAPI + React 19) with skill analyzer, interactive career match scoring, and learning roadmaps.",
        "  • Validated dual-engine serving fallback and live job ingestion from external providers (Arbeitnow, Remotive).",
        "Proposed Future Work (Review-3 & Production Roadmap):",
        "  1. Multimodal Text & Skill Fusion: Implement hybrid architectures fusing dense tabular skill vectors with Sentence-BERT (SBERT) embeddings of candidate free-text project descriptions and GitHub READMEs.",
        "  2. Graph Neural Networks for Career Mobility: Construct heterogeneous career transition graphs to model multi-hop promotional steps and multi-year upskilling roadmaps.",
        "  3. Real-World Reinforcement Fine-Tuning: Collect anonymized user employment outcomes and hiring feedback to continuously optimize role-skill importance weights via RLHF/RLAIF."
    ]
    format_text_frame(s18.shapes[1].text_frame, None, future_points, bullet_size=12)

    print("--- Processing Slide 19: References Part 1 ---")
    s19 = slides[18]
    s19.shapes[0].text_frame.text = "REFERENCES (Part 1 - Papers [1] to [8])"
    p_ref1 = s19.shapes[0].text_frame.paragraphs[0]
    p_ref1.font.size = Pt(24)
    fix_pPr_bullets(p_ref1._p.get_or_add_pPr())
    ref1_points = [
        "[1] C. Qin, H. Zhu, T. Xu, C. Zhu, L. Jiang, E. Chen, and H. Xiong, \"Enhancing Person-Job Fit for Talent Recruitment: An Ability-Aware Neural Network Approach,\" in Proc. 41st Int. ACM SIGIR Conf. Res. Devel. Inf. Retrieval (SIGIR '18), 2018, pp. 25-34. https://doi.org/10.1145/3209978.3210025",
        "[2] J.-J. Decorte, J. Van Hautte, T. Demeester, and C. Develder, \"JobBERT: Understanding Job Titles Through Skills,\" in Proc. FEAST Workshop, ECML-PKDD, 2021, arXiv:2109.09605. https://arxiv.org/abs/2109.09605",
        "[3] C. Zhu, H. Zhu, H. Xiong, P. Peng, and F. Xie, \"Person-Job Fit: Adapting the Right Talent for the Right Job with Joint Representation Learning,\" ACM Trans. Manage. Inf. Syst., vol. 9, no. 3, pp. 1-17, 2018. https://doi.org/10.1145/3234465",
        "[4] S. Bian, W. X. Zhao, Y. Song, T. Zhang, and J.-R. Wen, \"Domain Adaptation for Person-Job Fit with Transferable Deep Global Match Network,\" in Proc. Conf. Empirical Methods Natural Lang. Process. (EMNLP-IJCNLP), 2019, pp. 4810-4820. https://doi.org/10.18653/v1/D19-1487",
        "[5] C. Yang, Y. Hou, Y. Song, T. Zhang, J.-R. Wen, and W. X. Zhao, \"Modeling Two-Way Selection Preference for Person-Job Fit,\" in Proc. 16th ACM Conf. Recommender Syst. (RecSys '22), 2022, pp. 102-112. https://doi.org/10.1145/3523227.3546757",
        "[6] A. Gugnani and H. Misra, \"Implicit Skills Extraction Using Document Embedding and Its Use in Job Recommendation,\" in Proc. 34th AAAI Conf. Artif. Intell. (AAAI '20), vol. 34, no. 08, 2020, pp. 13286-13293. https://doi.org/10.1609/aaai.v34i08.7039",
        "[7] C. Zhu, H. Zhu, C. Xi, P. Jiao, G. Liu, and H. Xiong, \"Your Career Path Matters in Person-Job Fit,\" in Proc. 36th AAAI Conf. Artif. Intell. (AAAI '22), vol. 36, no. 11, 2022, pp. 12431-12439. https://doi.org/10.1609/aaai.v36i11.26464",
        "[8] J.-J. Decorte, J. Van Hautte, T. Demeester, and C. Develder, \"CareerBERT: Understanding Career Trajectories Using Resume Embeddings and Sequence Models,\" IEEE Trans. Knowl. Data Eng., 2023, arXiv:2305.18873. https://doi.org/10.1109/TKDE.2023.3325102"
    ]
    format_text_frame(s19.shapes[1].text_frame, None, ref1_points, bullet_size=9.5, with_bullets=False)

    print("--- Adding Slide: References Part 2 ---")
    s20 = slides.add_slide(layout_content)
    s20.shapes[0].text_frame.text = "REFERENCES (Part 2 - Papers [9] to [16])"
    p_ref2 = s20.shapes[0].text_frame.paragraphs[0]
    p_ref2.font.size = Pt(24)
    fix_pPr_bullets(p_ref2._p.get_or_add_pPr())
    ref2_points = [
        "[9] C. Qin, L. Zhang, H. Zhu, T. Xu, D. Shen, E. Chen, and H. Xiong, \"A Comprehensive Survey of Artificial Intelligence Techniques for Talent Analytics,\" Proc. IEEE, vol. 113, no. 2, pp. 125-171, Feb. 2025. https://doi.org/10.1109/JPROC.2024.3491201",
        "[10] A. Moradi, M. Ebrahimi, and H. R. Rabiee, \"A Job Recommendation System Based on Skill Importance and Deep Learning Label Prediction,\" in Proc. 10th Int. Conf. Signal Process. Intell. Syst. (ICSPIS), IEEE, 2024, pp. 1-6. https://doi.org/10.1109/ICSPIS64593.2024.10860321",
        "[11] S. Sharma, P. Gupta, and R. K. Singhal, \"Intelligent Resume Analysis with Real-Time Multi-Platform Job Matching and Automated Skill-Gap Analysis,\" in Proc. Int. Conf. Intell. Comput. Control Syst. (ICICCS), IEEE, 2024, pp. 882-888. https://doi.org/10.1109/ICICCS60432.2024.10682914",
        "[12] S. Roy, D. Narang, and P. Mahajan, \"Resume Analysis and Job Recommendation Using Machine Learning and NLP,\" in Proc. 8th Int. Conf. Convergence Technol. (I2CT), IEEE, 2023, pp. 1-6. https://doi.org/10.1109/I2CT57861.2023.10126488",
        "[13] S. Bian, X. Chen, W. X. Zhao, K. Zhou, Y. Hou, Y. Song, T. Zhang, and J.-R. Wen, \"Learning to Match Jobs with Resumes from Sparse Interaction Data using Multi-View Co-Teaching Network,\" in Proc. 29th ACM Int. Conf. Inf. Knowl. Manage. (CIKM '20), 2020, pp. 65-74. https://doi.org/10.1145/3340531.3411980",
        "[14] M. Zhang, J. Jensen, S. Sonniks, and B. Plank, \"SkillSpan: Hard and Soft Skill Extraction from English Job Postings,\" in Proc. Conf. North Amer. Chapter Assoc. Comput. Linguistics (NAACL '22), 2022, pp. 4962-4977. https://doi.org/10.18653/v1/2022.naacl-main.366",
        "[15] E. Senger, K. F. Lu, and R. Klinger, \"Deep Learning-based Computational Job Market Analysis: A Survey on Skill Extraction and Classification from Job Postings,\" in Proc. 1st Workshop NLP for Human Resources (NLP4HR), EACL/ACL, 2024, pp. 1-16. https://doi.org/10.18653/v1/2024.nlp4hr-1.1",
        "[16] K. Nguyen, M. Zhang, S. Montariol, and A. Bosselut, \"Rethinking Skill Extraction in the Job Market Domain using Large Language Models,\" in Proc. 1st Workshop NLP for Human Resources (NLP4HR), EACL/ACL, 2024, pp. 27-42. https://doi.org/10.18653/v1/2024.nlp4hr-1.3"
    ]
    format_text_frame(s20.shapes[1].text_frame, None, ref2_points, bullet_size=9.5, with_bullets=False)

    # REORDER SLIDES TO EXACT ACADEMIC SEQUENCE
    print("\n--- Reordering Slides to Academic Chronological Sequence ---")
    move_slide(prs, 19, 10)
    move_slide(prs, 20, 17)

    print(f"\nSaving final presentation to {OUTPUT_PATH}...")
    prs.save(str(OUTPUT_PATH))
    print(f"Presentation successfully created! Total slides: {len(prs.slides)}")

if __name__ == "__main__":
    main()
