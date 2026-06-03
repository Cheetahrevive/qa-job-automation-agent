import PyPDF2
import docx
from typing import Dict, List
import os
import re

class ResumeParser:
    def __init__(self):
        self.qa_skills_db = {
            "automation": ["selenium", "cypress", "playwright", "webdriverio", "puppeteer", "appium"],
            "api_testing": ["postman", "restassured", "requests", "soapui", "swagger"],
            "performance": ["jmeter", "k6", "gatling", "locust", "loadrunner"],
            "languages": ["python", "java", "javascript", "typescript", "c#", "ruby", "go"],
            "ci_cd": ["jenkins", "github actions", "gitlab ci", "circleci", "travis ci"],
            "frameworks": ["pytest", "testng", "junit", "mocha", "jest", "cucumber"],
            "methodologies": ["agile", "scrum", "kanban", "bdd", "tdd", "waterfall"],
            "tools": ["jira", "confluence", "testrail", "zephyr", "qtest", "xray"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"],
            "database": ["sql", "mysql", "postgresql", "mongodb", "oracle", "redis"]
        }
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume and extract relevant information"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume not found: {file_path}")
        
        text = self._extract_text(file_path)
        
        return {
            "skills": self._extract_skills(text),
            "experience_years": self._extract_experience(text),
            "job_titles": self._extract_job_titles(text),
            "certifications": self._extract_certifications(text),
            "education": self._extract_education(text),
            "raw_text": text
        }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX"""
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return ' '.join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            return ' '.join([para.text for para in doc.paragraphs])
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def _extract_skills(self, text: str) -> List[Dict]:
        """Extract QA-related skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.qa_skills_db.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.append({
                        "skill": skill.title(),
                        "category": category.replace('_', ' ').title()
                    })
        
        return found_skills
    
    def _extract_experience(self, text: str) -> int:
        """Estimate years of experience from resume"""
        # Look for patterns like "5+ years", "5 years of experience"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Default estimation based on job history
        job_dates = re.findall(r'(20\d{2})\s*[-–to]+\s*(20\d{2}|present|current)', text.lower())
        if job_dates:
            years = set()
            for start, end in job_dates:
                years.add(int(start))
                if end.isdigit():
                    years.add(int(end))
                else:
                    years.add(2024)  # Current year
            
            if years:
                return max(years) - min(years)
        
        return 0
    
    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract previous job titles"""
        qa_titles = [
            'qa engineer', 'quality assurance engineer', 'test engineer',
            'automation engineer', 'sdet', 'software test engineer',
            'qa analyst', 'quality analyst', 'test automation engineer',
            'senior qa', 'lead qa', 'qa manager', 'test lead'
        ]
        
        text_lower = text.lower()
        found_titles = []
        
        for title in qa_titles:
            if title in text_lower:
                found_titles.append(title.title())
        
        return list(set(found_titles))
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_keywords = [
            'istqb', 'cste', 'csqa', 'csm', 'aws certified',
            'azure certified', 'google certified', 'pmp'
        ]
        
        text_lower = text.lower()
        found_certs = []
        
        for cert in cert_keywords:
            if cert in text_lower:
                found_certs.append(cert.upper())
        
        return found_certs
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        # Look for degree patterns
        degrees = [
            'bachelor', 'master', 'phd', 'associate', 'b.tech', 'm.tech',
            'b.e.', 'm.e.', 'b.sc', 'm.sc', 'mba'
        ]
        
        for degree in degrees:
            if degree in text.lower():
                education.append({"degree": degree.title(), "field": "Computer Science"})
        
        return education
