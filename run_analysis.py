#!/usr/bin/env python
"""
Mind Reader AI System - Standalone Execution Script
Executes the notebook code and tests all components
"""

import json
import os
import sys

def extract_notebook_cells(notebook_path):
    """Extract code cells from Jupyter notebook"""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    code_cells = []
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            code = ''.join(cell['source'])
            if code.strip():
                code_cells.append(code)
    
    return code_cells

def execute_notebook(notebook_path):
    """Execute all code cells from the notebook"""
    print("=" * 80)
    print("MIND READER AI SYSTEM - EXECUTION")
    print("=" * 80)
    print(f"\nLoading notebook: {notebook_path}\n")
    
    try:
        code_cells = extract_notebook_cells(notebook_path)
        print(f"Found {len(code_cells)} code cells\n")
        
        # Create a shared namespace for all cells
        namespace = {'__name__': '__main__'}
        
        # Execute each cell sequentially
        for i, code in enumerate(code_cells, 1):
            print(f"\n{'='*80}")
            print(f"EXECUTING CELL {i}/{len(code_cells)}")
            print(f"{'='*80}\n")
            
            try:
                exec(code, namespace)
                print(f"✅ Cell {i} completed successfully")
            except Exception as e:
                print(f"❌ Error in Cell {i}: {str(e)}")
                # Continue with next cell even if one fails
                continue
        
        print(f"\n{'='*80}")
        print("EXECUTION COMPLETE")
        print(f"{'='*80}\n")
        
        # Return the namespace with all defined objects
        return namespace
        
    except FileNotFoundError:
        print(f"ERROR: Notebook file not found: {notebook_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in notebook file")
        return None

def test_mind_score_api(namespace):
    """Test the Mind Score API after execution"""
    print("\n" + "="*80)
    print("TESTING MIND SCORE API")
    print("="*80 + "\n")
    
    if 'mind_score_api' not in namespace:
        print("❌ mind_score_api not found in namespace")
        return False
    
    mind_score_api = namespace['mind_score_api']
    
    test_texts = [
        "I'm feeling wonderful about this new opportunity!",
        "I'm so happy and excited today!",
        "I feel sad and lonely",
        "I'm angry at this situation",
        "Maybe I wasn't there, um, I think...",  # Test deception
    ]
    
    print("Running test analyses:\n")
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}: \"{text}\"")
        try:
            result = mind_score_api.analyze(text, detailed=False)
            emotion = result.get('emotion_analysis', {}).get('emotion', 'N/A')
            score = result.get('mind_score', {}).get('overall_score', 'N/A')
            print(f"  ✅ Emotion: {emotion} | Score: {score}\n")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")
    
    return True

def main():
    notebook_path = "mind_reader_ai_system.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"ERROR: Notebook not found at {notebook_path}")
        sys.exit(1)
    
    # Execute notebook
    namespace = execute_notebook(notebook_path)
    
    if namespace:
        # Test the API
        test_mind_score_api(namespace)
        print("\n✅ All steps completed!")
    else:
        print("\n❌ Execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
