#!/usr/bin/env python3
"""
Test Suite for AI Tax Return Agent Prototype
Tests tax calculation logic, validation, and form generation
"""

import unittest
from tax_calculator import calculate_tax, validate_input, generate_tax_form
import os

class TestTaxCalculator(unittest.TestCase):
    """Test cases for tax calculation functionality"""
    
    def test_single_filer_basic(self):
        """Test basic single filer calculation"""
        result = calculate_tax(50000, 'single', 10000)
        
        # Taxable income should be 50000 - 15000 (2025 standard deduction is higher)
        expected_taxable = 50000 - 15000
        self.assertAlmostEqual(result['taxable_income'], expected_taxable, places=2)
        
        # Tax calculation for $35,000 taxable income (2025 brackets):
        # First $11,925 at 10% = $1,192.50
        # Remaining $23,075 at 12% = $2,769.00
        # Total = $3,961.50, rounded to $3,962
        expected_tax = round(1192.5 + (expected_taxable - 11925) * 0.12)
        self.assertEqual(result['tax_owed'], expected_tax)
    
    def test_married_filer_basic(self):
        """Test basic married filing jointly calculation"""
        result = calculate_tax(100000, 'married', 20000)
        
        # Uses standard deduction since it's higher than itemized (2025: $30,000)
        expected_taxable = 100000 - 30000
        self.assertAlmostEqual(result['taxable_income'], expected_taxable, places=2)
        
        # Tax calculation for $70,000 taxable income (2025 brackets):
        # First $23,850 at 10% = $2,385.00
        # Remaining $46,150 at 12% = $5,538.00
        # Total = $7,923.00
        expected_tax = round(2385 + (expected_taxable - 23850) * 0.12)
        self.assertEqual(result['tax_owed'], expected_tax)
    
    def test_high_income_single(self):
        """Test high income single filer with multiple brackets"""
        result = calculate_tax(500000, 'single', 50000)
        
        expected_taxable = 500000 - 50000  # Itemized deduction is higher
        self.assertAlmostEqual(result['taxable_income'], expected_taxable, places=2)
        
        # This should use multiple tax brackets
        self.assertGreater(result['tax_owed'], 100000)  # Should be substantial
        self.assertLess(result['tax_owed'], 200000)     # But not unreasonable
        
        # Marginal rate should be 35% for this income level (2025 brackets)
        self.assertEqual(result['marginal_rate'], 35)
    
    def test_zero_income(self):
        """Test zero income scenario"""
        result = calculate_tax(0, 'single', 0)
        
        self.assertEqual(result['taxable_income'], 0)
        self.assertEqual(result['tax_owed'], 0)
        self.assertEqual(result['after_tax_income'], 0)
        self.assertEqual(result['effective_rate'], 0)
    
    def test_standard_vs_itemized_deduction(self):
        """Test that system chooses higher deduction"""
        # Low itemized deduction - should use standard (2025: $15,000)
        result1 = calculate_tax(50000, 'single', 5000)
        self.assertEqual(result1['actual_deductions'], 15000)
        self.assertEqual(result1['deduction_type'], 'Standard')
        
        # High itemized deduction - should use itemized
        result2 = calculate_tax(50000, 'single', 20000)
        self.assertEqual(result2['actual_deductions'], 20000)
        self.assertEqual(result2['deduction_type'], 'Itemized')

class TestInputValidation(unittest.TestCase):
    """Test cases for input validation"""
    
    def test_valid_input(self):
        """Test valid input passes validation"""
        result = validate_input('50000', '10000', 'single')
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_negative_income(self):
        """Test negative income validation"""
        result = validate_input('-1000', '5000', 'single')
        self.assertFalse(result['valid'])
        self.assertIn('negative', result['error'].lower())
    
    def test_negative_deductions(self):
        """Test negative deductions validation"""
        result = validate_input('50000', '-500', 'single')
        self.assertFalse(result['valid'])
        self.assertIn('negative', result['error'].lower())
    
    def test_deductions_exceed_income(self):
        """Test deductions exceeding income"""
        result = validate_input('30000', '50000', 'single')
        self.assertFalse(result['valid'])
        self.assertIn('exceed', result['error'].lower())
    
    def test_invalid_filing_status(self):
        """Test invalid filing status"""
        result = validate_input('50000', '10000', 'invalid_status')
        self.assertFalse(result['valid'])
        
    def test_non_numeric_input(self):
        """Test non-numeric input validation"""
        result = validate_input('abc', '10000', 'single')
        self.assertFalse(result['valid'])
        
        result = validate_input('50000', 'xyz', 'single')
        self.assertFalse(result['valid'])
    
    def test_empty_input(self):
        """Test empty input validation"""
        result = validate_input('', '10000', 'single')
        self.assertFalse(result['valid'])
        
        result = validate_input('50000', '', 'single')
        self.assertFalse(result['valid'])
        
        result = validate_input('50000', '10000', '')
        self.assertFalse(result['valid'])
    
    def test_extremely_high_values(self):
        """Test extremely high values validation"""
        result = validate_input('99999999', '10000', 'single')
        self.assertFalse(result['valid'])
        self.assertIn('high', result['error'].lower())

class TestFormGeneration(unittest.TestCase):
    """Test cases for tax form generation"""
    
    def test_form_generation(self):
        """Test that tax form PDF is generated correctly"""
        test_data = {
            'income': 50000,
            'deductions': 13850,
            'status': 'single',
            'tax_owed': 4133,
            'after_tax_income': 45867,
            'taxable_income': 36150,
            'federal_withheld': 5000,
            'is_refund': True,
            'net_payment': 867
        }
        
        # Generate form
        form_path = generate_tax_form(test_data)
        
        # Check that file was created
        self.assertTrue(os.path.exists(form_path))
        
        # Check that it's a PDF file
        self.assertTrue(form_path.endswith('.pdf'))
        
        # Check file size is reasonable (PDF should be > 1000 bytes)
        file_size = os.path.getsize(form_path)
        self.assertGreater(file_size, 1000)
        
        # Basic PDF validation - check file header
        with open(form_path, 'rb') as f:
            header = f.read(4)
            
        # PDF files start with %PDF
        self.assertEqual(header[:4], b'%PDF')
        
        # Clean up
        os.remove(form_path)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_tax_bracket_boundaries(self):
        """Test calculations at tax bracket boundaries"""
        # Test at 10% to 12% boundary for single filer (2025: $11,925)
        result = calculate_tax(11925 + 15000, 'single', 0)  # Exactly at boundary
        
        # Should be exactly $1,193 (11,925 * 0.10 = 1192.5, rounded to 1193)
        self.assertEqual(result['tax_owed'], round(1192.5))
        
        # Test just over the boundary
        result = calculate_tax(11926 + 15000, 'single', 0)
        expected_tax = round(1192.5 + 0.12)  # Previous bracket + $1 at 12%
        self.assertEqual(result['tax_owed'], expected_tax)
    
    def test_maximum_reasonable_income(self):
        """Test maximum reasonable income limit"""
        result = calculate_tax(9999999, 'single', 0)
        
        # Should handle very high income without errors
        self.assertGreater(result['tax_owed'], 3000000)  # Substantial tax
        self.assertEqual(result['marginal_rate'], 37)    # Top bracket
    
    def test_effective_rate_calculation(self):
        """Test effective tax rate calculation"""
        result = calculate_tax(100000, 'single', 0)
        
        # Effective rate should be less than marginal rate
        self.assertLess(result['effective_rate'], result['marginal_rate'])
        
        # Effective rate should be reasonable (between 10-25% for this income)
        self.assertGreater(result['effective_rate'], 10)
        self.assertLess(result['effective_rate'], 25)

def run_comprehensive_tests():
    """Run all test suites and display results"""
    print("🧪 Running AI Tax Return Agent Test Suite\n")
    
    # Create test suite
    test_classes = [
        TestTaxCalculator,
        TestInputValidation,
        TestFormGeneration,
        TestEdgeCases
    ]
    
    total_tests = 0
    total_failures = 0
    
    for test_class in test_classes:
        print(f"📋 Running {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        tests_run = result.testsRun
        failures = len(result.failures) + len(result.errors)
        
        total_tests += tests_run
        total_failures += failures
        
        if failures == 0:
            print(f"  ✅ All {tests_run} tests passed")
        else:
            print(f"  ❌ {failures} out of {tests_run} tests failed")
            for failure in result.failures + result.errors:
                print(f"     - {failure[0]}: {failure[1].split('AssertionError:')[-1].strip()}")
        
        print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_tests - total_failures}")
    print(f"   Failed: {total_failures}")
    
    if total_failures == 0:
        print("   🎉 All tests passed! System is working correctly.")
    else:
        print(f"   ⚠️ {total_failures} tests failed. Please review.")
    
    return total_failures == 0

if __name__ == '__main__':
    # Run comprehensive test suite
    success = run_comprehensive_tests()
    
    if success:
        print("\n🚀 System ready for demonstration!")
    else:
        print("\n🔧 Please fix failing tests before deployment.")
        
    exit(0 if success else 1) 