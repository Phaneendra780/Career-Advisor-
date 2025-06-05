import streamlit as st
import requests
import json
import google.generativeai as genai
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="AI Career Advisor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .skill-tag {
        display: inline-block;
        background-color: #e1f5fe;
        color: #01579b;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
    .job-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .company-tag {
        background-color: #4caf50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

class JobMatchingTool:
    def __init__(self):
        self.setup_apis()
    
    def setup_apis(self):
        """Setup API configurations using st.secrets"""
        try:
            # Try to get API keys from secrets
            self.gemini_key = st.secrets.get("GEMINI_API_KEY")
            self.tavily_key = st.secrets.get("TAVILY_API_KEY")
            self.huggingface_key = st.secrets.get("HUGGINGFACE_API_KEY")
            
            if self.gemini_key and self.tavily_key:
                # Configure Gemini
                genai.configure(api_key=self.gemini_key)
                st.session_state.api_keys_configured = True
                st.sidebar.success("✅ APIs configured from secrets!")
            else:
                st.session_state.api_keys_configured = False
                self.show_secrets_configuration()
                
        except Exception as e:
            st.session_state.api_keys_configured = False
            self.show_secrets_configuration()
    
    def show_secrets_configuration(self):
        """Show configuration instructions for secrets"""
        st.sidebar.header("🔑 API Configuration")
        st.sidebar.error("⚠️ API keys not found in secrets!")
        
        st.sidebar.markdown("""
        **Setup st.secrets for secure API management:**
        
        1. Create `.streamlit/secrets.toml` in your project root:
        ```toml
        GEMINI_API_KEY = "your_gemini_api_key_here"
        TAVILY_API_KEY = "your_tavily_api_key_here"
        HUGGINGFACE_API_KEY = "your_huggingface_token_here"
        ```
        
        2. Add `.streamlit/` to your `.gitignore` file
        
        3. For Streamlit Cloud deployment, add secrets in the app settings
        """)
        
        # Fallback manual configuration
        with st.sidebar.expander("🔧 Manual Configuration (Fallback)"):
            gemini_key = st.text_input(
                "Gemini API Key", 
                type="password", 
                help="Get your key from Google AI Studio"
            )
            
            tavily_key = st.text_input(
                "Tavily API Key", 
                type="password",
                help="Get your key from Tavily.com"
            )
            
            huggingface_key = st.text_input(
                "Hugging Face API Token", 
                type="password",
                help="Get your free token from huggingface.co/settings/tokens"
            )
            
            if st.button("Configure APIs Manually"):
                if gemini_key and tavily_key:
                    try:
                        genai.configure(api_key=gemini_key)
                        self.gemini_key = gemini_key
                        self.tavily_key = tavily_key
                        self.huggingface_key = huggingface_key
                        st.session_state.api_keys_configured = True
                        st.success("APIs configured successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error configuring APIs: {str(e)}")
                else:
                    st.error("Please provide both Gemini and Tavily API keys")
    
    def call_huggingface(self, prompt: str, model: str = "microsoft/DialoGPT-medium") -> str:
        """Call Hugging Face Inference API - Free tier available"""
        try:
            # Use a free model that works well for text generation
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_key}" if hasattr(self, 'huggingface_key') and self.huggingface_key else None
            }
            
            # Try different free models for better results
            models_to_try = [
                "microsoft/DialoGPT-medium",
                "distilgpt2",
                "gpt2",
                "facebook/blenderbot-400M-distill"
            ]
            
            for model_name in models_to_try:
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                    
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 200,
                            "temperature": 0.7,
                            "do_sample": True
                        }
                    }
                    
                    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                            # Clean up the response
                            if generated_text.startswith(prompt):
                                generated_text = generated_text[len(prompt):].strip()
                            return generated_text if generated_text else "Analysis completed using AI."
                        elif isinstance(result, dict) and "generated_text" in result:
                            return result["generated_text"]
                    
                except Exception as model_error:
                    continue
            
            # Fallback response if all models fail
            return self.generate_fallback_analysis(prompt)
            
        except Exception as e:
            return self.generate_fallback_analysis(prompt)
    
    def generate_fallback_analysis(self, prompt: str) -> str:
        """Generate a basic analysis when AI services are unavailable"""
        if "skills" in prompt.lower():
            return """Based on your skills, here are some insights for the Indian job market:
            
            • Indian IT sector shows strong demand for technical and soft skills
            • Startups and established companies both offer good opportunities
            • Focus on continuous learning and skill development
            • Consider roles in emerging areas like AI, data science, and cloud computing
            • Bangalore, Mumbai, and Hyderabad remain top job markets"""
        
        return "Analysis completed. Please check the detailed results below."
    
    def search_tavily(self, query: str) -> Dict:
        """Search using Tavily API"""
        try:
            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}
            data = {
                "api_key": self.tavily_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "max_results": 5
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Tavily API error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error calling Tavily: {str(e)}"}
    
    def call_gemini(self, prompt: str) -> str:
        """Call Gemini AI"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"
    
    def analyze_skills_and_jobs(self, skills: List[str]) -> Dict:
        """Analyze user skills and suggest job roles for Indian market"""
        skills_text = ", ".join(skills)
        
        prompt = f"""
        Based on these skills: {skills_text}
        
        Analyze for the INDIAN job market and provide JSON response with:
        1. "eligible_jobs": List of 5-7 job roles popular in India (IT, services, startups)
        2. "skill_gaps": For each job role, list skills needed for Indian companies
        3. "learning_recommendations": Indian platforms like BYJU'S, Unacademy, Coursera India, local bootcamps
        4. "career_path": Progression path considering Indian IT industry structure
        5. "indian_market_insights": Specific insights about Indian job market trends
        
        Focus on roles in Indian IT companies, startups, service companies, and MNCs with Indian operations.
        Format as valid JSON only.
        """
        
        # Use Gemini for detailed analysis
        gemini_response = self.call_gemini(prompt)
        
        # Use Hugging Face as backup analysis
        hf_prompt = f"""
        Analyze these skills for Indian job market: {skills_text}
        Suggest 5 job roles popular in Indian IT companies, startups, and service sector.
        Consider roles at TCS, Infosys, Flipkart, Paytm, and other Indian companies.
        Include required additional skills for Indian market.
        Keep response concise and India-focused.
        """
        hf_response = self.call_huggingface(hf_prompt)
        
        try:
            # Try to parse Gemini response as JSON
            analysis = json.loads(gemini_response)
            analysis["huggingface_insights"] = hf_response
            return analysis
        except:
            # Fallback structure if JSON parsing fails
            return {
                "eligible_jobs": ["Software Developer", "Data Analyst", "Business Analyst", "Product Manager", "DevOps Engineer"],
                "skill_gaps": {
                    "Software Developer": ["Spring Boot", "Microservices", "AWS", "System Design"],
                    "Data Analyst": ["SQL", "Power BI", "Python", "Statistics"],
                    "Business Analyst": ["JIRA", "Confluence", "Process Mapping", "Domain Knowledge"],
                    "Product Manager": ["Market Research", "Roadmapping", "Analytics", "Stakeholder Management"],
                    "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "Cloud Platforms"]
                },
                "learning_recommendations": {
                    "SQL": ["W3Schools", "Coursera SQL course", "HackerRank SQL"],
                    "Python": ["Python.org tutorial", "Coursera Python", "BYJU'S Python course"],
                    "AWS": ["AWS free tier", "Coursera AWS", "A Cloud Guru"],
                    "Power BI": ["Microsoft Learn", "Coursera Power BI", "Edureka"]
                },
                "indian_market_insights": "Strong demand in Indian IT sector, growing startup ecosystem, remote work opportunities increasing",
                "gemini_raw": gemini_response,
                "huggingface_insights": hf_response
            }
    
    def get_company_and_salary_info(self, job_role: str) -> Dict:
        """Get Indian company and salary information for job role"""
        # Search for Indian companies hiring for this role
        company_query = f"top Indian companies hiring {job_role} 2024 2025 TCS Infosys Wipro startup unicorn"
        company_results = self.search_tavily(company_query)
        
        # Search for Indian salary information
        salary_query = f"{job_role} salary India INR rupees 2024 2025 Bangalore Mumbai Delhi Hyderabad Pune"
        salary_results = self.search_tavily(salary_query)
        
        # Analyze results with Gemini for Indian context
        analysis_prompt = f"""
        Based on this job role: {job_role} in INDIA
        
        Company search results: {company_results}
        Salary search results: {salary_results}
        
        Extract and provide for INDIAN job market:
        1. Top Indian companies hiring (include: TCS, Infosys, Wipro, HCL, Accenture India, Flipkart, Paytm, BYJU'S, Zomato, Swiggy, Ola, etc.)
        2. Salary ranges in INR for Indian cities (Bangalore, Mumbai, Delhi, Hyderabad, Pune, Chennai)
        3. Entry level: 3-8 LPA, Mid level: 8-20 LPA, Senior: 20-50+ LPA
        4. Key insights about Indian job market for this role
        5. City-wise opportunities and cost of living considerations
        
        Format as JSON with keys: companies, salary_ranges, market_insights, city_wise_data
        Focus on Indian IT services, startups, MNCs with Indian operations.
        """
        
        gemini_analysis = self.call_gemini(analysis_prompt)
        
        try:
            return json.loads(gemini_analysis)
        except:
            return {
                "companies": [
                    "Tata Consultancy Services (TCS)", "Infosys", "Wipro", "HCL Technologies", 
                    "Accenture India", "Flipkart", "Amazon India", "Google India", 
                    "Microsoft India", "Paytm", "BYJU'S", "Zomato", "Swiggy"
                ],
                "salary_ranges": {
                    "entry": "₹4,00,000 - ₹8,00,000 LPA",
                    "mid": "₹8,00,000 - ₹20,00,000 LPA", 
                    "senior": "₹20,00,000 - ₹50,00,000+ LPA"
                },
                "city_wise_data": {
                    "Bangalore": "Tech hub, highest salaries, high cost of living",
                    "Mumbai": "Financial center, diverse opportunities",
                    "Delhi/NCR": "Government + private sector opportunities",
                    "Hyderabad": "Growing tech city, good work-life balance",
                    "Pune": "IT services hub, lower cost than Bangalore/Mumbai",
                    "Chennai": "Manufacturing + IT, automotive sector strong"
                },
                "market_insights": "Strong demand in Indian IT sector, growing startup ecosystem",
                "raw_analysis": gemini_analysis
            }
    
    def create_skill_gap_visualization(self, current_skills: List[str], required_skills: Dict):
        """Create visualization for skill gaps"""
        # Prepare data for visualization
        all_skills = set()
        for job_skills in required_skills.values():
            all_skills.update(job_skills)
        
        skill_data = []
        for skill in all_skills:
            has_skill = skill in current_skills
            job_count = sum(1 for job_skills in required_skills.values() if skill in job_skills)
            skill_data.append({
                "Skill": skill,
                "Have": "Yes" if has_skill else "No",
                "Job_Demand": job_count
            })
        
        df = pd.DataFrame(skill_data)
        
        # Create bubble chart
        fig = px.scatter(
            df, 
            x="Skill", 
            y="Job_Demand",
            color="Have",
            size="Job_Demand",
            title="Skill Gap Analysis",
            labels={"Job_Demand": "Number of Jobs Requiring This Skill"}
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        return fig

def main():
    st.markdown('<h1 class="main-header">🇮🇳 AI Career Advisor - India Edition</h1>', unsafe_allow_html=True)
    
    # Initialize the tool
    tool = JobMatchingTool()
    
    if not st.session_state.get('api_keys_configured', False):
        st.warning("⚠️ Please configure your API keys using st.secrets or the manual fallback option.")
        st.info("""
        **For secure API management, create `.streamlit/secrets.toml`:**
        ```toml
        GEMINI_API_KEY = "your_gemini_api_key_here" 
        TAVILY_API_KEY = "your_tavily_api_key_here"
        HUGGINGFACE_API_KEY = "your_huggingface_token_here"
        ```
        
        **Get your API keys:**
        - **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
        - **Tavily API**: [Tavily.com](https://tavily.com)
        - **Hugging Face**: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (Free!)
        """)
        return
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Your Skills")
        
        # Skill input methods
        input_method = st.radio(
            "How would you like to input your skills?",
            ["Manual Entry", "Upload Resume", "Skill Categories"]
        )
        
        skills = []
        
        if input_method == "Manual Entry":
            skills_input = st.text_area(
                "Enter your skills (comma-separated)",
                placeholder="Python, Machine Learning, SQL, Project Management, Communication"
            )
            if skills_input:
                skills = [skill.strip() for skill in skills_input.split(",")]
        
        elif input_method == "Upload Resume":
            uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx', 'txt'])
            if uploaded_file:
                st.info("Resume upload feature - would extract skills using AI")
                # Placeholder for resume parsing
                skills = ["Python", "Data Analysis", "Machine Learning", "SQL"]
        
        elif input_method == "Skill Categories":
            st.subheader("Select your skills by category")
            
            tech_skills = st.multiselect(
                "Technical Skills",
                ["Python", "Java", "JavaScript", "SQL", "Machine Learning", "Data Analysis", 
                 "Spring Boot", "React", "Node.js", "AWS", "Azure", "Docker", "Kubernetes",
                 "Power BI", "Tableau", "MongoDB", "PostgreSQL", "Git", "Jenkins"]
            )
            
            soft_skills = st.multiselect(
                "Soft Skills", 
                ["Leadership", "Communication", "Project Management", "Problem Solving",
                 "Team Collaboration", "Critical Thinking", "Adaptability", "Client Interaction",
                 "Stakeholder Management", "Agile/Scrum", "Cross-functional Collaboration"]
            )
            
            domain_skills = st.multiselect(
                "Domain Skills",
                ["Banking & Finance", "Healthcare", "E-commerce", "EdTech", "FinTech", 
                 "Digital Marketing", "Supply Chain", "Manufacturing", "Retail", "Insurance",
                 "Government/Public Sector", "Startup Ecosystem", "IT Services"]
            )
            
            skills = tech_skills + soft_skills + domain_skills
        
        # Display selected skills
        if skills:
            st.subheader("Your Skills:")
            skills_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in skills])
            st.markdown(skills_html, unsafe_allow_html=True)
    
    with col2:
        st.header("⚙️ Analysis Options")
        
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Quick", "Detailed", "Comprehensive"]
        )
        
        focus_areas = st.multiselect(
            "Focus Areas",
            ["Job Matching", "Skill Gaps", "Salary Analysis", "Company Research", "Learning Path"]
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Fresher (0-2 years)", "Junior (2-5 years)", "Mid-Level (5-10 years)", 
             "Senior (10+ years)", "Lead/Manager"]
        )
        
        location_preference = st.multiselect(
            "Preferred Cities",
            ["Bangalore", "Mumbai", "Delhi/NCR", "Hyderabad", "Pune", "Chennai", 
             "Kolkata", "Ahmedabad", "Remote", "Any Location"],
            default=["Bangalore", "Mumbai"]
        )
    
    # Analysis button
    if st.button("🔍 Analyze My Career Options", type="primary"):
        if not skills:
            st.error("Please enter your skills first!")
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Skill and Job Analysis
        status_text.text("Analyzing your skills and matching job roles...")
        progress_bar.progress(20)
        
        analysis = tool.analyze_skills_and_jobs(skills)
        
        # Step 2: Job Role Analysis
        status_text.text("Researching job market and companies...")
        progress_bar.progress(50)
        
        job_info = {}
        for job in analysis.get("eligible_jobs", []):
            job_info[job] = tool.get_company_and_salary_info(job)
        
        progress_bar.progress(80)
        status_text.text("Generating recommendations...")
        
        # Step 3: Display Results
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        # Results Display
        st.header("📊 Your Career Analysis Results")
        
        # Job Matches
        st.subheader("🎯 Eligible Job Roles")
        
        for i, job in enumerate(analysis.get("eligible_jobs", [])):
            with st.expander(f"{job} - Click to expand"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Skill Gaps:**")
                    gaps = analysis.get("skill_gaps", {}).get(job, [])
                    for gap in gaps:
                        st.write(f"• {gap}")
                
                with col2:
                    st.write("**Top Indian Companies:**")
                    companies = job_info.get(job, {}).get("companies", [])
                    for company in companies[:6]:
                        st.write(f"• {company}")
                
                # Salary information in INR
                salary_info = job_info.get(job, {}).get("salary_ranges", {})
                if salary_info:
                    st.write("**Salary Ranges (INR):**")
                    for level, salary in salary_info.items():
                        st.write(f"• {level.title()}: {salary}")
                
                # City-wise information
                city_info = job_info.get(job, {}).get("city_wise_data", {})
                if city_info:
                    st.write("**City-wise Opportunities:**")
                    for city, info in city_info.items():
                        st.write(f"• **{city}**: {info}")
        
        # Skill Gap Visualization
        if analysis.get("skill_gaps"):
            st.subheader("📈 Skill Gap Analysis")
            fig = tool.create_skill_gap_visualization(skills, analysis["skill_gaps"])
            st.plotly_chart(fig, use_container_width=True)
        
        # Career Path
        if analysis.get("career_path"):
            st.subheader("🛤️ Suggested Career Path in India")
            st.write(analysis["career_path"])
        
        # Learning Resources - India focused
        st.subheader("📚 Learning Recommendations (India-focused)")
        st.info("💡 **Popular Indian Learning Platforms**: BYJU'S, Unacademy, Coursera India, Udemy India, Simplilearn, Great Learning")
        
        recommendations = analysis.get("learning_recommendations", {})
        
        learning_df_data = []
        for skill, resources in recommendations.items():
            for resource in resources:
                learning_df_data.append({"Skill": skill, "Resource": resource, "Type": "Online Course"})
        
        # Add Indian-specific resources
        indian_resources = [
            {"Skill": "Data Science", "Resource": "Great Learning - Data Science", "Type": "Indian Platform"},
            {"Skill": "Full Stack Development", "Resource": "Masai School", "Type": "Indian Bootcamp"},
            {"Skill": "AI/ML", "Resource": "IIT Madras Online", "Type": "Premium Indian"},
            {"Skill": "Cloud Computing", "Resource": "Simplilearn AWS", "Type": "Indian Platform"},
            {"Skill": "Digital Marketing", "Resource": "Digital Vidya", "Type": "Indian Specialized"}
        ]
        
        learning_df_data.extend(indian_resources)
        
        if learning_df_data:
            learning_df = pd.DataFrame(learning_df_data)
            st.dataframe(learning_df, use_container_width=True)
        
        # Indian Market Insights
        st.subheader("🇮🇳 Indian Job Market Insights")
        
        if analysis.get("indian_market_insights"):
            st.info(f"💡 **Market Insight**: {analysis['indian_market_insights']}")
        
        # City-wise salary comparison
        city_salary_data = []
        for job, info in job_info.items():
            city_data = info.get("city_wise_data", {})
            for city, details in city_data.items():
                city_salary_data.append({
                    "Job Role": job,
                    "City": city,
                    "Details": details
                })
        
        if city_salary_data:
            st.subheader("🏙️ City-wise Job Market Analysis")
            city_df = pd.DataFrame(city_salary_data)
            st.dataframe(city_df, use_container_width=True)
        
        # AI Insights section
        if analysis.get("huggingface_insights"):
            st.subheader("🤖 Additional AI Insights")
            st.info(analysis["huggingface_insights"])
        
        # Raw insights (expandable)
        with st.expander("🔧 Technical Details (Raw Data)"):
            st.json(analysis)

if __name__ == "__main__":
    main()
