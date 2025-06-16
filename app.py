import streamlit as st
import os
import pandas as pd
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from datetime import datetime
import re
import time

# Set page configuration with custom theme
st.set_page_config(
    page_title="Job Matching Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Enhanced CSS with cream theme and advanced animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;500;600;700&display=swap');
    
    /* Cream professional color palette */
    :root {
        --primary-cream: #FFF8E7;
        --secondary-cream: #F5F0E1;
        --warm-cream: #F0E8D6;
        --rich-cream: #E8DCC0;
        --accent-brown: #8B7355;
        --dark-brown: #6B5B47;
        --text-dark: #2C2416;
        --text-medium: #4A3D2A;
        --text-light: #FFFFFF;
        --glass-bg: rgba(255, 248, 231, 0.85);
        --glass-border: rgba(245, 240, 225, 0.9);
        --shadow-soft: 0 4px 16px -4px rgba(43, 36, 22, 0.08);
        --shadow-medium: 0 8px 32px -8px rgba(43, 36, 22, 0.12);
        --shadow-heavy: 0 16px 48px -12px rgba(43, 36, 22, 0.18);
        --gradient-warm: linear-gradient(135deg, #FFF8E7 0%, #F5F0E1 50%, #F0E8D6 100%);
        --gradient-rich: linear-gradient(135deg, #E8DCC0 0%, #8B7355 100%);
    }
    
    /* Global font styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .main-header {
        font-family: 'Playfair Display', serif !important;
    }
    
    /* Animated background with cream gradients */
    .stApp {
        background: linear-gradient(-45deg, #FFF8E7, #F5F0E1, #F0E8D6, #E8DCC0, #D4C4A8);
        background-size: 400% 400%;
        animation: creamGradientBG 20s ease infinite;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    @keyframes creamGradientBG {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 0%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Enhanced floating particles */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        overflow: hidden;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        background: rgba(139, 115, 85, 0.15);
        border-radius: 50%;
        animation: floatParticle linear infinite;
        filter: blur(1px);
    }
    
    .particle:nth-child(odd) {
        background: rgba(232, 220, 192, 0.25);
        animation: floatParticleReverse linear infinite;
    }
    
    @keyframes floatParticle {
        0% { 
            transform: translateY(100vh) translateX(-50px) scale(0);
            opacity: 0;
        }
        10% { 
            opacity: 1;
            transform: translateY(90vh) translateX(-40px) scale(1);
        }
        90% { 
            opacity: 0.8;
            transform: translateY(10vh) translateX(40px) scale(0.8);
        }
        100% { 
            transform: translateY(-10vh) translateX(50px) scale(0);
            opacity: 0;
        }
    }
    
    @keyframes floatParticleReverse {
        0% { 
            transform: translateY(-10vh) translateX(50px) scale(0);
            opacity: 0;
        }
        10% { 
            opacity: 1;
            transform: translateY(0vh) translateX(40px) scale(1);
        }
        90% { 
            opacity: 0.8;
            transform: translateY(90vh) translateX(-40px) scale(0.8);
        }
        100% { 
            transform: translateY(100vh) translateX(-50px) scale(0);
            opacity: 0;
        }
    }
    
    /* Container with enhanced glass morphism */
    .main .block-container {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-radius: 20px !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: var(--shadow-medium) !important;
        padding: 3rem !important;
        margin-top: 1rem !important;
        animation: containerFadeIn 1.2s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .main .block-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-rich);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes containerFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(40px) scale(0.95);
            filter: blur(10px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1);
            filter: blur(0px);
        }
    }
    
    @keyframes shimmer {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    /* Header with typewriter effect */
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        color: var(--accent-brown) !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        letter-spacing: -1px;
        animation: typewriter 2s steps(20, end), blink 0.8s step-end infinite alternate;
        position: relative;
        overflow: hidden;
        white-space: nowrap;
        border-right: 3px solid var(--accent-brown);
    }
    
    @keyframes typewriter {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink {
        50% { border-color: transparent; }
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 400;
        color: var(--text-medium);
        margin-bottom: 2.5rem;
        opacity: 0;
        animation: subtitleFadeIn 1s ease-out 1s forwards;
        position: relative;
    }
    
    .subtitle::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 2px;
        background: var(--gradient-rich);
        animation: lineGrow 1s ease-out 1.5s forwards;
        transform-origin: center;
        scale: 0;
    }
    
    @keyframes subtitleFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes lineGrow {
        from { scale: 0; }
        to { scale: 1; }
    }
    
    /* Enhanced card styling with hover animations */
    .glass-card {
        background: var(--text-light) !important;
        border-radius: 16px !important;
        border: 1px solid var(--rich-cream) !important;
        padding: 2.5rem !important;
        margin-bottom: 2rem !important;
        box-shadow: var(--shadow-soft) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(139, 115, 85, 0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: var(--shadow-heavy) !important;
        border-color: var(--accent-brown) !important;
        background: var(--primary-cream) !important;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    /* Input section with staggered animations */
    .input-section {
        background: var(--text-light) !important;
        border-radius: 20px !important;
        border: 1px solid var(--rich-cream) !important;
        padding: 3rem !important;
        margin-bottom: 2.5rem !important;
        box-shadow: var(--shadow-soft) !important;
        animation: slideInLeft 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.5s both;
        position: relative;
        overflow: hidden;
    }
    
    .input-section::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 4px;
        height: 100%;
        background: var(--gradient-rich);
        animation: heightGrow 1s ease-out 1s forwards;
        transform-origin: top;
        scale: 1 0;
    }
    
    @keyframes slideInLeft {
        from { 
            opacity: 0; 
            transform: translateX(-50px);
        }
        to { 
            opacity: 1; 
            transform: translateX(0);
        }
    }
    
    @keyframes heightGrow {
        from { scale: 1 0; }
        to { scale: 1 1; }
    }
    
    /* Animated taglines */
    .tagline {
        text-align: center !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: var(--accent-brown) !important;
        margin: 2rem auto !important;
        padding: 1rem 2rem !important;
        border-radius: 50px !important;
        background: var(--text-light) !important;
        border: 2px solid var(--rich-cream) !important;
        max-width: 600px !important;
        animation: taglineBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.8s both;
        position: relative;
        box-shadow: var(--shadow-soft);
    }
    
    .tagline::before {
        content: '';
        position: absolute;
        top: 50%;
        left: -8px;
        transform: translateY(-50%);
        width: 16px;
        height: 16px;
        background: var(--accent-brown);
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes taglineBounce {
        from { 
            opacity: 0; 
            transform: scale(0.3) rotate(-10deg);
        }
        to { 
            opacity: 1; 
            transform: scale(1) rotate(0deg);
        }
    }
    
    @keyframes pulse {
        0%, 100% { transform: translateY(-50%) scale(1); opacity: 1; }
        50% { transform: translateY(-50%) scale(1.2); opacity: 0.7; }
    }
    
    .dark-tagline {
        text-align: center !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: var(--text-light) !important;
        margin: 2rem auto !important;
        padding: 1rem 2rem !important;
        border-radius: 50px !important;
        background: var(--gradient-rich) !important;
        max-width: 600px !important;
        animation: slideInRight 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
        box-shadow: var(--shadow-medium);
        position: relative;
        overflow: hidden;
    }
    
    .dark-tagline::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: ripple 3s ease-out infinite;
    }
    
    @keyframes slideInRight {
        from { 
            opacity: 0; 
            transform: translateX(50px);
        }
        to { 
            opacity: 1; 
            transform: translateX(0);
        }
    }
    
    @keyframes ripple {
        0% {
            width: 0;
            height: 0;
            opacity: 0.8;
        }
        100% {
            width: 300px;
            height: 300px;
            opacity: 0;
        }
    }
    
    /* Enhanced button with multiple animations */
    .stButton > button {
        background: var(--gradient-rich) !important;
        color: var(--text-light) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: 50px !important;
        padding: 1rem 2.5rem !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-soft);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        transition: all 0.6s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: var(--shadow-heavy) !important;
        background: var(--dark-brown) !important;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.02) !important;
    }
    
    /* Feature boxes with staggered entrance */
    .feature-box {
        background: var(--text-light) !important;
        border-radius: 20px !important;
        border: 1px solid var(--rich-cream) !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: 100% !important;
        animation: featureSlideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both;
        position: relative;
        overflow: hidden;
    }
    
    .feature-box:nth-child(1) { animation-delay: 0.1s; }
    .feature-box:nth-child(2) { animation-delay: 0.2s; }
    .feature-box:nth-child(3) { animation-delay: 0.3s; }
    .feature-box:nth-child(4) { animation-delay: 0.4s; }
    
    .feature-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-rich);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-10px) scale(1.03) !important;
        box-shadow: var(--shadow-heavy) !important;
        border-color: var(--accent-brown) !important;
        background: var(--primary-cream) !important;
    }
    
    .feature-box:hover::before {
        transform: scaleX(1);
    }
    
    @keyframes featureSlideUp {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.9);
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1);
        }
    }
    
    .feature-icon {
        font-size: 3rem !important;
        margin-bottom: 1.5rem !important;
        color: var(--accent-brown) !important;
        animation: iconBounce 2s ease-in-out infinite;
        display: inline-block;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-5px) scale(1.1); }
    }
    
    .feature-title {
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        color: var(--text-dark) !important;
        margin-bottom: 1rem !important;
    }
    
    .feature-description {
        color: var(--text-medium) !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        opacity: 0.9;
    }
    
    /* Results section with dramatic entrance */
    .results-card {
        background: var(--text-light) !important;
        border-radius: 20px !important;
        border: 1px solid var(--rich-cream) !important;
        padding: 3rem !important;
        box-shadow: var(--shadow-medium) !important;
        min-height: 400px !important;
        animation: resultsSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .results-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--gradient-rich);
        border-radius: 22px;
        z-index: -1;
        animation: borderGlow 3s ease-in-out infinite;
    }
    
    @keyframes resultsSlideIn {
        from { 
            opacity: 0; 
            transform: translateY(50px) scale(0.95);
            filter: blur(5px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1);
            filter: blur(0);
        }
    }
    
    @keyframes borderGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .info-label {
        font-weight: 700 !important;
        color: var(--accent-brown) !important;
        font-size: 1.3rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        position: relative;
        padding-left: 2rem;
    }
    
    .info-label::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 1rem;
        height: 0.3rem;
        background: var(--gradient-rich);
        border-radius: 2px;
        animation: labelSlide 0.5s ease-out;
    }
    
    @keyframes labelSlide {
        from { width: 0; }
        to { width: 1rem; }
    }
    
    /* Text styling with subtle animations */
    .stMarkdown, .stText, p, div, span {
        color: var(--text-dark) !important;
        transition: color 0.3s ease;
    }
    
    /* Enhanced input fields */
    .stTextArea > div > div > textarea,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: var(--primary-cream) !important;
        color: var(--text-dark) !important;
        border: 2px solid var(--rich-cream) !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 1rem !important;
        padding: 0.8rem !important;
    }
    
    .stTextArea > div > div > textarea:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--accent-brown) !important;
        box-shadow: 0 0 0 4px rgba(139, 115, 85, 0.1) !important;
        background: var(--text-light) !important;
        transform: scale(1.02) !important;
    }
    
    .stTextArea > div > div > textarea::placeholder,
    .stTextInput > div > div > input::placeholder {
        color: rgba(44, 36, 22, 0.5) !important;
        font-style: italic;
    }
    
    /* Label styling */
    .stTextArea > label,
    .stTextInput > label,
    .stSelectbox > label {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Enhanced disclaimer */
    .disclaimer-box {
        background: rgba(139, 115, 85, 0.08) !important;
        border: 1px solid var(--rich-cream) !important;
        border-left: 5px solid var(--accent-brown) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        color: var(--text-dark) !important;
        animation: disclaimerSlide 0.6s ease-out 0.3s both;
        position: relative;
        overflow: hidden;
    }
    
    .disclaimer-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background: rgba(139, 115, 85, 0.05);
        animation: fillDisclaimer 2s ease-out 1s forwards;
    }
    
    @keyframes disclaimerSlide {
        from { 
            opacity: 0; 
            transform: translateX(-30px);
        }
        to { 
            opacity: 1; 
            transform: translateX(0);
        }
    }
    
    @keyframes fillDisclaimer {
        from { width: 0; }
        to { width: 100%; }
    }
    
    /* Placeholder with breathing animation */
    .placeholder-content {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 400px !important;
        text-align: center !important;
        background: var(--text-light) !important;
        border-radius: 20px !important;
        border: 3px dashed var(--rich-cream) !important;
        animation: breathe 4s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .placeholder-content::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(139, 115, 85, 0.05) 0%, transparent 70%);
        border-radius: 50%;
        animation: expandingCircle 6s ease-in-out infinite;
    }
    
    @keyframes breathe {
        0%, 100% { 
            transform: scale(1);
            border-color: var(--rich-cream);
        }
        50% { 
            transform: scale(1.02);
            border-color: var(--accent-brown);
        }
    }
    
    @keyframes expandingCircle {
        0%, 100% { 
            transform: translate(-50%, -50%) scale(0.8);
            opacity: 0.3;
        }
        50% { 
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 0.1;
        }
    }
    
    .placeholder-icon {
        font-size: 4.5rem !important;
        margin-bottom: 1.5rem !important;
        color: var(--accent-brown) !important;
        animation: iconFloat 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    
    .placeholder-title {
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        color: var(--text-dark) !important;
        margin-bottom: 1rem !important;
        position: relative;
        z-index: 1;
    }
    
    .placeholder-description {
        color: var(--text-medium) !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        opacity: 0.8;
        position: relative;
        z-index: 1;
    }
    
    /* Loading animation with cream theme */
    .loading-spinner {
        animation: spin 1s linear infinite;
        width: 40px;
        height: 40px;
        border: 4px solid var(--rich-cream);
        border-top: 4px solid var(--accent-brown);
        border-radius: 50%;
        margin: 30px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Footer with subtle animation */
    .footer {
        text-align: center !important;
        margin-top: 4rem !important;
        padding-top: 2.5rem !important;
        border-top: 2px solid var(--rich-cream) !important;
        color: var(--text-medium) !important;
        font-size: 0.9rem !important;
        opacity: 0;
        animation: footerFadeIn 1s ease-out 2s forwards;
        position: relative;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: -2px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 2px;
        background: var(--gradient-rich);
        animation: footerLineGrow 1s ease-out 2.5s forwards;
    }
    
    @keyframes footerFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 0.9; transform: translateY(0); }
    }
    
    @keyframes footerLineGrow {
        from { width: 0; }
        to { width: 100px; }
    }
    
    /* Responsive design with enhanced mobile experience */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem !important;
            animation: mobileTypewriter 1.5s steps(15, end), blink 0.8s step-end infinite alternate;
        }
        
        @keyframes mobileTypewriter {
            from { width: 0; }
            to { width: 100%; }
        }
        
        .glass-card, .input-section, .results-card {
            padding: 2rem !important;
        }
        
        .feature-box {
            margin-bottom: 1.5rem !important;
            padding: 1.5rem !important;
        }
        
        .main .block-container {
            padding: 2rem !important;
        }
        
        .tagline, .dark-tagline {
            font-size: 1.1rem !important;
            padding: 0.8rem 1.5rem !important;
        }
        
        .particles {
            display: none; /* Hide particles on mobile for better performance */
        }
    }
    
    /* Scroll animations */
    @media (prefers-reduced-motion: no-preference) {
        .scroll-animate {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .scroll-animate.visible {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        :root {
            --primary-cream: #FFFFFF;
            --secondary-cream: #F0F0F0;
            --warm-cream: #E0E0E0;
            --rich-cream: #D0D0D0;
            --accent-brown: #000000;
            --dark-brown: #333333;
            --text-dark: #000000;
            --text-medium: #333333;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced floating particles with cream theme
st.markdown("""
<div class="particles" id="particles-js"></div>
<script>
    // Create enhanced floating particles
    document.addEventListener('DOMContentLoaded', function() {
        const particles = document.querySelector('.particles');
        if (!particles) return;
        
        const colors = ['#FFF8E7', '#F5F0E1', '#F0E8D6', '#E8DCC0', '#D4C4A8'];
        const shapes = ['circle', 'square', 'triangle'];
        
        // Clear existing particles
        particles.innerHTML = '';
        
        // Create more sophisticated particles
        for (let i = 0; i < 40; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            
            // Random properties with more variation
            const size = Math.random() * 20 + 8;
            const posX = Math.random() * 100;
            const posY = Math.random() * 100 + 100;
            const duration = Math.random() * 25 + 15;
            const delay = Math.random() * 8;
            const color = colors[Math.floor(Math.random() * colors.length)];
            const opacity = Math.random() * 0.3 + 0.1;
            
            // Apply styles
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}%`;
            particle.style.top = `${posY}%`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `${delay}s`;
            particle.style.backgroundColor = color;
            particle.style.opacity = opacity;
            
            // Add slight variations
            if (Math.random() > 0.7) {
                particle.style.borderRadius = '20%';
            }
            if (Math.random() > 0.8) {
                particle.style.filter = 'blur(2px)';
            }
            
            particles.appendChild(particle);
        }
        
        // Add scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);
        
        // Observe elements for scroll animations
        document.querySelectorAll('.scroll-animate').forEach(el => {
            observer.observe(el);
        });
    });
</script>
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
            # Add custom spinner with cream theme
            st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
                <div class="loading-spinner"></div>
            </div>
            <div style="text-align: center; color: var(--accent-brown); font-weight: 600; font-size: 1.1rem; margin-top: 1rem;">
                ✨ Discovering your perfect career matches...
            </div>
            """, unsafe_allow_html=True)
            
            response = agent.run(query)
            return response.content.strip()
    except Exception as e:
        st.error(f"Error analyzing job match: {e}")
        return None

def main():
    # Initialize session state
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    # Header with enhanced animation
    st.markdown('<div class="main-header">🚀 AI Career Navigator</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="subtitle">
        Transform your potential into opportunity with intelligent career matching
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced disclaimer with better styling
    st.markdown("""
    <div class="disclaimer-box">
        <div style="display: flex; align-items: flex-start;">
            <span style="font-size: 1.5rem; margin-right: 1rem; margin-top: 0.2rem;">💡</span>
            <div>
                <div style="font-weight: 700; margin-bottom: 0.5rem; color: var(--accent-brown); font-size: 1.1rem;">INTELLIGENT CAREER GUIDANCE</div>
                <div style="font-size: 1rem; line-height: 1.6; color: var(--text-dark); opacity: 0.9;">This advanced AI tool analyzes real-time market data to provide personalized career insights. While our recommendations are based on current industry trends and data, job markets are dynamic. We recommend using this as a starting point for your career exploration and consulting with career professionals for comprehensive guidance.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Section with enhanced styling
    st.markdown('<div class="tagline">🎯 Unlock your career potential with AI-powered insights!</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-section scroll-animate">', unsafe_allow_html=True)
    
    # Enhanced skills input with better UX
    skills = st.text_area(
        "🛠️ Your Professional Skills & Expertise",
        placeholder="e.g., Python, JavaScript, React, SQL, Machine Learning, Project Management, Data Analysis, Leadership, Communication, Problem Solving...",
        height=120,
        help="💡 Include both technical skills (programming languages, tools, software) and soft skills (leadership, communication, teamwork). The more detailed, the better your matches!"
    )
    
    # Experience level with enhanced options
    experience_level = st.selectbox(
        "📊 Professional Experience Level",
        [
            "🌱 Entry Level (0-2 years) - Recent graduate or career starter",
            "🚀 Mid Level (2-5 years) - Developing expertise and taking on more responsibility", 
            "⭐ Senior Level (5-10 years) - Experienced professional with proven track record",
            "🎯 Expert Level (10+ years) - Industry leader with extensive experience"
        ],
        help="📈 Select the option that best describes your current professional standing"
    )
    
    # Preferred location with enhanced input
    preferred_location = st.text_input(
        "📍 Preferred Work Location",
        placeholder="e.g., New York, Remote, San Francisco, London, Hybrid (City Name)...",
        help="🌍 Specify your ideal work location. You can mention 'Remote', specific cities, or 'Hybrid' options"
    )
    
    # Career goals with better guidance
    career_goals = st.text_area(
        "🎯 Career Aspirations & Goals (Optional but Recommended)",
        placeholder="e.g., Become a Senior Software Engineer at a tech startup, Transition into Data Science from finance, Lead a product team at a Fortune 500 company, Start my own consulting business...",
        height=100,
        help="🚀 Share your career dreams! This helps us provide more targeted recommendations and identify the right growth path for you"
    )
    
    # Enhanced analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Discover My Career Opportunities", key="analyze_btn", use_container_width=True):
            if skills.strip():
                st.session_state.analyze_clicked = True
                
                # Perform analysis with enhanced feedback
                st.markdown("""
                <div style="text-align: center; margin: 2rem 0; padding: 1.5rem; background: var(--primary-cream); border-radius: 15px; border: 1px solid var(--rich-cream);">
                    <div style="font-size: 1.3rem; font-weight: 600; color: var(--accent-brown); margin-bottom: 0.5rem;">🔮 AI Analysis in Progress</div>
                    <div style="color: var(--text-medium); font-size: 1rem;">Our AI is scanning thousands of job opportunities and market trends to find your perfect matches...</div>
                </div>
                """, unsafe_allow_html=True)
                
                analysis_result = analyze_job_match(skills, experience_level, preferred_location, career_goals)
                st.session_state.analysis_results = analysis_result
                
                if analysis_result:
                    st.success("✨ Analysis complete! Your personalized career roadmap is ready below.")
                    st.balloons()  # Celebratory animation
            else:
                st.error("⚠️ Please enter your skills to begin the career analysis.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results Section with enhanced presentation
    st.markdown('<div class="dark-tagline scroll-animate">📊 Your personalized career intelligence awaits!</div>', unsafe_allow_html=True)
    
    # Display results if available
    if st.session_state.analysis_results:
        st.markdown('<div class="results-card scroll-animate">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2.5rem;">
            <div style="font-size: 2.2rem; font-weight: 800; color: var(--accent-brown); margin-bottom: 0.5rem;">✨ Your Career Intelligence Report</div>
            <div style="font-size: 1.1rem; color: var(--text-medium); opacity: 0.9;">Powered by real-time market data and AI analysis</div>
            <div style="width: 80px; height: 3px; background: var(--gradient-rich); margin: 1rem auto; border-radius: 2px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced formatting with better visual hierarchy
        formatted_info = st.session_state.analysis_results.replace(
            "*Eligible Job Roles:*", "<div class='info-label'>🎯 Perfect Job Matches for You</div>"
        ).replace(
            "*Skill Gap Analysis:*", "<div class='info-label'>📈 Skills Development Roadmap</div>"
        ).replace(
            "*Companies Hiring:*", "<div class='info-label'>🏢 Companies Looking for Your Talents</div>"
        ).replace(
            "*Salary Packages:*", "<div class='info-label'>💰 Earning Potential & Compensation</div>"
        )
        
        # Add download option for results
        st.markdown("""
        <div style="background: var(--primary-cream); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; border: 1px solid var(--rich-cream);">
        """, unsafe_allow_html=True)
        
        st.markdown(formatted_info, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Save Report", use_container_width=True):
                st.info("💡 Tip: Use your browser's print function (Ctrl+P) to save this report as PDF!")
        with col2:
            if st.button("🔄 New Analysis", use_container_width=True):
                st.session_state.analysis_results = None
                st.session_state.analyze_clicked = False
                st.rerun()
        with col3:
            if st.button("📧 Share Results", use_container_width=True):
                st.info("💡 Copy the URL to share your results, or use the print function to create a PDF!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="placeholder-content scroll-animate">
            <div class="placeholder-icon">🎯</div>
            <div class="placeholder-title">Ready to Discover Your Dream Career?</div>
            <div class="placeholder-description">
                Enter your skills and preferences above, then click "Discover My Career Opportunities" to unlock personalized insights powered by real-time market data and AI analysis.
                <br><br>
                <strong>✨ Get ready to explore:</strong><br>
                • Perfect job matches tailored to your skills<br>
                • Skills development roadmap for growth<br>
                • Companies actively seeking your talents<br>
                • Real salary data and earning potential
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced features section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0;">
        <div style="font-size: 2.5rem; font-weight: 800; color: var(--accent-brown); margin-bottom: 1rem;">
            🚀 Discover What Awaits You
        </div>
        <div style="font-size: 1.2rem; color: var(--text-medium); opacity: 0.9; max-width: 600px; margin: 0 auto;">
            Our AI-powered platform analyzes thousands of data points to deliver personalized career insights
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4, gap="large")
    
    with feature_col1:
        st.markdown("""
        <div class="feature-box scroll-animate">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Job Matching</div>
            <div class="feature-description">Advanced AI algorithms analyze your unique skill profile to identify positions where you'll excel and grow</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="feature-box scroll-animate">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Growth Strategy</div>
            <div class="feature-description">Get a personalized skills development roadmap with prioritized learning paths based on market demand</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="feature-box scroll-animate">
            <div class="feature-icon">🏢</div>
            <div class="feature-title">Company Intelligence</div>
            <div class="feature-description">Discover companies actively hiring for your skillset, from innovative startups to established industry leaders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col4:
        st.markdown("""
        <div class="feature-box scroll-animate">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Market Insights</div>
            <div class="feature-description">Access real-time salary data, compensation packages, and career progression potential in your field</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("""
    <div class="footer">
        ✨ Powered by cutting-edge AI technology • Gemini Flash 2 Pro + Tavily Search • Real-time Job Market Intelligence<br>
        <strong>©️ 2025 AI Career Navigator - Transform Your Future with Intelligent Career Guidance</strong><br>
        <div style="margin-top: 1rem; font-size: 0.85rem; opacity: 0.7;">
            🌟 Helping professionals discover their perfect career path through data-driven insights
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
