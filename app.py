import streamlit as st
import os
import pandas as pd
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
from io import BytesIO
import re

# Set page configuration with custom theme
st.set_page_config(
    page_title="Job Matching Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="💼"
)

# Custom CSS for light theme styling
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Main container styling */
    .main .block-container {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        color: #000000;
    }
    .success-box {
        background-color: #D1FAE5;
        border-left: 5px solid #059669;
        padding: 1rem;
        border-radius: 5px;
        color: #000000;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-left: 5px solid #D97706;
        padding: 1rem;
        border-radius: 5px;
        color: #000000;
    }
    .info-box {
        background-color: #E0F2FE;
        border-left: 5px solid #0284C7;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        color: #000000;
    }
    .disclaimer-box {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 5px solid #DC2626;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0 0 1rem 0;
        color: #000000;
    }
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        font-weight: 600;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        width: 100%;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1E40AF !important;
    }
    .input-section {
        border: 2px solid #E2E8F0;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
        background-color: #FFFFFF;
        color: #000000;
    }
    .info-label {
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .tagline {
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E3A8A;
        margin: 1.5rem auto;
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: #EFF6FF;
        border: 1px solid #DBEAFE;
        max-width: 400px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .dark-tagline {
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: #FFFFFF;
        margin: 1.5rem auto;
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: #1E3A8A;
        max-width: 400px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Force text colors for all elements */
    .stMarkdown, .stText, p, div, span {
        color: #000000 !important;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #E2E8F0 !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #E2E8F0 !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        color: #1E3A8A !important;
    }
    
    /* Force white background for all containers */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    
    /* Download button specific styling */
    .stDownloadButton > button {
        background-color: #047857 !important;
        color: white !important;
        border: none !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #065F46 !important;
    }
</style>
""", unsafe_allow_html=True)

# API Keys from Streamlit secrets
try:
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError as e:
    st.error(f"Missing API key in secrets: {e}")
    st.info("""
    **Setup Instructions:**
    
    1. Create a `.streamlit/secrets.toml` file in your project directory
    2. Add your API keys:
    ```
    TAVILY_API_KEY = "your_tavily_api_key_here"
    GOOGLE_API_KEY = "your_google_api_key_here"
    ```
    3. If deploying to Streamlit Community Cloud, add these secrets in your app settings
    """)
    st.stop()

# Check if API keys are available
if not TAVILY_API_KEY or not GOOGLE_API_KEY:
    st.error("API keys are missing or empty. Please check your secrets configuration.")
    st.stop()

SYSTEM_PROMPT = """
You are an expert career counselor and job market analyst with deep knowledge of various industries, job roles, and skill requirements.
Your role is to analyze a person's skills and provide comprehensive job matching analysis based on real-time market data.

You have access to web search tools to gather the latest information about:
- Current job market trends
- Specific job role requirements
- Company hiring practices and salary ranges
- Skill gap analysis for different roles
- Industry-specific requirements

Always provide accurate, up-to-date information based on real market data, never use synthetic or placeholder information.
Focus on actionable insights that can help the person make informed career decisions.
"""

INSTRUCTIONS = """
Based on the user's skills, perform the following analysis using web search to gather real-time data:

1. **Eligible Job Roles Analysis:**
   - Search for current job openings that match the user's skills
   - Identify specific job titles and roles they qualify for
   - Provide detailed job descriptions and responsibilities
   - Include both entry-level and advanced positions based on skill level

2. **Skill Gap Analysis:**
   - Compare user's skills with requirements for desired/relevant job roles
   - Identify specific skills that are missing or need improvement
   - Prioritize skill gaps based on market demand and career impact
   - Suggest learning resources and certification programs

3. **Company and Opportunity Analysis:**
   - Search for companies actively hiring for relevant roles
   - Include company names, sizes, and industries
   - Provide information about company culture and work environment
   - Include both established companies and startups

4. **Salary and Package Analysis:**
   - Research current salary ranges for identified job roles
   - Include base salary, bonuses, and benefits information
   - Consider geographic location and experience level
   - Provide salary progression paths

Return all information in a structured format:
*Eligible Job Roles:* <detailed list with specific roles, requirements, and market demand>
*Skill Gap Analysis:* <specific skills missing, priority levels, and learning recommendations>
*Companies Hiring:* <company names, role details, and application information>
*Salary Packages:* <current market rates, ranges, and progression paths>

Ensure all information is current, accurate, and based on real market data from your web searches.
"""

@st.cache_resource
def get_agent():
    """Initialize and cache the AI agent."""
    try:
        return Agent(
            model=Gemini(id="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY),
            system_prompt=SYSTEM_PROMPT,
            instructions=INSTRUCTIONS,
            tools=[TavilyTools(api_key=TAVILY_API_KEY)],
            markdown=True,
        )
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None

def analyze_job_match(skills, experience_level, preferred_location, career_goals):
    """Analyze job matching based on user's skills and preferences."""
    agent = get_agent()
    if agent is None:
        return None

    try:
        # Create comprehensive query for the agent
        query = f"""
        Analyze job opportunities for a candidate with the following profile:
        
        Skills: {skills}
        Experience Level: {experience_level}
        Preferred Location: {preferred_location}
        Career Goals: {career_goals}
        
        Please provide a comprehensive job market analysis including eligible roles, skill gaps, hiring companies, and salary information.
        Use current market data from job portals, company websites, and industry reports.
        """
        
        with st.spinner("🔍 Analyzing job market and matching opportunities..."):
            response = agent.run(query)
            return response.content.strip()
    except Exception as e:
        st.error(f"Error analyzing job match: {e}")
        return None

def create_job_report_pdf(analysis_results, user_profile):
    """Create a PDF report of the job analysis."""
    try:
        buffer = BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Content to add to PDF
        content = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            alignment=1,
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.navy,
            spaceAfter=6
        )
        normal_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=12,
            leading=14
        )
        
        # Title
        content.append(Paragraph("Job Matching Analysis Report", title_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content.append(Paragraph(f"Generated on: {current_datetime}", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # User Profile Section
        content.append(Paragraph("Candidate Profile:", heading_style))
        for key, value in user_profile.items():
            if value:
                content.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Analysis results
        content.append(Paragraph("Job Market Analysis:", heading_style))
        
        # Format the analysis results for PDF
        if analysis_results:
            # Use regex to find sections in the format "*SectionName:* Content"
            section_pattern = r"\*([\w\s]+):\*(.*?)(?=\*[\w\s]+:\*|$)"
            matches = re.findall(section_pattern, analysis_results, re.DOTALL | re.IGNORECASE)
            
            if matches:
                for section_title, section_content in matches:
                    content.append(Paragraph(f"<b>{section_title.strip()}:</b>", normal_style))
                    
                    # Handle multiline content
                    paragraphs = section_content.strip().split("\n")
                    for para in paragraphs:
                        if para.strip():
                            # Escape HTML characters for ReportLab
                            clean_para = para.strip().replace('<', '&lt;').replace('>', '&gt;')
                            content.append(Paragraph(clean_para, normal_style))
                    
                    content.append(Spacer(1, 0.15*inch))
            else:
                # Fallback: add the entire analysis as-is if regex doesn't match
                clean_results = analysis_results.replace('<', '&lt;').replace('>', '&gt;')
                content.append(Paragraph(clean_results, normal_style))
        
        # Footer
        content.append(Spacer(1, 0.5*inch))
        content.append(Paragraph("© 2025 Job Matching Tool | Powered by Gemini AI + Tavily", 
                                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))
        
        # Build PDF
        pdf.build(content)
        
        # Get the PDF value from the buffer
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error creating PDF: {e}")
        return None

def main():
    # Initialize session state
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}

    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">💼 Job Matching Tool</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem; color: #4B5563;">
            Enter your skills to discover job opportunities, skill gaps, and salary insights
        </div>
        """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer-box" style="margin-top: 0; margin-bottom: 1rem;">
        <div style="display: flex; align-items: flex-start;">
            <span style="font-size: 1.3rem; margin-right: 0.5rem; margin-top: 0.1rem;">💡</span>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem; color: #DC2626;">CAREER GUIDANCE DISCLAIMER</div>
                <div style="font-size: 0.9rem; line-height: 1.4; color: #374151;">This tool provides general career guidance based on market data analysis. Job market conditions vary by location and time. Always verify information independently and consider consulting with career professionals for personalized advice.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in two-column layout
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        # Tagline above the input section
        st.markdown('<div class="tagline">🎯 Find your perfect job match instantly!</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # Skills input
        skills = st.text_area(
            "Your Skills",
            placeholder="e.g., Python, JavaScript, React, SQL, Machine Learning, Project Management, Data Analysis...",
            height=100,
            help="List all your technical and soft skills separated by commas"
        )
        
        # Experience level
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level (0-2 years)", "Mid Level (2-5 years)", "Senior Level (5-10 years)", "Expert Level (10+ years)"],
            help="Select your current experience level"
        )
        
        # Preferred location
        preferred_location = st.text_input(
            "Preferred Job Location",
            placeholder="e.g., New York, Remote, San Francisco, London...",
            help="Enter your preferred work location or 'Remote' for remote work"
        )
        
        # Career goals
        career_goals = st.text_area(
            "Career Goals (Optional)",
            placeholder="e.g., Become a Senior Software Engineer, Transition to Data Science, Start in Product Management...",
            height=80,
            help="Describe your career aspirations and goals"
        )
        
        # Analyze button
        if st.button("🔍 Analyze Job Market", key="analyze_btn"):
            if skills.strip():
                st.session_state.analyze_clicked = True
                
                # Store user profile
                st.session_state.user_profile = {
                    "Skills": skills,
                    "Experience Level": experience_level,
                    "Preferred Location": preferred_location,
                    "Career Goals": career_goals
                }
                
                # Perform analysis
                analysis_result = analyze_job_match(skills, experience_level, preferred_location, career_goals)
                st.session_state.analysis_results = analysis_result
            else:
                st.error("Please enter your skills to proceed with the analysis.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Tagline above the results section
        st.markdown('<div class="dark-tagline">📊 Your career roadmap awaits!</div>', unsafe_allow_html=True)
        
        # Display results if available
        if st.session_state.analysis_results:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="subheader">Job Market Analysis Results</div>', unsafe_allow_html=True)
            
            # Format the analysis results with better styling
            formatted_info = st.session_state.analysis_results.replace(
                "*Eligible Job Roles:*", "<div class='info-label'>🎯 Eligible Job Roles:</div>"
            ).replace(
                "*Skill Gap Analysis:*", "<div class='info-label'>📈 Skill Gap Analysis:</div>"
            ).replace(
                "*Companies Hiring:*", "<div class='info-label'>🏢 Companies Hiring:</div>"
            ).replace(
                "*Salary Packages:*", "<div class='info-label'>💰 Salary Packages:</div>"
            )
            
            st.markdown(formatted_info, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Create PDF report
            if st.session_state.user_profile:
                pdf_bytes = create_job_report_pdf(st.session_state.analysis_results, st.session_state.user_profile)
                if pdf_bytes:
                    st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
                    download_filename = f"job_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label="📄 Download Career Report",
                        data=pdf_bytes,
                        file_name=download_filename,
                        mime="application/pdf",
                        key="download_pdf",
                        use_container_width=True,
                        help="Download a comprehensive PDF report with job analysis results",
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 400px; text-align: center;">
                <div style="color: #6B7280; font-size: 4rem; margin-bottom: 1rem;">💼</div>
                <div style="font-weight: 600; font-size: 1.2rem; color: #1E3A8A; margin-bottom: 0.5rem;">Ready to Find Your Dream Job</div>
                <div style="color: #374151;">Enter your skills and preferences, then click "Analyze Job Market" to see personalized job recommendations</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Additional features section
    st.markdown("---")
    st.markdown("### 🚀 What You'll Discover")
    
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
    
    with feature_col1:
        st.markdown("""
        <div class="info-box">
            <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">🎯</div>
            <div style="font-weight: 600; text-align: center; margin-bottom: 0.5rem;">Job Roles</div>
            <div style="text-align: center; font-size: 0.9rem;">Discover positions that match your skills perfectly</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="warning-box">
            <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">📈</div>
            <div style="font-weight: 600; text-align: center; margin-bottom: 0.5rem;">Skill Gaps</div>
            <div style="text-align: center; font-size: 0.9rem;">Identify skills to learn for better opportunities</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="success-box">
            <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">🏢</div>
            <div style="font-weight: 600; text-align: center; margin-bottom: 0.5rem;">Companies</div>
            <div style="text-align: center; font-size: 0.9rem;">Find companies actively hiring for your profile</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col4:
        st.markdown("""
        <div class="info-box">
            <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">💰</div>
            <div style="font-weight: 600; text-align: center; margin-bottom: 0.5rem;">Salaries</div>
            <div style="text-align: center; font-size: 0.9rem;">Get current market salary ranges and packages</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #E5E7EB; color: #6B7280; font-size: 0.8rem;">
        © 2025 Job Matching Tool | Powered by Gemini Flash 2 Pro + Tavily | Real-time Job Market Data
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
