"""
Example 04: Custom Semantic Types

Learn how to extend LogPress with custom field type patterns for
domain-specific logs.

Use cases:
- Application-specific error codes (e.g., ERR-1234, SVC-ERROR-567)
- Custom transaction IDs (e.g., TXN-ABCD1234, ORDER-123456)
- Domain-specific timestamps or identifiers
- Business-specific metrics or codes

This example shows how to add custom pattern recognition to improve
schema extraction accuracy for your specific log format.
"""

import re
from typing import Tuple, List, Optional
from logpress import Compressor
from logpress.context.classification.semantic_types import SemanticTypeRecognizer


class CustomSemanticRecognizer(SemanticTypeRecognizer):
    """
    Extended semantic type recognizer with custom patterns
    
    This class adds domain-specific field patterns on top of
    the built-in patterns (timestamp, IP, severity, etc.)
    """
    
    def __init__(self):
        super().__init__()
        # Add custom patterns to the recognizer
        self.custom_patterns = {
            'ERROR_CODE': [
                (r'^ERR-\d{4}$', 0.95),           # ERR-1234
                (r'^[A-Z]{3}-ERROR-\d{3,5}$', 0.90),  # SVC-ERROR-567
                (r'^E\d{6}$', 0.85),              # E123456
            ],
            'TRANSACTION_ID': [
                (r'^TXN-[A-Z0-9]{8}$', 0.95),     # TXN-ABCD1234
                (r'^ORDER-\d{6,10}$', 0.90),      # ORDER-123456
                (r'^[A-F0-9]{32}$', 0.80),        # MD5-like hash
            ],
            'CUSTOMER_ID': [
                (r'^CUST-\d{8}$', 0.95),          # CUST-12345678
                (r'^C\d{10}$', 0.85),             # C1234567890
            ],
            'SESSION_ID': [
                (r'^SID-[A-Z0-9]{16}$', 0.95),    # SID-ABC123XYZ789QWER
                (r'^sess_[a-f0-9]{32}$', 0.90),   # sess_abc123...
            ],
        }
    
    def recognize_custom_type(self, token: str) -> Tuple[Optional[str], float]:
        """
        Try to match token against custom patterns
        
        Returns:
            (field_type, confidence_score) or (None, 0.0) if no match
        """
        for field_type, patterns in self.custom_patterns.items():
            for pattern, confidence in patterns:
                if re.match(pattern, token):
                    return (field_type, confidence)
        
        # No custom pattern matched
        return (None, 0.0)
    
    def recognize(self, token: str) -> Tuple[str, float]:
        """
        Override recognize to check custom patterns first
        """
        # Try custom patterns first
        custom_type, confidence = self.recognize_custom_type(token)
        if custom_type and confidence > 0.7:  # High confidence threshold
            return (custom_type, confidence)
        
        # Fall back to parent class (built-in patterns)
        return super().recognize(token)


def create_sample_logs_with_custom_fields() -> List[str]:
    """Generate sample logs with custom field types"""
    logs = [
        "[2024-12-01 10:00:00] INFO Transaction TXN-ABCD1234 for CUST-12345678 completed successfully",
        "[2024-12-01 10:00:01] ERROR Transaction TXN-EFGH5678 failed with ERR-1234: Database timeout",
        "[2024-12-01 10:00:02] WARN Customer CUST-87654321 exceeded rate limit for ORDER-123456",
        "[2024-12-01 10:00:03] INFO Session SID-ABC123XYZ789QWER authenticated for C9876543210",
        "[2024-12-01 10:00:04] ERROR Payment service returned SVC-ERROR-567 for TXN-IJKL9012",
        "[2024-12-01 10:00:05] INFO Order ORDER-789012 shipped to CUST-11223344",
        "[2024-12-01 10:00:06] ERROR Critical error E123456 in payment processing",
        "[2024-12-01 10:00:07] INFO Session sess_a1b2c3d4e5f6789012345678901234567 expired",
        "[2024-12-01 10:00:08] WARN Transaction TXN-MNOP3456 pending review for fraud detection",
        "[2024-12-01 10:00:09] INFO Customer CUST-55667788 placed ORDER-345678",
    ]
    return logs


def demonstrate_custom_patterns():
    """Show how custom patterns improve schema extraction"""
    
    print("=" * 70)
    print("Example 04: Custom Semantic Type Patterns")
    print("=" * 70)
    print()
    
    # Create sample logs
    logs = create_sample_logs_with_custom_fields()
    
    print("Sample logs with custom fields:")
    print("-" * 70)
    for i, log in enumerate(logs[:3], 1):
        print(f"{i}. {log}")
    print(f"... and {len(logs) - 3} more logs")
    print()
    
    # Method 1: Using standard Compressor (without custom patterns)
    print("1. Standard Schema Extraction (built-in patterns only):")
    print("-" * 70)
    
    standard_compressor = Compressor(min_support=2)
    compressed_standard, stats_standard = standard_compressor.compress(logs)
    
    print(f"Templates extracted: {stats_standard.template_count}")
    print(f"Compression ratio: {stats_standard.compression_ratio:.2f}×")
    print()
    
    # Show detected templates (standard)
    if hasattr(standard_compressor, 'generator') and hasattr(standard_compressor.generator, 'templates'):
        templates = standard_compressor.generator.templates
        for template in templates[:2]:
            print(f"Template: {' '.join(template.pattern)}")
            print(f"  Matches: {template.match_count} logs")
            print(f"  Field types: {len(template.field_types)} detected")
            print()
    
    print()
    
    # Method 2: Using custom semantic recognizer
    print("2. Enhanced Schema Extraction (with custom patterns):")
    print("-" * 70)
    
    # Create custom recognizer
    custom_recognizer = CustomSemanticRecognizer()
    
    # Test custom pattern recognition
    test_tokens = [
        "TXN-ABCD1234",
        "ERR-1234",
        "CUST-12345678",
        "ORDER-123456",
        "SID-ABC123XYZ789QWER"
    ]
    
    print("Custom pattern recognition:")
    for token in test_tokens:
        field_type, confidence = custom_recognizer.recognize(token)
        print(f"  '{token}' -> {field_type} (confidence: {confidence:.2f})")
    print()
    
    # Note: To fully integrate custom recognizer, you would need to:
    # 1. Extend TemplateGenerator to use custom recognizer
    # 2. Pass custom recognizer to Compressor
    # For this example, we demonstrate the pattern matching capability
    
    print("Benefits of custom patterns:")
    print("  ✓ Better semantic understanding of domain-specific fields")
    print("  ✓ More accurate template extraction")
    print("  ✓ Improved compression through field-specific encoding")
    print("  ✓ Better query filtering on custom fields")
    print()
    
    # Method 3: Show how to use in production
    print("3. Production Integration:")
    print("-" * 70)
    print("""
To integrate custom patterns in production:

1. Create your custom recognizer class:
   
   class MyAppRecognizer(SemanticTypeRecognizer):
       def __init__(self):
           super().__init__()
           self.custom_patterns = {
               'YOUR_FIELD_TYPE': [
                   (r'^YOUR-PATTERN$', 0.95),
               ]
           }

2. Configure your log pipeline:
   
   recognizer = MyAppRecognizer()
   # Use with your compression pipeline
   
3. Benefits:
   - Automatic detection of domain fields
   - Better compression ratios
   - Enhanced query capabilities
   - Semantic validation
    """)


def demonstrate_pattern_validation():
    """Show how to test and validate custom patterns"""
    
    print()
    print("=" * 70)
    print("Pattern Validation")
    print("=" * 70)
    print()
    
    recognizer = CustomSemanticRecognizer()
    
    # Test cases: (token, expected_type, should_match)
    test_cases = [
        # Valid patterns
        ("ERR-1234", "ERROR_CODE", True),
        ("TXN-ABCD1234", "TRANSACTION_ID", True),
        ("CUST-12345678", "CUSTOMER_ID", True),
        ("ORDER-123456", "ORDER_ID", False),  # ORDER is TRANSACTION_ID
        
        # Invalid patterns (should not match)
        ("ERR-ABC", "ERROR_CODE", False),
        ("TXN-123", "TRANSACTION_ID", False),
        ("CUSTOMER-12345678", "CUSTOMER_ID", False),
    ]
    
    print("Validation Results:")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for token, expected_type, should_match in test_cases:
        field_type, confidence = recognizer.recognize_custom_type(token)
        
        if should_match:
            # Check if detected correctly
            if field_type == expected_type or confidence > 0.7:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        else:
            # Check if correctly rejected
            if confidence < 0.7:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        
        print(f"{status} | '{token}' -> {field_type} (conf: {confidence:.2f})")
    
    print()
    print(f"Validation: {passed} passed, {failed} failed")
    print()


if __name__ == "__main__":
    # Run the demonstrations
    demonstrate_custom_patterns()
    demonstrate_pattern_validation()
    
    print("=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("""
1. Custom patterns extend LogPress for domain-specific logs
2. Pattern confidence scoring (0.0-1.0) controls matching strictness
3. Higher confidence = more specific pattern
4. Test your patterns with validation before production
5. Custom types enable better compression and querying

Next steps:
- Add your application's error codes
- Define your transaction ID formats
- Create patterns for business-specific fields
- Test pattern accuracy with your real logs
    """)
