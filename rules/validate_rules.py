#!/usr/bin/env python3
"""
Comprehensive validation script for AUTOCOM rules files.

Validates:
- YAML syntax
- Markdown structure
- Required files existence
- Cross-references between files
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  PyYAML not installed. YAML validation will be skipped.")
    print("   Install with: pip install pyyaml")


def validate_yaml_file(file_path: Path) -> bool:
    """Validate a single YAML file."""
    if not YAML_AVAILABLE:
        return True
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        print(f"✓ {file_path.name} - Valid YAML")
        return True
    except yaml.YAMLError as e:
        print(f"✗ {file_path.name} - Invalid YAML: {e}")
        return False
    except Exception as e:
        print(f"✗ {file_path.name} - Error reading file: {e}")
        return False


def validate_markdown_file(file_path: Path) -> bool:
    """Validate a markdown file for basic structure."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for at least one header
        if not re.search(r'^#\s+.+', content, re.MULTILINE):
            print(f"✗ {file_path.name} - No headers found")
            return False
        
        # Check for reasonable length (at least 100 characters)
        if len(content) < 100:
            print(f"✗ {file_path.name} - File too short (< 100 chars)")
            return False
        
        print(f"✓ {file_path.name} - Valid Markdown")
        return True
    except Exception as e:
        print(f"✗ {file_path.name} - Error reading file: {e}")
        return False


def check_required_files(rules_dir: Path) -> Tuple[bool, List[str]]:
    """Check if all required files exist."""
    required_files = [
        "00-START-HERE.md",
        "README.md",
        "AGENT_CODING_RULES.md",
        "Forge-Framework.md",
        "MIND-Model-Rules.md",
        "Cross-Platform-Rules.md",
        "General-Dev-Rules.md",
        "Framework.yaml",
        "MIND-Model-Rules.yaml",
        "validate_rules.py",
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = rules_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    return len(missing_files) == 0, missing_files


def check_cross_references(rules_dir: Path) -> bool:
    """Check if cross-references between files are valid."""
    all_valid = True
    
    # Check if 00-START-HERE.md references exist
    start_file = rules_dir / "00-START-HERE.md"
    if start_file.exists():
        with open(start_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract file references
        references = re.findall(r'`([^`]+\.md)`', content)
        
        for ref in references:
            # Handle relative paths
            if ref.startswith("../"):
                ref_path = rules_dir.parent / ref[3:]
            else:
                ref_path = rules_dir / ref
            
            if not ref_path.exists():
                print(f"✗ Cross-reference error: {ref} not found (referenced in 00-START-HERE.md)")
                all_valid = False
    
    return all_valid


def main():
    """Main validation function."""
    print("=" * 60)
    print("AUTOCOM Rules Validation")
    print("=" * 60)
    print()
    
    rules_dir = Path(__file__).parent
    all_valid = True
    
    # Check required files
    print("1. Checking required files...")
    required_ok, missing = check_required_files(rules_dir)
    if required_ok:
        print("✓ All required files present")
    else:
        print(f"✗ Missing files: {', '.join(missing)}")
        all_valid = False
    print()
    
    # Validate YAML files
    print("2. Validating YAML files...")
    yaml_files = list(rules_dir.glob("*.yaml"))
    if yaml_files:
        for yaml_file in yaml_files:
            if not validate_yaml_file(yaml_file):
                all_valid = False
    else:
        print("⚠️  No YAML files found")
    print()
    
    # Validate Markdown files
    print("3. Validating Markdown files...")
    md_files = list(rules_dir.glob("*.md"))
    if md_files:
        for md_file in md_files:
            if not validate_markdown_file(md_file):
                all_valid = False
    else:
        print("⚠️  No Markdown files found")
    print()
    
    # Check cross-references
    print("4. Checking cross-references...")
    if check_cross_references(rules_dir):
        print("✓ All cross-references valid")
    else:
        all_valid = False
    print()
    
    # Final result
    print("=" * 60)
    if all_valid:
        print("✅ All validations passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some validations failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
