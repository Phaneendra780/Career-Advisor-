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

# [Rest of your existing code remains exactly the same...]
# [Include all the Python code from the previous implementation]
# [Only the CSS theme has been changed]

def main():
    # [Keep all your existing main() function code exactly the same]
    # [Only the visual styling has been modified]

if __name__ == "__main__":
    main()
