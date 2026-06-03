# scripts/create_test_resume.py
from fpdf import FPDF
import os

def create_test_resume():
    """Create a test resume PDF"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'resume')
    os.makedirs(data_dir, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "John Doe", ln=True, align='C')
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "QA Automation Engineer", ln=True, align='C')
    pdf.cell(0, 6, "Email: john.doe@email.com | Phone: (555) 123-4567", ln=True, align='C')
    pdf.cell(0, 6, "LinkedIn: linkedin.com/in/johndoe | Location: San Francisco, CA", ln=True, align='C')
    
    pdf.ln(10)
    
    # Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PROFESSIONAL SUMMARY", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, "Experienced QA Automation Engineer with 5+ years in software testing. Proficient in Selenium, Python, Java, API testing, and CI/CD pipelines. Strong background in Agile methodologies and test automation frameworks.")
    
    pdf.ln(5)
    
    # Skills
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "TECHNICAL SKILLS", ln=True)
    pdf.set_font("Arial", "", 10)
    
    skills = [
        "Automation: Selenium WebDriver, Cypress, Playwright, Appium",
        "Languages: Python, Java, JavaScript, SQL",
        "API Testing: Postman, REST Assured, SoapUI",
        "CI/CD: Jenkins, GitHub Actions, Docker, Kubernetes",
        "Frameworks: TestNG, JUnit, PyTest, Mocha",
        "Tools: JIRA, TestRail, Git, AWS, Azure"
    ]
    
    for skill in skills:
        pdf.cell(0, 6, f"• {skill}", ln=True)
    
    pdf.ln(5)
    
    # Experience
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PROFESSIONAL EXPERIENCE", ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Senior QA Engineer | Tech Corp Inc. | 2020-Present", ln=True)
    pdf.set_font("Arial", "", 10)
    experiences = [
        "• Developed and maintained automation frameworks using Selenium and Python",
        "• Reduced regression testing time by 60% through automated test suites",
        "• Led API testing initiatives using Postman and REST Assured",
        "• Implemented CI/CD pipeline integration with Jenkins and GitHub Actions"
    ]
    for exp in experiences:
        pdf.cell(0, 6, exp, ln=True)
    
    pdf.ln(3)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "QA Engineer | Digital Solutions Ltd. | 2018-2020", ln=True)
    pdf.set_font("Arial", "", 10)
    experiences = [
        "• Created and executed test plans for web and mobile applications",
        "• Automated 200+ test cases using Java and Selenium WebDriver",
        "• Performed performance testing using JMeter"
    ]
    for exp in experiences:
        pdf.cell(0, 6, exp, ln=True)
    
    # Save
    pdf_path = os.path.join(data_dir, 'test_resume.pdf')
    pdf.output(pdf_path)
    print(f"✅ Test resume created: {pdf_path}")

if __name__ == '__main__':
    try:
        from fpdf import FPDF
        create_test_resume()
    except ImportError:
        print("Installing fpdf...")
        os.system("pip install fpdf")
        from fpdf import FPDF
        create_test_resume()
