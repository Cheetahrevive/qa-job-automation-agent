from typing import List, Dict
import re

class JobMatcher:
    def __init__(self):
        self.match_threshold = 0.6
    
    def match_jobs(self, resume: Dict, jobs: List[Dict]) -> List[Dict]:
        """Score and rank jobs based on resume fit"""
        matched_jobs = []
        
        for job in jobs:
            # Calculate skill match
            skill_match = self._calculate_skill_match(resume.get('skills', []), job)
            
            # Calculate experience match
            experience_match = self._calculate_experience_match(
                resume.get('experience_years', 0), job
            )
            
            # Calculate title match
            title_match = self._calculate_title_match(
                resume.get('job_titles', []), job
            )
            
            # Combined score (weighted)
            final_score = (skill_match * 0.5) + (experience_match * 0.3) + (title_match * 0.2)
            
            if final_score >= self.match_threshold:
                job['match_score'] = final_score
                job['skill_match'] = skill_match
                job['experience_match'] = experience_match
                matched_jobs.append(job)
        
        # Sort by match score
        matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_jobs
    
    def _calculate_skill_match(self, resume_skills: List[Dict], job: Dict) -> float:
        """Calculate percentage of required skills matched"""
        job_description = job.get('description', '').lower()
        if not job_description or not resume_skills:
            return 0.0
        
        # Extract skills from job description
        job_skills = self._extract_job_skills(job_description)
        if not job_skills:
            return 0.5  # Default score if no skills found
        
        # Count matching skills
        resume_skill_names = {s['skill'].lower() for s in resume_skills}
        matched = sum(1 for skill in job_skills if skill.lower() in resume_skill_names)
        
        return matched / len(job_skills) if job_skills else 0.0
    
    def _extract_job_skills(self, description: str) -> List[str]:
        """Extract required skills from job description"""
        # Common QA skills to look for
        common_skills = [
            'selenium', 'python', 'java', 'javascript', 'api testing',
            'automation', 'manual testing', 'test cases', 'test plans',
            'agile', 'scrum', 'jira', 'jenkins', 'git', 'sql',
            'performance testing', 'regression testing', 'integration testing',
            'cypress', 'playwright', 'postman', 'rest api', 'soap'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill in description_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _calculate_experience_match(self, resume_years: int, job: Dict) -> float:
        """Match years of experience"""
        job_description = job.get('description', '').lower()
        
        # Look for required years in job description
        patterns = [
            r'(\d+)[\+]*\s*(?:\+\s*)?years?\s*(?:of\s*)?experience',
            r'experience\s*:?\s*(\d+)[\+]*\s*years?',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
        ]
        
        required_years = 0
        for pattern in patterns:
            match = re.search(pattern, job_description)
            if match:
                required_years = int(match.group(1))
                break
        
        if required_years == 0:
            return 0.7  # Default score if no experience requirement
        
        if resume_years >= required_years:
            return 1.0
        elif resume_years >= required_years * 0.7:
            return 0.7
        else:
            return 0.3
    
    def _calculate_title_match(self, resume_titles: List[str], job: Dict) -> float:
        """Match job titles"""
        job_title = job.get('title', '').lower()
        if not job_title or not resume_titles:
            return 0.5
        
        resume_titles_lower = [t.lower() for t in resume_titles]
        
        # Direct match
        if any(title in job_title for title in resume_titles_lower):
            return 1.0
        
        # Partial match
        words = set(job_title.split())
        for title in resume_titles_lower:
            title_words = set(title.split())
            if words & title_words:
                return 0.7
        
        return 0.3
