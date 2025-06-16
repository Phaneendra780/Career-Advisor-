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
    page_icon="🚀"
)

# Nude and professional CSS with modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Nude professional color palette */
    :root {
        --primary-nude: #F5EFE6;
        --secondary-nude: #E8DFCA;
        --dark-nude: #D8C4B6;
        --accent-nude: #967E76;
        --text-dark: #3D3B40;
        --text-light: #FFFFFF;
        --glass-bg: rgba(245, 239, 230, 0.7);
        --glass-border: rgba(232, 223, 202, 0.8);
        --shadow-light: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        --shadow-heavy: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main app styling */
    .stApp {
        background: var(--primary-nude) !important;
        min-height: 100vh;
    }
    
    /* Container styling with professional look */
    .main .block-container {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: var(--shadow-medium) !important;
        padding: 2rem !important;
        margin-top: 1rem !important;
        animation: fadeInUp 0.8s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: var(--accent-nude) !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        font-weight: 400;
        color: var(--text-dark);
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .glass-card {
        background: var(--text-light) !important;
        border-radius: 12px !important;
        border: 1px solid var(--secondary-nude) !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        box-shadow: var(--shadow-light) !important;
        transition: all 0.3s ease !important;
    }
    
    .glass-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: var(--shadow-medium) !important;
        border-color: var(--accent-nude) !important;
    }
    
    /* Input section styling */
    .input-section {
        background: var(--text-light) !important;
        border-radius: 12px !important;
        border: 1px solid var(--secondary-nude) !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        box-shadow: var(--shadow-light) !important;
    }
    
    /* Tagline styling */
    .tagline {
        text-align: center !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        color: var(--accent-nude) !important;
        margin: 1.5rem auto !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 8px !important;
        background: var(--text-light) !important;
        border: 1px solid var(--secondary-nude) !important;
        max-width: 500px !important;
    }
    
    .dark-tagline {
        text-align: center !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        color: var(--text-light) !important;
        margin: 1.5rem auto !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 8px !important;
        background: var(--accent-nude) !important;
        max-width: 500px !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--accent-nude) !important;
        color: var(--text-light) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--dark-nude) !important;
        box-shadow: var(--shadow-medium) !important;
    }
    
    /* Feature box styling */
    .feature-box {
        background: var(--text-light) !important;
        border-radius: 12px !important;
        border: 1px solid var(--secondary-nude) !important;
        padding: 1.5rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
    }
    
    .feature-box:hover {
        transform: translateY(-5px) !important;
        box-shadow: var(--shadow-medium) !important;
        border-color: var(--accent-nude) !important;
    }
    
    .feature-icon {
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
        color: var(--accent-nude) !important;
    }
    
    .feature-title {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: var(--text-dark) !important;
        margin-bottom: 0.5rem !important;
    }
    
    .feature-description {
        color: var(--text-dark) !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        opacity: 0.8;
    }
    
    /* Results section styling */
    .results-card {
        background: var(--text-light) !important;
        border-radius: 12px !important;
        border: 1px solid var(--secondary-nude) !important;
        padding: 2rem !important;
        box-shadow: var(--shadow-light) !important;
        min-height: 400px !important;
    }
    
    .info-label {
        font-weight: 600 !important;
        color: var(--accent-nude) !important;
        font-size: 1.1rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Text styling */
    .stMarkdown, .stText, p, div, span {
        color: var(--text-dark) !important;
    }
    
    /* Input field styling */
    .stTextArea > div > div > textarea,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: var(--text-light) !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--secondary-nude) !important;
        border-radius: 8px !important;
    }
    
    .stTextArea > div > div > textarea:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--accent-nude) !important;
        box-shadow: 0 0 0 2px rgba(150, 126, 118, 0.1) !important;
    }
    
    .stTextArea > div > div > textarea::placeholder,
    .stTextInput > div > div > input::placeholder {
        color: rgba(61, 59, 64, 0.5) !important;
    }
    
    /* Label styling */
    .stTextArea > label,
    .stTextInput > label,
    .stSelectbox > label {
        color: var(--text-dark) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    /* Disclaimer styling */
    .disclaimer-box {
        background: rgba(150, 126, 118, 0.1) !important;
        border: 1px solid var(--secondary-nude) !important;
        border-left: 4px solid var(--accent-nude) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        color: var(--text-dark) !important;
    }
    
    /* Placeholder content styling */
    .placeholder-content {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 400px !important;
        text-align: center !important;
        background: var(--text-light) !important;
        border-radius: 12px !important;
        border: 2px dashed var(--secondary-nude) !important;
    }
    
    .placeholder-icon {
        font-size: 4rem !important;
        margin-bottom: 1rem !important;
        color: var(--secondary-nude) !important;
    }
    
    .placeholder-title {
        font-weight: 600 !important;
        font-size: 1.3rem !important;
        color: var(--text-dark) !important;
        margin-bottom: 0.5rem !important;
    }
    
    .placeholder-description {
        color: var(--text-dark) !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        opacity: 0.7;
    }
    
    /* Footer styling */
    .footer {
        text-align: center !important;
        margin-top: 3rem !important;
        padding-top: 2rem !important;
        border-top: 1px solid var(--secondary-nude) !important;
        color: var(--text-dark) !important;
        font-size: 0.85rem !important;
        opacity: 0.8;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.2rem !important;
        }
        
        .glass-card, .input-section, .results-card {
            padding: 1.5rem !important;
        }
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
            textColor=colors.HexColor('#967E76'),  # Using the accent nude color
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
        content.append(Paragraph("©️ 2025 Job Matching Tool | Powered by Gemini AI + Tavily", 
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
        st.markdown('<div class="main-header">🚀 AI Job Matcher</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="subtitle">
            Discover your perfect career path with AI-powered job matching
        </div>
        """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
        <div style="display: flex; align-items: flex-start;">
            <span style="font-size: 1.3rem; margin-right: 0.5rem; margin-top: 0.1rem;">💡</span>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem; color: var(--text-dark);">CAREER GUIDANCE DISCLAIMER</div>
                <div style="font-size: 0.9rem; line-height: 1.4; color: var(--text-dark); opacity: 0.9;">This tool provides general career guidance based on market data analysis. Job market conditions vary by location and time. Always verify information independently and consider consulting with career professionals for personalized advice.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        # Tagline above the input section
        st.markdown('<div class="tagline">🎯 Transform your skills into opportunities!</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # Skills input
        skills = st.text_area(
            "🛠️ Your Skills",
            placeholder="e.g., Python, JavaScript, React, SQL, Machine Learning, Project Management, Data Analysis...",
            height=100,
            help="List all your technical and soft skills separated by commas"
        )
        
        # Experience level
        experience_level = st.selectbox(
            "📊 Experience Level",
            ["Entry Level (0-2 years)", "Mid Level (2-5 years)", "Senior Level (5-10 years)", "Expert Level (10+ years)"],
            help="Select your current experience level"
        )
        
        # Preferred location
        preferred_location = st.text_input(
            "📍 Preferred Job Location",
            placeholder="e.g., New York, Remote, San Francisco, London...",
            help="Enter your preferred work location or 'Remote' for remote work"
        )
        
        # Career goals
        career_goals = st.text_area(
            "🎯 Career Goals (Optional)",
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
            st.markdown('<div class="results-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 1.8rem; font-weight: 700; color: var(--accent-nude); margin-bottom: 1.5rem; text-align: center;">✨ Your Job Market Analysis</div>', unsafe_allow_html=True)
            
            # Format the analysis results with better styling
            formatted_info = st.session_state.analysis_results.replace(
                "*Eligible Job Roles:*", "<div class='info-label'>🎯 Eligible Job Roles</div>"
            ).replace(
                "*Skill Gap Analysis:*", "<div class='info-label'>📈 Skill Gap Analysis</div>"
            ).replace(
                "*Companies Hiring:*", "<div class='info-label'>🏢 Companies Hiring</div>"
            ).replace(
                "*Salary Packages:*", "<div class='info-label'>💰 Salary Packages</div>"
            )
            
            st.markdown(formatted_info, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Create PDF report
            if st.session_state.user_profile:
                pdf_bytes = create_job_report_pdf(st.session_state.analysis_results, st.session_state.user_profile)
                if pdf_bytes:
                    st.markdown("<div style='text-align: center; margin-top: 1.5rem;'>", unsafe_allow_html=True)
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
            <div class="placeholder-content">
                <div class="placeholder-icon">🎯</div>
                <div class="placeholder-title">Ready to Find Your Dream Job?</div>
                <div class="placeholder-description">Enter your skills and preferences, then click "Analyze Job Market" to discover personalized career opportunities</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Additional features section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 2rem; font-weight: 700; color: var(--accent-nude); margin: 2rem 0;">
        🚀 What You'll Discover
    </div>
    """, unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4, gap="medium")
    
    with feature_col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Perfect Job Matches</div>
            <div class="feature-description">Discover positions that align perfectly with your unique skill set and experience level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Skill Gap Analysis</div>
            <div class="feature-description">Identify exactly which skills to develop for your dream career opportunities</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🏢</div>
            <div class="feature-title">Top Companies</div>
            <div class="feature-description">Find companies actively hiring professionals with your background and expertise</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col4:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Salary Insights</div>
            <div class="feature-description">Get real-time market salary data and compensation packages for your target roles</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        ✨ Powered by cutting-edge AI technology • Gemini Flash 2 Pro + Tavily • Real-time Job Market Intelligence<br>
        <strong>©️ 2025 AI Job Matcher - Your Gateway to Career Success</strong>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
