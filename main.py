from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import re
from collections import defaultdict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# [Previous assessments list remains exactly the same...]
assessments = [

    #Business
    {"name": "Account Manager Solution", "url": "https://www.shl.com/solutions/use-cases/pre-employment-testing/account-manager/", "technologies": ["sales", "account management", "customer relations"], "duration": "45m", "type": "Job Solution", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Administrative Professional - Short Form", "url": "https://www.shl.com/solutions/use-cases/pre-employment-testing/administrative-professional/", "technologies": ["administrative", "organization", "communication"], "duration": "35m", "type": "Job Solution", "remote": "Yes", "adaptive": "No"},
    {"name": "Agency Manager Solution", "url": "https://www.shl.com/solutions/use-cases/pre-employment-testing/agency-manager/", "technologies": ["management", "leadership", "operations"], "duration": "50m", "type": "Job Solution", "remote": "Yes", "adaptive": "Partial"},
    {"name": "Apprentice + 8.0 Job Focused Assessment", "url": "https://www.shl.com/solutions/products/ready-to-use-assessments/apprentice-8/", "technologies": ["apprenticeship", "technical skills", "aptitude"], "duration": "60m", "type": "Job Solution", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Apprentice 8.0 Job Focused Assessment", "url": "https://www.shl.com/solutions/products/ready-to-use-assessments/apprentice-8/", "technologies": ["vocational", "mechanical", "electrical"], "duration": "55m", "type": "Job Solution", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Bank Administrative Assistant - Short Form", "url": "https://www.shl.com/solutions/use-cases/financial-services/banking-roles/", "technologies": ["banking", "administration", "compliance"], "duration": "30m", "type": "Job Solution", "remote": "Yes", "adaptive": "No"},
    {"name": "Bank Collections Agent - Short Form", "url": "https://www.shl.com/solutions/use-cases/financial-services/collections/", "technologies": ["collections", "negotiation", "financial"], "duration": "40m", "type": "Job Solution", "remote": "Yes", "adaptive": "Partial"},
    {"name": "Bank Operations Supervisor - Short Form", "url": "https://www.shl.com/solutions/use-cases/financial-services/banking-roles/", "technologies": ["bank operations", "supervision", "compliance"], "duration": "45m", "type": "Job Solution", "remote": "Yes", "adaptive": "Partial"},
    {"name": "Bilingual Spanish Reservation Agent Solution", "url": "https://www.shl.com/solutions/use-cases/customer-service/bilingual/", "technologies": ["spanish", "customer service", "reservations"], "duration": "35m", "type": "Job Solution", "remote": "Yes", "adaptive": "No"},
    {"name": "Bookkeeping, Accounting, Auditing Clerk Short Form", "url": "https://www.shl.com/solutions/use-cases/financial-services/accounting/", "technologies": ["accounting", "bookkeeping", "auditing"], "duration": "40m", "type": "Job Solution", "remote": "Yes", "adaptive": "No"},
    {"name": "Branch Manager - Short Form", "url": "https://www.shl.com/solutions/use-cases/financial-services/banking-roles/", "technologies": ["branch management", "banking", "leadership"], "duration": "50m", "type": "Job Solution", "remote": "Yes", "adaptive": "Partial"},
    {"name": "Cashier Solution", "url": "https://www.shl.com/solutions/use-cases/retail-hospitality/cashier/", "technologies": ["retail", "cash handling", "customer service"], "duration": "30m", "type": "Job Solution", "remote": "Yes", "adaptive": "No"},

    # Java
    {"name": "Java 8 (New)", "url": "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/", "technologies": ["java", "java 8"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Core Java (Advanced)", "url": "https://www.shl.com/solutions/products/product-catalog/view/core-java-advanced-level-new/", "technologies": ["java", "core java"], "duration": "55m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java Platform Enterprise Edition 7 (Java EE 7)", "url": "https://www.shl.com/solutions/products/product-catalog/view/java-platform-enterprise-edition-7-java-ee-7/", "technologies": ["java", "java ee"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java EE 6", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33291-java-ee-6/", "technologies": ["java", "java ee"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java Programming Intermediate", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33459-java-programming-intermediate/", "technologies": ["java"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java Programming Advanced", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33458-java-programming-advanced/", "technologies": ["java"], "duration": "55m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Core Java", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33328-core-java/", "technologies": ["java", "core java"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java Programming Basic", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33457-java-programming-basic/", "technologies": ["java"], "duration": "40m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java Spring Framework", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33330-java-spring-framework/", "technologies": ["java", "spring"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Java Servlets", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33329-java-servlets/", "technologies": ["java", "servlets"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    
    # Python
    {"name": "Python (New)", "url": "https://www.shl.com/solutions/products/product-catalog/view/python-new/", "technologies": ["python"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python 3.6", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33495-python-3-6/", "technologies": ["python"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python Programming Intermediate", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33493-python-programming-intermediate/", "technologies": ["python"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Core Python", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33341-core-python/", "technologies": ["python"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python Programming Basic", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33492-python-programming-basic/", "technologies": ["python"], "duration": "40m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python Advanced Level", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33338-python-advanced-level/", "technologies": ["python"], "duration": "55m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python for Data Science", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33343-python-for-data-science/", "technologies": ["python", "data science"], "duration": "65m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Automata Python", "url": "https://www.shl.com/solutions/products/product-catalog/view/automata-python/", "technologies": ["python", "automata"], "duration": "55m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python Coding Simulation", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33496-python-coding-simulation/", "technologies": ["python"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Python Programming Concepts", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33494-python-programming-concepts/", "technologies": ["python"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    
    # SQL
    {"name": "SQL (New)", "url": "https://www.shl.com/solutions/products/product-catalog/view/sql-new/", "technologies": ["sql"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Entry Level", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33381-sql-entry-level/", "technologies": ["sql"], "duration": "40m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL for Client-Server Applications", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33592-sql-for-client-server-applications/", "technologies": ["sql"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Advanced SQL Queries", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33595-advanced-sql-queries/", "technologies": ["sql", "database"], "duration": "55m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Database Design", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33590-sql-database-design/", "technologies": ["sql", "database"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Joins and Subqueries", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33591-sql-joins-and-subqueries/", "technologies": ["sql"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Stored Procedures", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33593-sql-stored-procedures/", "technologies": ["sql"], "duration": "55m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Optimization", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33594-sql-optimization/", "technologies": ["sql"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Programming", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33588-sql-programming/", "technologies": ["sql"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SQL Query Writing", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33589-sql-query-writing/", "technologies": ["sql"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},

    
    # HTML/CSS
    {"name": "HTML/CSS (New)", "url": "https://www.shl.com/solutions/products/product-catalog/view/htmlcss-new/", "technologies": ["html", "css", "web development"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "HTML5 (New)", "url": "https://www.shl.com/solutions/products/product-catalog/view/html5-new/", "technologies": ["html", "web development"], "duration": "40m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "Cascading Style Sheets 4.0", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33706-cascading-style-sheets-4-0/", "technologies": ["css", "web development"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "HTML5 and CSS3", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33708-html5-and-css3/", "technologies": ["html", "css", "web development"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "HTML Programming Basic", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33701-html-programming-basic/", "technologies": ["html", "web development"], "duration": "40m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "CSS3 Advanced", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33707-css3-advanced/", "technologies": ["css", "web development"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "Web Development Basics", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33709-web-development-basics/", "technologies": ["html", "css", "web development"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "HTML5 Forms and Elements", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33710-html5-forms-and-elements/", "technologies": ["html", "web development"], "duration": "40m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "CSS Layouts", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33711-css-layouts/", "technologies": ["css", "web development"], "duration": "45m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    {"name": "CSS Animation", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33712-css-animation/", "technologies": ["css", "web development"], "duration": "50m", "type": "Technical", "remote": "Yes", "adaptive": "No"},
    
    # Machine Learning
    {"name": "Data Science (New)", "url": "https://www.shl.com/solutions/products/product-catalog/view/data-science-new/", "technologies": ["data science", "machine learning"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Machine Learning Basics", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33601-machine-learning-basics/", "technologies": ["machine learning", "ml"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Supervised Learning Techniques", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33602-supervised-learning-techniques/", "technologies": ["machine learning", "ml"], "duration": "65m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Unsupervised Learning Techniques", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33603-unsupervised-learning-techniques/", "technologies": ["machine learning", "ml"], "duration": "65m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Deep Learning Fundamentals", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33604-deep-learning-fundamentals/", "technologies": ["deep learning"], "duration": "70m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Automata ML", "url": "https://www.shl.com/solutions/products/product-catalog/view/automata-machine-learning/", "technologies": ["machine learning", "ml", "automata"], "duration": "60m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "ML Model Evaluation", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33605-ml-model-evaluation/", "technologies": ["machine learning", "ml"], "duration": "65m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Applied Machine Learning", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33606-applied-machine-learning/", "technologies": ["machine learning", "ml"], "duration": "70m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "ML in Production", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33607-ml-in-production/", "technologies": ["machine learning", "ml"], "duration": "75m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Natural Language Processing", "url": "https://www.shl.com/c/global/ibm-kenexa-catalog/view/33608-natural-language-processing/", "technologies": ["nlp", "natural language processing"], "duration": "70m", "type": "Technical", "remote": "Yes", "adaptive": "Yes"},
    
    
    # Verbal Tests
    {"name": "Business Communication (adaptive)", "url": "https://www.shl.com/solutions/products/product-catalog/view/business-communication-adaptive/", "technologies": ["communication", "verbal", "business writing"], "duration": "30m", "type": "Verbal", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Business Communications", "url": "https://www.shl.com/solutions/products/product-catalog/view/business-communications/", "technologies": ["communication", "professional writing", "email", "Initial commit"], "duration": "35m", "type": "Verbal", "remote": "Yes", "adaptive": "No"},
    {"name": "Interpersonal Communications", "url": "https://www.shl.com/solutions/products/product-catalog/view/interpersonal-communications/", "technologies": ["communication", "soft skills", "teamwork"], "duration": "25m", "type": "Verbal", "remote": "Yes", "adaptive": "No"},
    {"name": "Verify - Technical Checking - Next Generation", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-technical-checking-next-generation/", "technologies": ["technical writing", "attention to detail", "proofreading"], "duration": "40m", "type": "Verbal", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify - Verbal Ability - Next Generation", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-verbal-ability-next-generation/", "technologies": ["verbal reasoning", "comprehension", "critical thinking"], "duration": "45m", "type": "Verbal", "remote": "Yes", "adaptive": "Yes"},

    # Reasoning Tests
    {"name": "SHL Verify Interactive - Inductive Reasoning", "url": "https://www.shl.com/solutions/products/product-catalog/view/shl-verify-interactive-inductive-reasoning/", "technologies": ["pattern recognition", "logical thinking", "problem solving", "cognitive", "reasoning"], "duration": "25m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SHL Verify Interactive - Deductive Reasoning", "url": "https://www.shl.com/solutions/products/product-catalog/view/shl-verify-interactive-deductive-reasoning/", "technologies": ["logical reasoning", "decision making", "analysis", "cognitive", "reasoning"], "duration": "30m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SHL Verify Interactive - Numerical Reasoning", "url": "https://www.shl.com/solutions/products/product-catalog/view/shl-verify-interactive-numerical-reasoning/", "technologies": ["numeracy", "data interpretation", "financial analysis", "cognitive", "reasoning"], "duration": "35m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "SHL Verify Interactive G+", "url": "https://www.shl.com/solutions/products/product-catalog/view/shl-verify-interactive-g/", "technologies": ["general ability", "cognitive skills", "aptitude", "reasoning", "reasoning"], "duration": "50m", "type": "cognitive", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify - Deductive Reasoning", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-deductive-reasoning/", "technologies": ["logical deduction", "syllogisms", "critical thinking", "cognitive", "reasoning"], "duration": "30m", "type": "cognitive", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify - Inductive Reasoning (2014)", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-inductive-reasoning-2014/", "technologies": ["pattern recognition", "abstract reasoning", "problem solving", "cognitive", "reasoning"], "duration": "25m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify - Numerical Ability", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-numerical-ability/", "technologies": ["numerical analysis", "data interpretation", "mathematics", "cognitive", "reasoning"], "duration": "35m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify G+ - Ability Test Report", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-g-ability-test-report/", "technologies": ["cognitive ability", "general intelligence", "aptitude", "cognitive", "reasoning"], "duration": "55m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify G+ - Candidate Report", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-g-candidate-report/", "technologies": ["cognitive profile", "strengths analysis", "development areas", "cognitive", "reasoning"], "duration": "60m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},
    {"name": "Verify Interactive Ability Report", "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-interactive-ability-report/", "technologies": ["cognitive skills", "performance analysis", "potential", "cognitive", "reasoning"], "duration": "50m", "type": "Reasoning", "remote": "Yes", "adaptive": "Yes"},

    # Personality Tests
    {"name": "Motivation Questionnaire MQM5", "url": "https://www.shl.com/solutions/products/product-catalog/view/motivation-questionnaire-mqm5/", "technologies": ["motivation", "drive", "work preferences"], "duration": "20m", "type": "Personality", "remote": "Yes", "adaptive": "No"},
    {"name": "MQ Candidate Motivation Report", "url": "https://www.shl.com/solutions/products/product-catalog/view/mq-candidate-motivation-report/", "technologies": ["motivational fit", "engagement", "career alignment"], "duration": "25m", "type": "Personality", "remote": "Yes", "adaptive": "No"},
    {"name": "MQ Employee Motivation Report", "url": "https://www.shl.com/solutions/products/product-catalog/view/mq-employee-motivation-report/", "technologies": ["employee engagement", "retention", "job satisfaction"], "duration": "25m", "type": "Personality", "remote": "Yes", "adaptive": "No"},
    {"name": "MQ Motivation Report Pack", "url": "https://www.shl.com/solutions/products/product-catalog/view/mq-motivation-report-pack/", "technologies": ["motivation profile", "development", "coaching"], "duration": "30m", "type": "Personality", "remote": "Yes", "adaptive": "No"},
    {"name": "MQ Profile", "url": "https://www.shl.com/solutions/products/product-catalog/view/mq-profile/", "technologies": ["work motivation", "career drivers", "values"], "duration": "20m", "type": "Personality", "remote": "Yes", "adaptive": "No"},
    {"name": "OPQ MQ Sales Report", "url": "https://www.shl.com/solutions/products/product-catalog/view/opq-mq-sales-report/", "technologies": ["sales personality", "persuasion", "resilience"], "duration": "35m", "type": "Personality", "remote": "Yes", "adaptive": "No"},
]

class RecommendationRequest(BaseModel):
    text: str
    max_duration: Optional[int] = None

class QueryRequest(BaseModel):
    query: str

def find_technologies(text: str) -> List[str]:
    text_lower = text.lower()
    found_techs = set()
    for assessment in assessments:
        for tech in assessment["technologies"]:
            if re.search(r'\b' + re.escape(tech.lower()) + r'\b', text_lower):
                found_techs.add(tech.lower())
    return list(found_techs)

@app.post("/api/recommend")
async def recommend(request: RecommendationRequest):
    return get_recommendations(request.text, request.max_duration)

@app.post("/query")
async def query_api(req: QueryRequest):
    recommendations = get_recommendations(req.query)
    return {
        "answer": "Based on your query, we recommend the following SHL assessments:",
        "source_documents": recommendations["assessments"]
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def get_recommendations(text: str, max_duration: Optional[int] = None):
    text_lower = text.lower()
    tech_assessments = defaultdict(list)
    all_matched = []

    for assessment in assessments:
        tech_match = any(
            re.search(r'\b' + re.escape(tech.lower()) + r'\b', text_lower)
            for tech in assessment["technologies"]
        )
        duration_ok = True
        if max_duration:
            duration = int(assessment["duration"].replace('m', ''))
            duration_ok = duration <= max_duration

        if tech_match and duration_ok:
            primary_tech = next(
                (tech for tech in assessment["technologies"]
                 if re.search(r'\b' + re.escape(tech.lower()) + r'\b', text_lower)),
                assessment["technologies"][0]
            )
            tech_assessments[primary_tech.lower()].append(assessment)
            all_matched.append(assessment)

    found_techs = find_technologies(text)
    if not found_techs:
        return {
            "technologies": [],
            "assessments": [a for a in all_matched[:10]]
        }

    tech_counts = {}
    remaining = 10
    for tech in found_techs:
        available = len(tech_assessments.get(tech, []))
        if available > 0:
            tech_counts[tech] = 1
            remaining -= 1

    if remaining > 0:
        total_available = sum(
            min(len(tech_assessments.get(tech, [])), 10) - tech_counts.get(tech, 0)
            for tech in found_techs
        )
        if total_available > 0:
            for tech in found_techs:
                available = len(tech_assessments.get(tech, [])) - tech_counts.get(tech, 0)
                if available > 0:
                    share = max(1, round(available / total_available * remaining))
                    tech_counts[tech] = tech_counts.get(tech, 0) + min(share, available)

    recommendations = []
    used_assessments = set()
    for tech in found_techs:
        if tech in tech_assessments:
            count = tech_counts.get(tech, 0)
            for assessment in tech_assessments[tech]:
                if count <= 0:
                    break
                if assessment["name"] not in used_assessments:
                    recommendations.append(assessment)
                    used_assessments.add(assessment["name"])
                    count -= 1

    if len(recommendations) < 10 and len(all_matched) > len(recommendations):
        for assessment in all_matched:
            if assessment["name"] not in used_assessments and len(recommendations) < 10:
                recommendations.append(assessment)
                used_assessments.add(assessment["name"])

    return {
        "technologies": found_techs,
        "assessments": recommendations[:10]
    }
