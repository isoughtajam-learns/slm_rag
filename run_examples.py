#!/usr/bin/env python
"""
Entry point for running examples.
Run this file from the root directory.
"""

import os
import sys

# Disable ChromaDB telemetry before any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run examples
from examples.examples import *

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        
        examples = {
            "1": example_documentation_query,
            "2": example_incident_analysis,
            "3": example_summarization,
            "4": example_action_request,
            "5": example_batch_queries,
            "6": example_system_info,
            "7": example_custom_documents,
        }
        
        if example_name in examples:
            examples[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print("Available examples: 1-7, or run without args for all")
    else:
        run_all_examples()

