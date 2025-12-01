"""
Example 05: Schema Extraction Only

Learn how to extract log templates and schemas WITHOUT compression.

Use cases:
- Log format discovery and documentation
- Schema evolution tracking
- Format validation
- Template-based log parsing
- Understanding log structure before compression

This is useful when you want to:
1. Analyze log structure without storing compressed data
2. Generate documentation of log formats
3. Track how log schemas change over time
4. Validate logs against expected templates
"""

from typing import List, Dict
from logpress.context.extraction.template_generator import TemplateGenerator
from datetime import datetime


def create_diverse_sample_logs() -> List[str]:
    """Generate logs from different sources with varying formats"""
    logs = [
        # Apache-style web server logs
        "[2024-12-01 10:00:00] INFO 192.168.1.100 GET /api/users HTTP/1.1 200 1024",
        "[2024-12-01 10:00:01] INFO 192.168.1.101 GET /api/products HTTP/1.1 200 2048",
        "[2024-12-01 10:00:02] ERROR 192.168.1.102 POST /api/orders HTTP/1.1 500 0",
        "[2024-12-01 10:00:03] INFO 192.168.1.103 DELETE /api/users/123 HTTP/1.1 204 0",
        
        # Application errors
        "[2024-12-01 10:01:00] ERROR Database connection failed: timeout after 30s",
        "[2024-12-01 10:01:05] ERROR Database connection failed: timeout after 30s",
        "[2024-12-01 10:01:10] ERROR Database connection failed: timeout after 30s",
        
        # Authentication logs
        "[2024-12-01 10:02:00] WARN User admin failed login attempt from 10.0.0.1",
        "[2024-12-01 10:02:05] WARN User john failed login attempt from 10.0.0.2",
        "[2024-12-01 10:02:10] INFO User alice logged in successfully from 10.0.0.3",
        
        # System events
        "[2024-12-01 10:03:00] INFO Service web-server started on port 8080",
        "[2024-12-01 10:03:01] INFO Service database started on port 5432",
        "[2024-12-01 10:03:02] INFO Service cache-server started on port 6379",
        
        # Performance metrics
        "[2024-12-01 10:04:00] METRIC Request latency: 45ms endpoint: /api/users",
        "[2024-12-01 10:04:01] METRIC Request latency: 120ms endpoint: /api/products",
        "[2024-12-01 10:04:02] METRIC Request latency: 85ms endpoint: /api/orders",
    ]
    return logs


def extract_schemas_basic():
    """Basic schema extraction demonstration"""
    
    print("=" * 70)
    print("Example 05: Schema Extraction Only (No Compression)")
    print("=" * 70)
    print()
    
    # Create sample logs
    logs = create_diverse_sample_logs()
    
    print(f"Analyzing {len(logs)} log entries...")
    print()
    
    # Initialize template generator
    generator = TemplateGenerator(min_support=2)  # Need at least 2 logs to form a template
    
    # Extract templates
    templates = generator.extract_schemas(logs)
    
    print(f"Discovered {len(templates)} unique log templates:")
    print("=" * 70)
    print()
    
    # Display each template
    for i, template in enumerate(templates, 1):
        print(f"Template {i}: {template.template_id}")
        print("-" * 70)
        print(f"Pattern:  {' '.join(template.pattern)}")
        print(f"Matches:  {template.match_count} logs ({template.match_count/len(logs)*100:.1f}%)")
        print(f"Confidence: {template.confidence:.2f}")
        
        # Show field types
        if template.field_types:
            print(f"Fields:   {len(template.field_types)} detected")
            for pos, field_type in template.field_types.items():
                print(f"  - Position {pos}: {field_type.value}")
        
        # Show sample logs
        print("Samples:")
        for sample in template.example_logs[:2]:
            print(f"  • {sample}")
        
        print()


def analyze_schema_coverage():
    """Analyze how well templates cover the log corpus"""
    
    print("=" * 70)
    print("Schema Coverage Analysis")
    print("=" * 70)
    print()
    
    logs = create_diverse_sample_logs()
    generator = TemplateGenerator(min_support=2)
    templates = generator.extract_schemas(logs)
    
    # Calculate coverage statistics
    total_logs = len(logs)
    covered_logs = sum(t.match_count for t in templates)
    uncovered_logs = total_logs - covered_logs
    
    print(f"Total logs analyzed: {total_logs}")
    print(f"Logs matched by templates: {covered_logs} ({covered_logs/total_logs*100:.1f}%)")
    print(f"Unique logs (no template): {uncovered_logs} ({uncovered_logs/total_logs*100:.1f}%)")
    print()
    
    # Template size distribution
    print("Template Distribution:")
    print("-" * 70)
    
    templates_sorted = sorted(templates, key=lambda t: t.match_count, reverse=True)
    
    for i, template in enumerate(templates_sorted[:5], 1):
        percentage = (template.match_count / total_logs) * 100
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = "█" * bar_length
        
        print(f"{i}. {bar} {percentage:.1f}% ({template.match_count} logs)")
        print(f"   Pattern: {' '.join(template.pattern[:8])}{'...' if len(template.pattern) > 8 else ''}")
        print()


def track_schema_evolution():
    """Demonstrate schema evolution tracking over time"""
    
    print("=" * 70)
    print("Schema Evolution Tracking")
    print("=" * 70)
    print()
    
    # Simulate logs from different time periods
    logs_v1 = [
        "[2024-11-01 10:00:00] INFO User logged in",
        "[2024-11-01 10:00:01] INFO User logged out",
        "[2024-11-01 10:00:02] ERROR Database error",
    ] * 3  # Repeat to meet min_support
    
    logs_v2 = [
        "[2024-11-15 10:00:00] INFO User alice logged in from 10.0.0.1",
        "[2024-11-15 10:00:01] INFO User bob logged out from 10.0.0.2",
        "[2024-11-15 10:00:02] ERROR Database error: connection timeout",
    ] * 3  # Repeat to meet min_support
    
    logs_v3 = [
        "[2024-12-01 10:00:00] INFO [AUTH] User alice logged in from 10.0.0.1 with role admin",
        "[2024-12-01 10:00:01] INFO [AUTH] User bob logged out from 10.0.0.2 with role user",
        "[2024-12-01 10:00:02] ERROR [DB] Database error: connection timeout on pool-1",
    ] * 3  # Repeat to meet min_support
    
    print("Version 1 Schema (Nov 1, 2024):")
    print("-" * 70)
    generator_v1 = TemplateGenerator(min_support=2)
    templates_v1 = generator_v1.extract_schemas(logs_v1)
    print(f"Templates: {len(templates_v1)}")
    for t in templates_v1:
        print(f"  • {' '.join(t.pattern)}")
    print()
    
    print("Version 2 Schema (Nov 15, 2024) - Added user details:")
    print("-" * 70)
    generator_v2 = TemplateGenerator(min_support=2)
    templates_v2 = generator_v2.extract_schemas(logs_v2)
    print(f"Templates: {len(templates_v2)}")
    for t in templates_v2:
        print(f"  • {' '.join(t.pattern)}")
    print()
    
    print("Version 3 Schema (Dec 1, 2024) - Added categories and roles:")
    print("-" * 70)
    generator_v3 = TemplateGenerator(min_support=2)
    templates_v3 = generator_v3.extract_schemas(logs_v3)
    print(f"Templates: {len(templates_v3)}")
    for t in templates_v3:
        print(f"  • {' '.join(t.pattern)}")
    print()
    
    print("Schema Evolution Summary:")
    print("-" * 70)
    print("• Version 1: Basic logging (timestamp, severity, message)")
    print("• Version 2: Added user identification and IP addresses")
    print("• Version 3: Added log categories, user roles, error details")
    print()
    print("This tracking helps:")
    print("  ✓ Detect breaking changes in log format")
    print("  ✓ Document format evolution for compliance")
    print("  ✓ Plan backwards-compatible compression strategies")
    print("  ✓ Identify when to update log parsers")
    print()


def validate_logs_against_schema():
    """Show how to use templates for log validation"""
    
    print("=" * 70)
    print("Log Validation Against Expected Schema")
    print("=" * 70)
    print()
    
    # Known good logs
    training_logs = [
        "[2024-12-01 10:00:00] INFO Service started on port 8080",
        "[2024-12-01 10:00:01] INFO Service started on port 5432",
        "[2024-12-01 10:00:02] INFO Service started on port 6379",
    ]
    
    # Extract expected schema
    generator = TemplateGenerator(min_support=2)
    templates = generator.extract_schemas(training_logs)
    
    print("Expected Schema (from training logs):")
    print("-" * 70)
    expected_pattern = templates[0].pattern if templates else []
    print(f"Pattern: {' '.join(expected_pattern)}")
    print()
    
    # New logs to validate
    test_logs = [
        "[2024-12-01 11:00:00] INFO Service started on port 9090",  # Valid
        "[2024-12-01 11:00:01] ERROR Service crashed unexpectedly",  # Invalid format
        "[2024-12-01 11:00:02] INFO Service started on port 3000",   # Valid
        "Service started without timestamp",                          # Invalid (missing timestamp)
    ]
    
    print("Validating new logs:")
    print("-" * 70)
    
    for log in test_logs:
        # Simple validation: check if log matches expected pattern structure
        # In production, you'd use the template generator's matching logic
        is_valid = log.startswith("[") and "INFO Service started on port" in log
        
        status = "✓ VALID  " if is_valid else "✗ INVALID"
        print(f"{status} | {log[:60]}")
    
    print()
    print("Validation use cases:")
    print("  • Pre-compression format verification")
    print("  • Log quality monitoring")
    print("  • Detecting malformed log entries")
    print("  • Ensuring compliance with logging standards")
    print()


def export_schema_documentation():
    """Generate documentation from extracted schemas"""
    
    print("=" * 70)
    print("Schema Documentation Export")
    print("=" * 70)
    print()
    
    logs = create_diverse_sample_logs()
    generator = TemplateGenerator(min_support=2)
    templates = generator.extract_schemas(logs)
    
    print("Generated Log Format Documentation:")
    print("=" * 70)
    print()
    
    for i, template in enumerate(templates, 1):
        print(f"## Log Format {i}: {template.template_id}")
        print()
        print(f"**Pattern:** `{' '.join(template.pattern)}`")
        print()
        print(f"**Frequency:** {template.match_count} occurrences ({template.match_count/len(logs)*100:.1f}%)")
        print()
        
        if template.field_types:
            print("**Detected Fields:**")
            print()
            print("| Position | Semantic Type |")
            print("|----------|---------------|")
            for pos, field_type in template.field_types.items():
                print(f"| {pos} | {field_type.value} |")
            print()
        
        print("**Example:**")
        print(f"```\n{template.example_logs[0] if template.example_logs else 'N/A'}\n```")
        print()
        print("-" * 70)
        print()


if __name__ == "__main__":
    # Run all demonstrations
    extract_schemas_basic()
    print("\n")
    
    analyze_schema_coverage()
    print("\n")
    
    track_schema_evolution()
    print("\n")
    
    validate_logs_against_schema()
    print("\n")
    
    export_schema_documentation()
    
    print("=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("""
1. Schema extraction works independently from compression
2. Templates reveal implicit log structure automatically
3. Coverage analysis shows how well templates fit your logs
4. Evolution tracking documents format changes over time
5. Validation ensures logs match expected formats
6. Export schemas as documentation for teams

When to use schema extraction only:
✓ Discovering unknown log formats
✓ Documenting legacy systems
✓ Validating log quality
✓ Planning compression strategies
✓ Tracking format evolution

Next steps:
- Extract schemas from your production logs
- Track schema changes across releases
- Use templates for log validation
- Generate documentation for your team
    """)
