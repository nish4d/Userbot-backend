#!/usr/bin/env python3
"""
Test script for multiple keyword functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import create_reply_rule, get_reply_rules

def test_multiple_triggers():
    """Test creating and retrieving rules with multiple triggers"""
    print("Testing multiple trigger functionality...")
    
    # Test 1: Create rule with multiple triggers
    print("\n1. Creating rule with multiple triggers:")
    triggers = ["hello", "hi", "hey"]
    response = "Hello there! How can I help you today?"
    rule_id = create_reply_rule(triggers, response)
    print(f"Created rule with ID: {rule_id}")
    
    # Test 2: Create rule with single trigger (backward compatibility)
    print("\n2. Creating rule with single trigger (backward compatibility):")
    single_trigger = "bye"
    response2 = "Goodbye! Have a great day!"
    rule_id2 = create_reply_rule(single_trigger, response2)
    print(f"Created rule with ID: {rule_id2}")
    
    # Test 3: Retrieve and display rules
    print("\n3. Retrieving all rules:")
    rules = get_reply_rules()
    for rule in rules:
        print(f"Rule ID: {rule.get('_id')}")
        print(f"Triggers: {rule.get('triggers', 'N/A')}")
        print(f"Trigger (old): {rule.get('trigger', 'N/A')}")
        print(f"Response: {rule.get('response')}")
        print("---")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_multiple_triggers()