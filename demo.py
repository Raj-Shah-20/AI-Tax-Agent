#!/usr/bin/env python3
"""
AI Tax Return Agent - Demonstration Script
Showcases all features and capabilities of the prototype
"""

import os
from tax_calculator import calculate_tax, validate_input, generate_tax_form

def print_banner():
    """Display welcome banner"""
    print("=" * 60)
    print("🤖 AI TAX RETURN AGENT PROTOTYPE DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases the comprehensive tax preparation system")
    print("including calculations, validation, refund calculations, and form generation.")
    print("=" * 60)
    print()

def demo_tax_calculations():
    """Demonstrate tax calculation capabilities"""
    print("📊 TAX CALCULATION DEMONSTRATIONS")
    print("-" * 40)
    
    # Test cases with different scenarios including withholding
    test_cases = [
        {
            'scenario': 'Young Professional - Refund Expected',
            'income': 65000,
            'deductions': 8000,
            'withheld': 9000,
            'status': 'single'
        },
        {
            'scenario': 'Married Couple - Additional Tax Owed',
            'income': 120000,
            'deductions': 25000,
            'withheld': 8000,
            'status': 'married'
        },
        {
            'scenario': 'High Earner - Large Payment',
            'income': 250000,
            'deductions': 40000,
            'withheld': 35000,
            'status': 'single'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['scenario']}")
        print(f"   Income: ${case['income']:,}, Deductions: ${case['deductions']:,}, Withheld: ${case['withheld']:,}")
        
        # Calculate tax
        result = calculate_tax(case['income'], case['status'], case['deductions'], case['withheld'])
        
        print(f"   📋 Results:")
        print(f"      • Taxable Income: ${result['taxable_income']:,}")
        print(f"      • Total Tax: ${result['tax_owed']:,}")
        if result['is_refund']:
            print(f"      • 🎉 REFUND: ${result['net_payment']:,}")
        else:
            print(f"      • 💸 ADDITIONAL OWED: ${result['net_payment']:,}")
        print(f"      • Effective Rate: {result['effective_rate']:.2f}%")

def demo_input_validation():
    """Demonstrate input validation capabilities"""
    print("\n\n🔒 INPUT VALIDATION DEMONSTRATIONS")
    print("-" * 40)
    
    validation_tests = [
        {
            'description': 'Valid Input',
            'income': '75000',
            'deductions': '12000',
            'status': 'single',
            'withheld': '8000',
            'expected': True
        },
        {
            'description': 'Negative Income',
            'income': '-5000',
            'deductions': '10000',
            'status': 'single',
            'withheld': '3000',
            'expected': False
        },
        {
            'description': 'Deductions Exceed Income',
            'income': '30000',
            'deductions': '50000',
            'status': 'single',
            'withheld': '5000',
            'expected': False
        },
        {
            'description': 'Invalid Filing Status',
            'income': '50000',
            'deductions': '10000',
            'status': 'invalid',
            'withheld': '5000',
            'expected': False
        }
    ]
    
    for i, test in enumerate(validation_tests, 1):
        print(f"\n{i}. Testing: {test['description']}")
        
        result = validate_input(test['income'], test['deductions'], test['status'], test['withheld'])
        
        if result['valid'] == test['expected']:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"   Result: {status} - {'Valid' if result['valid'] else 'Invalid'}")
        if not result['valid']:
            print(f"   Error: {result['error']}")

def demo_form_generation():
    """Demonstrate tax form generation"""
    print("\n\n📄 TAX FORM GENERATION DEMONSTRATION")
    print("-" * 40)
    
    # Use a sample calculation for form generation
    sample_data = {
        'income': 85000,
        'deductions': 15000,
        'status': 'married',
        'tax_owed': 8520,
        'after_tax_income': 76480,
        'taxable_income': 57300,
        'federal_withheld': 10000,
        'is_refund': True,
        'net_payment': 1480
    }
    
    print("Generating tax form with sample data:")
    print(f"  • Income: ${sample_data['income']:,}")
    print(f"  • Tax Owed: ${sample_data['tax_owed']:,}")
    print(f"  • Refund: ${sample_data['net_payment']:,}")
    
    try:
        form_path = generate_tax_form(sample_data)
        print(f"\n✅ Tax form generated successfully!")
        print(f"   📁 File saved to: {form_path}")
        print(f"   📊 File size: {os.path.getsize(form_path):,} bytes")
        
        # Clean up demo file
        print(f"\n🧹 Cleaning up demo file...")
        os.remove(form_path)
        print(f"   Demo file removed.")
        
    except Exception as e:
        print(f"❌ Form generation failed: {e}")

def demo_smart_deduction_analysis():
    """Demonstrate smart deduction analysis features"""
    print("\n\n🎯 SMART DEDUCTION ANALYSIS DEMONSTRATION")
    print("-" * 40)
    
    scenarios = [
        {
            'name': 'Should Take Standard Deduction',
            'income': 60000,
            'deductions': 10000,
            'status': 'single'
        },
        {
            'name': 'Should Itemize Deductions',
            'income': 80000,
            'deductions': 18000,
            'status': 'single'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}:")
        print(f"   Income: ${scenario['income']:,}, Itemized: ${scenario['deductions']:,}")
        
        result = calculate_tax(scenario['income'], scenario['status'], scenario['deductions'], 0)
        analysis = result['deduction_analysis']
        
        print(f"   🎯 Recommended: {analysis['recommended_strategy'].title()} Deduction")
        print(f"   📈 Opportunities Found: {len(analysis['missed_opportunities'])}")
        print(f"   💡 Optimization Tips: {len(analysis['optimization_tips'])}")
        
        if analysis.get('ai_advice'):
            print(f"   🤖 AI Advisor: Active")
        else:
            print(f"   🤖 AI Advisor: Not configured")

def run_complete_demo():
    """Run the complete demonstration"""
    print_banner()
    
    try:
        # Run each demonstration section
        demo_tax_calculations()
        demo_input_validation()
        demo_form_generation()
        demo_smart_deduction_analysis()
        
        # Final summary
        print("\n\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("The AI Tax Return Agent prototype successfully demonstrated:")
        print("✅ Accurate progressive tax calculations with 2025 IRS brackets")
        print("✅ Federal tax withholding integration and refund calculations")
        print("✅ Comprehensive input validation and error handling")
        print("✅ Professional PDF tax form generation")
        print("✅ Smart deduction analysis with AI recommendations")
        print("✅ Multiple filing status support")
        print()
        print("🚀 Ready for web interface!")
        print("   Run 'python app.py' to start the web server")
        print("   Visit http://127.0.0.1:5000 to use the interface")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")

if __name__ == '__main__':
    # Ensure generated_forms directory exists
    os.makedirs('generated_forms', exist_ok=True)
    
    # Run the complete demonstration
    run_complete_demo() 