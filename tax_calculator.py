from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import openai
import json
import logging
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 2025 Tax Brackets (Official IRS IR-2024-273)
TAX_BRACKETS_2025 = {
    'single': [
        (11925, 0.10),
        (48475, 0.12),
        (103350, 0.22),
        (197300, 0.24),
        (250525, 0.32),
        (626350, 0.35),
        (float('inf'), 0.37)
    ],
    'married': [
        (23850, 0.10),
        (96950, 0.12),
        (206700, 0.22),
        (394600, 0.24),
        (501050, 0.32),
        (751600, 0.35),
        (float('inf'), 0.37)
    ]
}

# 2025 Standard Deductions (Official IRS IR-2024-273)
STANDARD_DEDUCTIONS_2025 = {
    'single': 15000,
    'married': 30000
}



# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_ENABLED = OPENAI_API_KEY is not None

# Initialize OpenAI client if API key is available
openai_client = None
if LLM_ENABLED:
    try:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logging.info(f"OpenAI client initialized successfully")
    except Exception as e:
        logging.warning(f"Failed to initialize OpenAI client: {e}")
        LLM_ENABLED = False
        openai_client = None

def validate_input(income_str, deductions_str, status, withheld_str=None):
    """
    Comprehensive input validation with security considerations
    """
    errors = []
    
    # Status validation
    if not status or status not in ['single', 'married']:
        errors.append("Please select a valid filing status.")
    
    # Income validation
    if not income_str:
        errors.append("Income is required.")
    else:
        try:
            income = float(income_str)
            if income < 0:
                errors.append("Income cannot be negative.")
            elif income > 10000000:  # Reasonable upper limit
                errors.append("Income amount seems unusually high. Please verify.")
        except ValueError:
            errors.append("Income must be a valid number.")
    
    # Deductions validation
    if not deductions_str:
        errors.append("Deductions field is required.")
    else:
        try:
            deductions = float(deductions_str)
            if deductions < 0:
                errors.append("Deductions cannot be negative.")
            elif deductions > 1000000:  # Reasonable upper limit
                errors.append("Deductions amount seems unusually high. Please verify.")
        except ValueError:
            errors.append("Deductions must be a valid number.")
    
    # Federal tax withheld validation
    if withheld_str is not None:
        if not withheld_str:
            errors.append("Federal tax withheld field is required.")
        else:
            try:
                withheld = float(withheld_str)
                if withheld < 0:
                    errors.append("Federal tax withheld cannot be negative.")
                elif withheld > 500000:  # Reasonable upper limit
                    errors.append("Federal tax withheld amount seems unusually high. Please verify.")
            except ValueError:
                errors.append("Federal tax withheld must be a valid number.")
    
    # Cross-validation
    if not errors:
        try:
            income = float(income_str)
            deductions = float(deductions_str)
            if deductions > income:
                errors.append("Deductions cannot exceed total income.")
            
            # Validate withheld vs income if provided
            if withheld_str:
                withheld = float(withheld_str)
                if withheld > income * 0.5:  # More than 50% of income seems high
                    errors.append("Federal tax withheld seems unusually high compared to income. Please verify.")
        except ValueError:
            pass  # Already caught above
    
    return {
        'valid': len(errors) == 0,
        'error': ' '.join(errors) if errors else None
    }

def analyze_deduction_strategy(income, status, itemized_deductions):
    """
    Provide intelligent analysis of deduction strategy with recommendations
    """
    standard_deduction = STANDARD_DEDUCTIONS_2025[status]
    
    analysis = {
        'standard_deduction': standard_deduction,
        'itemized_deductions': itemized_deductions,
        'recommended_strategy': '',
        'tax_savings_from_itemizing': 0,
        'deduction_gap': 0,
        'recommendations': [],
        'missed_opportunities': [],
        'optimization_tips': []
    }
    
    # Determine best strategy
    if itemized_deductions > standard_deduction:
        analysis['recommended_strategy'] = 'itemize'
        analysis['deduction_gap'] = itemized_deductions - standard_deduction
        
        # Calculate tax savings from itemizing
        marginal_rate = 0.12  # Default to 12% bracket
        for bracket_limit, rate in TAX_BRACKETS_2025[status]:
            if income <= bracket_limit:
                marginal_rate = rate
                break
        
        analysis['tax_savings_from_itemizing'] = round(analysis['deduction_gap'] * marginal_rate)
        
        analysis['recommendations'].append({
            'type': 'strategy',
            'title': '✅ Itemize Your Deductions',
            'description': f'You save ${analysis["tax_savings_from_itemizing"]:,} by itemizing vs. standard deduction.',
            'impact': 'high'
        })
        
    else:
        analysis['recommended_strategy'] = 'standard'
        analysis['deduction_gap'] = standard_deduction - itemized_deductions
        
        # Calculate how much more needed to benefit from itemizing
        shortfall = standard_deduction - itemized_deductions
        analysis['recommendations'].append({
            'type': 'strategy',
            'title': '📊 Take the Standard Deduction',
            'description': f'Standard deduction saves you ${analysis["deduction_gap"]:,} vs. itemizing.',
            'impact': 'high'
        })
        
        # Suggest ways to reach itemization threshold
        if shortfall <= 5000:  # Close to threshold
            analysis['recommendations'].append({
                'type': 'opportunity',
                'title': '💡 Close to Itemizing Threshold',
                'description': f'You need ${shortfall:,} more in deductions to benefit from itemizing.',
                'impact': 'medium'
            })
    
    # Get AI-powered advice first (prioritized)
    llm_advice = get_llm_tax_advice(income, status, itemized_deductions, standard_deduction)
    
    if llm_advice:
        # Use AI-generated analysis when available
        ai_opportunities = llm_advice.get('missed_opportunities', [])
        ai_tips = llm_advice.get('optimization_tips', [])
        
        # Use AI content exclusively
        analysis['missed_opportunities'] = ai_opportunities
        analysis['optimization_tips'] = ai_tips
        
        # Add AI-specific strategy if available
        if llm_advice.get('strategy_recommendation'):
            analysis['recommendations'].append({
                'type': 'ai_strategy',
                'title': '🤖 AI Tax Advisor Recommendation',
                'description': f"AI suggests: {llm_advice['strategy_recommendation']}",
                'impact': 'high'
            })
        
        # Add AI-specific advice
        if llm_advice.get('specific_advice'):
            analysis['ai_advice'] = llm_advice['specific_advice']
    else:
        # Fallback to traditional analysis when AI is not available
        traditional_opportunities = analyze_missed_deductions(income, status, itemized_deductions)
        traditional_tips = get_deduction_optimization_tips(income, status, itemized_deductions)
        
        analysis['missed_opportunities'] = traditional_opportunities
        analysis['optimization_tips'] = traditional_tips
        analysis['ai_advice'] = None
    
    return analysis

def analyze_missed_deductions(income, status, current_deductions):
    """
    Analyze potential missed deduction opportunities
    """
    missed_opportunities = []
    
    # Check for common deductions that might be missing
    estimated_salt = min(income * 0.08, 10000)  # Estimate SALT at 8% of income, capped at $10K
    estimated_charitable = income * 0.025  # Estimate charitable at 2.5% of income
    estimated_medical_threshold = income * 0.075  # Medical deduction threshold
    
    # SALT deduction opportunity
    if income > 50000 and current_deductions < estimated_salt:
        missed_opportunities.append({
            'category': 'SALT',
            'title': 'State and Local Tax Deduction',
            'description': f'You may be missing ${estimated_salt:,.0f} in state/local tax deductions.',
            'potential_savings': round((estimated_salt * 0.22)),  # Assume 22% bracket
            'tips': ['Include state income tax', 'Include property tax (up to $10K total)']
        })
    
    # Charitable deduction opportunity
    if current_deductions < estimated_charitable:
        missed_opportunities.append({
            'category': 'charitable',
            'title': 'Charitable Contribution Deduction',
            'description': f'Consider charitable giving for ${estimated_charitable:,.0f} potential deduction.',
            'potential_savings': round(estimated_charitable * 0.22),
            'tips': ['Cash donations to qualified charities', 'Donated goods (keep receipts)', 'Volunteer mileage']
        })
    
    # Medical deduction opportunity for high medical costs
    if income > 40000:
        missed_opportunities.append({
            'category': 'medical',
            'title': 'Medical Expense Deduction',
            'description': f'Medical expenses over ${estimated_medical_threshold:,.0f} may be deductible.',
            'potential_savings': 'Varies',
            'tips': ['Unreimbursed medical bills', 'Prescription costs', 'Medical travel expenses']
        })
    
    # Mortgage interest for homeowners
    if income > 60000 and current_deductions < 15000:
        missed_opportunities.append({
            'category': 'mortgage',
            'title': 'Mortgage Interest Deduction',
            'description': 'Homeowners can deduct mortgage interest (up to $750K loan).',
            'potential_savings': 'Varies',
            'tips': ['Primary residence mortgage interest', 'Points paid on mortgage', 'Home equity loan interest (if used for home improvement)']
        })
    
    return missed_opportunities

def get_deduction_optimization_tips(income, status, current_deductions):
    """
    Provide personalized tips for optimizing deductions
    """
    tips = []
    standard_deduction = STANDARD_DEDUCTIONS_2025[status]
    
    # General tips based on income level
    if income < 50000:
        tips.append({
            'title': 'Focus on Major Deductions',
            'description': 'At your income level, focus on larger deductions like SALT and charitable giving.',
            'priority': 'high'
        })
    elif income < 100000:
        tips.append({
            'title': 'Consider Bunching Deductions',
            'description': 'Consider "bunching" charitable contributions every other year to exceed standard deduction.',
            'priority': 'medium'
        })
    else:
        tips.append({
            'title': 'Maximize High-Income Deductions',
            'description': 'Take advantage of SALT deduction (up to $10K) and mortgage interest deductions.',
            'priority': 'high'
        })
    
    # Strategy tips based on deduction gap
    gap = abs(current_deductions - standard_deduction)
    if gap < 2000:
        tips.append({
            'title': 'Track Small Deductions',
            'description': 'You\'re close to the threshold - small deductions can make a big difference.',
            'priority': 'medium'
        })
    
    # Timing tips
    tips.append({
        'title': 'Year-End Tax Planning',
        'description': 'Consider timing charitable contributions and business expenses before year-end.',
        'priority': 'medium'
    })
    
    # Record keeping tips
    tips.append({
        'title': 'Keep Detailed Records',
        'description': 'Maintain receipts and documentation for all potential deductions.',
        'priority': 'high'
    })
    
    return tips

def get_llm_tax_advice(income, status, itemized_deductions, standard_deduction):
    """
    Get personalized tax advice from a large language model (OpenAI GPT)
    """
    if not LLM_ENABLED or openai_client is None:
        return None
    
    try:
        # Prepare anonymized data for LLM (no personal info, just tax figures)
        tax_context = {
            'income_range': get_income_range(income),
            'filing_status': status,
            'itemized_deductions': itemized_deductions,
            'standard_deduction': standard_deduction,
            'deduction_gap': abs(itemized_deductions - standard_deduction),
            'year': '2025'
        }
        
        # Create a focused prompt for tax advice
        prompt = f"""As a tax advisor, provide personalized deduction advice for a {tax_context['filing_status']} filer with:

Income Range: {tax_context['income_range']}
Current Itemized Deductions: ${tax_context['itemized_deductions']:,}
Standard Deduction Available: ${tax_context['standard_deduction']:,}
Gap: ${tax_context['deduction_gap']:,}

Please provide:
1. Strategy recommendation (standard vs itemize)
2. 3-4 specific missed deduction opportunities
3. 2-3 actionable optimization tips
4. Any income-specific advice

Focus on practical, actionable advice. Use 2025 tax rules. Be concise but specific.
Format as JSON with keys: strategy, missed_opportunities, optimization_tips, specific_advice."""

        # Call OpenAI API using the client instance
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional tax advisor providing accurate, practical tax advice based on 2025 IRS rules. Always recommend consulting a qualified tax professional for complex situations."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3  # Lower temperature for more consistent advice
        )
        
        # Parse the response
        llm_advice = response.choices[0].message.content
        
        # Calculate marginal rate for this income level
        marginal_rate = 0.22  # Default
        for bracket_limit, rate in TAX_BRACKETS_2025[status]:
            if income <= bracket_limit:
                marginal_rate = rate
                break
        
        # Try to parse as JSON, fallback to text parsing if needed
        try:
            advice_data = json.loads(llm_advice)
            return format_llm_advice(advice_data, income, marginal_rate)
        except json.JSONDecodeError:
            # Fallback: parse text response
            return parse_text_advice(llm_advice, income, marginal_rate)
            
    except Exception as e:
        logging.warning(f"LLM tax advice failed: {e}")
        return None

def get_income_range(income):
    """Convert specific income to general range for privacy"""
    if income < 30000:
        return "$20K-$30K"
    elif income < 50000:
        return "$30K-$50K"
    elif income < 75000:
        return "$50K-$75K"
    elif income < 100000:
        return "$75K-$100K"
    elif income < 150000:
        return "$100K-$150K"
    elif income < 250000:
        return "$150K-$250K"
    elif income < 500000:
        return "$250K-$500K"
    else:
        return "$500K+"

def extract_or_estimate_savings(potential_savings, description, income, marginal_rate):
    """
    Extract numerical savings from AI response or estimate based on deduction type and income
    """
    # First, try to extract a dollar amount from the potential_savings or description
    if potential_savings and isinstance(potential_savings, (int, float)):
        return int(potential_savings)
    
    # Try to extract dollar amounts from text
    text_to_search = f"{potential_savings or ''} {description}"
    dollar_matches = re.findall(r'\$[\d,]+', text_to_search)
    if dollar_matches:
        try:
            amount_str = dollar_matches[0].replace('$', '').replace(',', '')
            amount = int(float(amount_str))
            # If it's a reasonable deduction amount, calculate tax savings
            if 100 <= amount <= 50000:
                return int(amount * marginal_rate)
        except ValueError:
            pass
    
    # Look for percentage mentions and estimate savings
    percent_matches = re.findall(r'(\d+(?:\.\d+)?)%', description)
    if percent_matches:
        try:
            percent = float(percent_matches[0]) / 100
            estimated_deduction = income * percent
            if estimated_deduction <= 50000:  # Reasonable limit
                return int(estimated_deduction * marginal_rate)
        except ValueError:
            pass
    
    # Estimate based on common deduction types mentioned in description
    description_lower = description.lower()
    
    if any(word in description_lower for word in ['charitable', 'donation', 'charity', 'giving']):
        # Estimate charitable deductions at 2-4% of income
        estimated_deduction = min(income * 0.035, 12000)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['salt', 'state', 'property', 'local tax', 'real estate']):
        # SALT deduction capped at $10,000
        estimated_deduction = min(income * 0.08, 10000)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['mortgage', 'interest', 'home', 'house', 'property']):
        # Mortgage interest - varies widely, estimate conservatively
        if income > 100000:
            estimated_deduction = min(income * 0.15, 25000)
        else:
            estimated_deduction = min(income * 0.12, 18000)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['medical', 'health', 'doctor', 'hospital', 'prescription']):
        # Medical expenses over 7.5% of AGI
        estimated_deduction = max(0, income * 0.12 - income * 0.075)  # Assume 12% medical costs
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['business', 'professional', 'office', 'work', 'job']):
        # Business expenses - estimate conservatively
        estimated_deduction = min(income * 0.06, 7500)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['student loan', 'loan interest', 'student debt']):
        # Student loan interest deduction (up to $2,500)
        estimated_deduction = min(2500, income * 0.04)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['educator', 'teacher', 'classroom', 'teaching']):
        # Educator expense deduction (up to $300)
        estimated_deduction = 300
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['retirement', '401k', 'ira', 'pension', 'savings']):
        # Retirement savings credit or deduction
        if income < 50000:
            estimated_deduction = min(income * 0.10, 6000)  # Traditional IRA/401k deduction
        else:
            estimated_deduction = min(income * 0.05, 3000)  # Smaller credit for higher income
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['education', 'tuition', 'college', 'university']):
        # Education-related deductions (American Opportunity Credit, etc.)
        estimated_deduction = min(4000, income * 0.03)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['child', 'dependent', 'family', 'daycare']):
        # Child and dependent care credit
        estimated_deduction = min(income * 0.08, 8000)
        return int(estimated_deduction * marginal_rate)
    
    elif any(word in description_lower for word in ['energy', 'solar', 'electric', 'green', 'efficiency']):
        # Energy efficiency credits
        estimated_deduction = min(income * 0.02, 2000)
        return int(estimated_deduction * marginal_rate)
    
    # Default estimate based on income level
    if income < 50000:
        return int(500 * marginal_rate)  # $500 potential deduction
    elif income < 100000:
        return int(1500 * marginal_rate)  # $1,500 potential deduction
    elif income < 200000:
        return int(3000 * marginal_rate)  # $3,000 potential deduction
    else:
        return int(5000 * marginal_rate)  # $5,000 potential deduction

def format_llm_advice(advice_data, income=0, marginal_rate=0.22):
    """Format structured LLM advice into our system format"""
    formatted = {
        'strategy_recommendation': advice_data.get('strategy', ''),
        'missed_opportunities': [],
        'optimization_tips': [],
        'specific_advice': advice_data.get('specific_advice', '')
    }
    
    # Format missed opportunities
    if 'missed_opportunities' in advice_data:
        for opp in advice_data['missed_opportunities']:
            if isinstance(opp, dict):
                # Try to extract or calculate potential savings
                potential_savings = extract_or_estimate_savings(
                    opp.get('potential_savings'), 
                    opp.get('description', ''), 
                    income, 
                    marginal_rate
                )
                
                formatted['missed_opportunities'].append({
                    'category': 'llm_generated',
                    'title': opp.get('title', '🤖 AI-Generated Opportunity'),
                    'description': opp.get('description', str(opp)),
                    'potential_savings': potential_savings,
                    'tips': opp.get('tips', [str(opp)] if isinstance(opp, str) else [])
                })
            else:
                # For string opportunities, estimate savings based on content
                potential_savings = extract_or_estimate_savings(
                    None, 
                    str(opp), 
                    income, 
                    marginal_rate
                )
                
                formatted['missed_opportunities'].append({
                    'category': 'llm_generated',
                    'title': '🤖 AI Tax Opportunity',
                    'description': str(opp),
                    'potential_savings': potential_savings,
                    'tips': []
                })
    
    # Format optimization tips
    if 'optimization_tips' in advice_data:
        for tip in advice_data['optimization_tips']:
            if isinstance(tip, dict):
                formatted['optimization_tips'].append({
                    'title': tip.get('title', '🤖 AI Tax Tip'),
                    'description': tip.get('description', str(tip)),
                    'priority': tip.get('priority', 'medium')
                })
            else:
                formatted['optimization_tips'].append({
                    'title': '🤖 AI Tax Optimization',
                    'description': str(tip),
                    'priority': 'medium'
                })
    
    return formatted

def parse_text_advice(text_advice, income=0, marginal_rate=0.22):
    """Parse unstructured text advice from LLM"""
    # Simple fallback for unstructured text
    return {
        'strategy_recommendation': 'See AI advice below',
        'missed_opportunities': [{
            'category': 'llm_generated',
            'title': '🤖 AI Tax Advice',
            'description': text_advice[:200] + "..." if len(text_advice) > 200 else text_advice,
            'potential_savings': extract_or_estimate_savings(None, text_advice, income, marginal_rate),
            'tips': []
        }],
        'optimization_tips': [{
            'title': '🤖 AI Tax Optimization',
            'description': 'Review the AI advice for personalized recommendations.',
            'priority': 'medium'
        }],
        'specific_advice': text_advice[:200] + "..." if len(text_advice) > 200 else text_advice
    }

def calculate_tax(income, status, deductions, withheld=0):
    """
    Calculate tax using progressive tax brackets with detailed breakdown
    """
    # Use standard deduction if user deduction is less
    standard_deduction = STANDARD_DEDUCTIONS_2025[status]
    actual_deductions = max(deductions, standard_deduction)
    
    taxable_income = max(0, income - actual_deductions)
    
    # Calculate tax using progressive brackets
    tax_owed = 0
    previous_bracket = 0
    brackets_used = []
    
    for bracket_limit, rate in TAX_BRACKETS_2025[status]:
        if taxable_income > previous_bracket:
            taxable_in_bracket = min(taxable_income, bracket_limit) - previous_bracket
            tax_in_bracket = taxable_in_bracket * rate
            tax_owed += tax_in_bracket
            
            brackets_used.append({
                'range': f"${previous_bracket:,.0f} - ${min(bracket_limit, taxable_income):,.0f}",
                'rate': f"{rate*100:.0f}%",
                'taxable_amount': taxable_in_bracket,
                'tax_amount': tax_in_bracket
            })
            
            previous_bracket = bracket_limit
            
            if taxable_income <= bracket_limit:
                break
    
    # Calculate rates
    effective_rate = (tax_owed / income * 100) if income > 0 else 0
    
    # Find marginal rate
    marginal_rate = 0
    for bracket_limit, rate in TAX_BRACKETS_2025[status]:
        if taxable_income <= bracket_limit:
            marginal_rate = rate * 100
            break
    
    after_tax_income = income - tax_owed
    
    # Calculate refund or additional tax owed
    refund_or_owed = withheld - tax_owed
    
    # Perform smart deduction analysis
    deduction_analysis = analyze_deduction_strategy(income, status, deductions)
    
    return {
        'taxable_income': round(taxable_income),
        'tax_owed': round(tax_owed),
        'after_tax_income': round(after_tax_income),
        'effective_rate': round(effective_rate, 2),
        'marginal_rate': marginal_rate,
        'standard_deduction': standard_deduction,
        'actual_deductions': actual_deductions,
        'brackets_used': brackets_used,
        'deduction_type': 'Standard' if actual_deductions == standard_deduction else 'Itemized',
        'federal_withheld': round(withheld),
        'refund_or_owed': round(refund_or_owed),
        'is_refund': refund_or_owed > 0,
        'net_payment': round(abs(refund_or_owed)),
        'deduction_analysis': deduction_analysis
    }

def generate_tax_form_content(data):
    """
    Generate a simplified 1040 tax form as PDF bytes for serverless environment
    """
    from io import BytesIO
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Get the PDF content
    story = _build_tax_form_story(data)
    doc.build(story)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def _build_tax_form_story(data):
    """
    Build the story content for the tax form PDF
    """
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.black
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.black
    )
    
    normal_style = styles['Normal']
    
    # Build story (content)
    story = []
    
    # Header
    story.append(Paragraph("Form 1040", title_style))
    story.append(Paragraph("U.S. Individual Income Tax Return", styles['Normal']))
    story.append(Paragraph("2025", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Official notice
    story.append(Paragraph("<b>Official 2025 Tax Year:</b> This form uses the official IRS tax brackets and standard deductions from IR-2024-273 (October 22, 2024).", normal_style))
    story.append(Spacer(1, 12))
    
    # Filing Information
    story.append(Paragraph("Filing Information", section_style))
    filing_data = [
        ['Filing Status:', data['status'].title()],
        ['Date Prepared:', datetime.now().strftime('%m/%d/%Y')]
    ]
    filing_table = Table(filing_data, colWidths=[3*inch, 3*inch])
    filing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(filing_table)
    story.append(Spacer(1, 12))
    
    # Income Section
    story.append(Paragraph("Income", section_style))
    income_data = [
        ['1. Total Income:', f"${int(data['income']):,}"],
        ['2. Adjusted Gross Income:', f"${int(data['income']):,}"]
    ]
    income_table = Table(income_data, colWidths=[3*inch, 3*inch])
    income_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(income_table)
    story.append(Spacer(1, 12))
    
    # Deductions Section
    story.append(Paragraph("Deductions", section_style))
    deductions_data = [
        ['3. Standard/Itemized Deductions:', f"${int(data['deductions']):,}"],
        ['4. Taxable Income:', f"${int(data['taxable_income']):,}"]
    ]
    deductions_table = Table(deductions_data, colWidths=[3*inch, 3*inch])
    deductions_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(deductions_table)
    story.append(Spacer(1, 12))
    
    # Tax Calculation Section
    story.append(Paragraph("Tax Calculation", section_style))
    tax_data = [
        ['5. Total Tax:', f"${int(data['tax_owed']):,}"],
        ['6. After-Tax Income:', f"${int(data['after_tax_income']):,}"]
    ]
    tax_table = Table(tax_data, colWidths=[3*inch, 3*inch])
    tax_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tax_table)
    story.append(Spacer(1, 12))
    
    # Refund/Payment Section
    if data.get('is_refund', False):
        story.append(Paragraph("Refund", section_style))
        payment_data = [
            ['7. Federal Tax Withheld:', f"${int(data.get('federal_withheld', 0)):,}"],
            ['8. Refund Amount:', f"${int(data.get('net_payment', 0)):,}"]
        ]
        bg_color = colors.lightgreen
    else:
        story.append(Paragraph("Amount Owed", section_style))
        payment_data = [
            ['7. Federal Tax Withheld:', f"${int(data.get('federal_withheld', 0)):,}"],
            ['8. Additional Tax Owed:', f"${int(data.get('net_payment', 0)):,}"]
        ]
        bg_color = colors.mistyrose
    
    payment_table = Table(payment_data, colWidths=[3*inch, 3*inch])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 12))
    
    # Declaration Section
    story.append(Paragraph("Declaration", section_style))
    story.append(Paragraph("Under penalties of perjury, I declare that I have examined this return and accompanying schedules and statements, and to the best of my knowledge and belief, they are true, correct, and complete.", normal_style))
    story.append(Spacer(1, 12))
    
    signature_data = [
        ['Taxpayer\'s Signature:', '_________________________'],
        ['Date:', '_________________________']
    ]
    signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(signature_table)
    story.append(Spacer(1, 12))
    
    # Footer
    story.append(Paragraph("<b>IMPORTANT:</b> This is a simplified tax form generated for demonstration purposes only.", normal_style))
    story.append(Paragraph("Based on official IRS 2025 tax brackets (IR-2024-273). For actual tax filing, please consult a qualified tax professional or use official IRS forms.", normal_style))
    
    return story

def generate_tax_form(data):
    """
    Generate a simplified 1040 tax form as PDF with calculated data using ReportLab
    """
    # Generate PDF filename
    filename = f"tax_form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join('generated_forms', filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Build story and create PDF
    story = _build_tax_form_story(data)
    doc.build(story)
    
    return filepath