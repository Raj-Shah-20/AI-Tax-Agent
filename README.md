# 🤖 AI Tax Return Agent Prototype

## Overview

This project is a comprehensive prototype of an AI-powered tax return preparation agent, designed to automate basic tax calculations and generate simplified tax forms. The prototype demonstrates the core functionality of a tax preparation system while emphasizing security, validation, and user experience.

## 🚀 Features

### Core Functionality
- ✅ **Progressive Tax Calculation**: Uses official 2025 federal tax brackets (IRS IR-2024-273)
- ✅ **Multiple Filing Statuses**: Supports Single and Married Filing Jointly
- ✅ **Standard Deduction Integration**: Automatically applies standard deduction if beneficial
- ✅ **Federal Withholding**: Calculate refunds or additional taxes owed
- ✅ **Form Generation**: Creates downloadable simplified 1040 forms
- ✅ **Real-time Validation**: Client-side and server-side input validation
- ✅ **Responsive Design**: Works on desktop and mobile devices

### 🤖 AI-Powered Features
- ✅ **Smart Deduction Analysis**: AI-powered recommendations for tax optimization
- ✅ **Personalized Tax Advice**: GPT-powered insights based on your tax profile
- ✅ **Missed Opportunity Detection**: AI identifies potential deductions you might miss
- ✅ **Intelligent Strategy Recommendations**: Context-aware advice for tax planning

## 🛠️ Technical Stack

- **Backend**: Python 3.8+ with Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Templating**: Jinja2 template engine
- **PDF Generation**: ReportLab for tax form creation
- **AI Integration**: OpenAI GPT-3.5-turbo for intelligent tax advice

## 📦 Installation & Setup

### 🚀 Deploy to Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/ai-tax-agent)

1. **Click the Deploy button above** or go to [Vercel](https://vercel.com)
2. **Import your repository** from GitHub
3. **Set environment variables** (optional for AI features):
   - `OPENAI_API_KEY`: Get from [OpenAI API Keys](https://platform.openai.com/api-keys)
4. **Deploy** - Vercel will automatically build and deploy your app
5. **Access your app** at the provided Vercel URL

### 🖥️ Local Development

#### Prerequisites
```bash
Python 3.8 or higher
```

#### Installation Steps
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_tax_agent_prototype
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AI Features (Optional)**
   ```bash
   # Set environment variable for AI features
   export OPENAI_API_KEY="your_api_key_here"
   # Get API key from: https://platform.openai.com/api-keys
   ```

4. **Run the application**
   ```bash
   python index.py
   ```

5. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`

## 💡 Tax Calculation Logic

### 2025 Tax Brackets (Official IRS IR-2024-273)

**Single Filers:**
- 10% on income up to $11,925
- 12% on income $11,926 to $48,475
- 22% on income $48,476 to $103,350
- 24% on income $103,351 to $197,300
- 32% on income $197,301 to $250,525
- 35% on income $250,526 to $626,350
- 37% on income over $626,350

**Married Filing Jointly:**
- 10% on income up to $23,850
- 12% on income $23,851 to $96,950
- 22% on income $96,951 to $206,700
- 24% on income $206,701 to $394,600
- 32% on income $394,601 to $501,050
- 35% on income $501,051 to $751,600
- 37% on income over $751,600

### Standard Deductions (2025)
- **Single**: $15,000
- **Married Filing Jointly**: $30,000

> **Note**: These are the official tax brackets and standard deductions announced by the IRS in Revenue Procedure 2024-40 (IR-2024-273, October 22, 2024).

## 📋 Usage Instructions

### Basic Workflow
1. **Access the Application**: Navigate to the main page
2. **Enter Tax Information**:
   - Select filing status (Single or Married Filing Jointly)
   - Enter annual income
   - Enter itemized deductions (or 0 for standard deduction)
   - Enter federal tax withheld from paychecks
3. **Calculate Tax**: Click "Calculate My Tax Return"
4. **Review Results**: View detailed calculation breakdown including refund/owed amount
5. **Generate Form**: Download simplified 1040 form if needed

## 🧪 Testing

The application includes built-in validation and error handling. For local testing, simply run the application and test the web interface with various tax scenarios.

## 🔒 Security Features

### Input Validation
- **Range Checking**: Income and deductions must be within reasonable limits
- **Type Validation**: Ensures numeric inputs are properly formatted
- **Cross-Validation**: Prevents deductions from exceeding income
- **Sanitization**: Strips dangerous characters and validates data types

### Data Protection
- **No Persistent Storage**: Data is not saved to prevent privacy breaches
- **Error Logging**: Comprehensive logging for debugging without exposing sensitive data

## ⚠️ Limitations & Disclaimers

### Current Limitations
- **Simplified Calculations**: Does not include all tax scenarios
- **Limited Forms**: Only generates basic 1040 form
- **No State Taxes**: Federal taxes only
- **No Credits**: Tax credits not implemented

## 🔮 Future Enhancements

- **Tax Credits**: Implement common tax credits (Child Tax Credit, EITC)
- **State Tax Integration**: Add state tax calculations
- **Advanced Deductions**: Support for itemized deduction categories
- **Multi-Year Support**: Historical tax year calculations
- **Smart Document Parsing**: Allow users to upload W-2 or 1099 forms. Use OCR + NLP (e.g., Tesseract + spaCy or LayoutLM) to auto-fill fields from scanned documents
- **User Accounts & Data Security**: Add authentication (login/signup), Store user data securely (hashed, encrypted), Implement session management and form history
- **Dashboard & History**: Let users view previous returns. Visualize income vs deductions over time, Show refund trends or optimize filing strategies
- **Chatbot or Voice Assistant Interface**: Integrate with a chatbot or voice assistant to support conversational tax filing
- **Compliance & Explainability**: Add a clear audit log of calculations, Include explainable AI features (e.g., “Why this deduction?”), Prepare system for privacy regulations (GDPR, CCPA)
