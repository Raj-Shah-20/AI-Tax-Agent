from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from tax_calculator import calculate_tax, validate_input, generate_tax_form_content
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page with tax input form"""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Process tax calculation and display results"""
    try:
        # Get form data with validation
        income_str = request.form.get('income', '').strip()
        deductions_str = request.form.get('deductions', '').strip()
        status = request.form.get('status', '').strip()
        withheld_str = request.form.get('withheld', '').strip()
        
        # Validate input
        validation_result = validate_input(income_str, deductions_str, status, withheld_str)
        if not validation_result['valid']:
            return render_template('index.html', error=validation_result['error'])
        
        # Convert to float after validation
        income = float(income_str)
        deductions = float(deductions_str)
        withheld = float(withheld_str)
        
        # Calculate tax
        tax_result = calculate_tax(income, status, deductions, withheld)
        
        # Prepare results for display
        results = {
            'income': income,
            'deductions': deductions,
            'status': status,
            'withheld': withheld,
            'taxable_income': tax_result['taxable_income'],
            'tax_owed': tax_result['tax_owed'],
            'after_tax_income': tax_result['after_tax_income'],
            'effective_rate': tax_result['effective_rate'],
            'marginal_rate': tax_result['marginal_rate'],
            'refund_or_owed': tax_result['refund_or_owed'],
            'is_refund': tax_result['is_refund'],
            'net_payment': tax_result['net_payment'],
            'deduction_analysis': tax_result['deduction_analysis'],
            'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"Tax calculation completed for income: ${income}, status: {status}, withheld: ${withheld}")
        
        return render_template('result.html', **results)
        
    except ValueError as e:
        logger.error(f"ValueError in tax calculation: {e}")
        return render_template('index.html', error='Invalid input data. Please check your entries.')
    except Exception as e:
        logger.error(f"Unexpected error in tax calculation: {e}")
        return render_template('index.html', error='An unexpected error occurred. Please try again.')

@app.route('/generate_form', methods=['POST'])
def generate_form():
    """Generate and download tax form - modified for serverless environment"""
    try:
        # Get calculation data from form
        data = {
            'income': float(request.form.get('income')),
            'deductions': float(request.form.get('deductions')),
            'status': request.form.get('status'),
            'tax_owed': float(request.form.get('tax_owed')),
            'after_tax_income': float(request.form.get('after_tax_income')),
            'taxable_income': float(request.form.get('taxable_income')),
            'federal_withheld': float(request.form.get('withheld', 0)),
            'is_refund': request.form.get('is_refund') == 'True',
            'net_payment': float(request.form.get('net_payment', 0))
        }
        
        # Generate tax form content (returns PDF bytes)
        pdf_content = generate_tax_form_content(data)
        
        logger.info("Tax form generated successfully")
        
        # Return PDF as response
        response = Response(
            pdf_content,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=tax_form_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            }
        )
        return response
        
    except Exception as e:
        logger.error(f"Error generating tax form: {e}")
        return render_template('index.html', error='Error generating tax form. Please try again.')

@app.route('/api/validate', methods=['POST'])
def validate_api():
    """API endpoint for real-time validation"""
    try:
        data = request.get_json()
        result = validate_input(
            data.get('income', ''),
            data.get('deductions', ''),
            data.get('status', ''),
            data.get('withheld', '')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'valid': False, 'error': 'Validation error occurred'})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

# For Vercel
app = app

if __name__ == '__main__':
    app.run(debug=False) 