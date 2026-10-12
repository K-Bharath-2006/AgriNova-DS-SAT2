"""
AgriNova - Notebook Execution Validator (Headless)
==================================================
Reads and executes all code cells from notebooks/agrinova_eda.ipynb
with headless matplotlib configuration to confirm zero runtime syntax,
logic, or execution errors.
"""

import matplotlib
matplotlib.use("Agg") # Non-blocking headless backend
import matplotlib.pyplot as plt
plt.show = lambda *args, **kwargs: None

import nbformat
import traceback
from pathlib import Path

def validate_notebook(nb_path="AgriNova/notebooks/agrinova_eda.ipynb"):
    print(f"Validating notebook execution: {nb_path}")
    nb = nbformat.read(nb_path, as_version=4)
    
    global_scope = {
        "display": print,
        "plt": plt
    }
    code_cell_idx = 1
    
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            print(f"Executing Code Cell {code_cell_idx}...")
            source = cell.source
            try:
                # Replace display() with print() if running outside IPython
                cleaned_source = source.replace("display(", "print(")
                exec(cleaned_source, global_scope)
                print(f"  -> Cell {code_cell_idx} passed successfully.")
                code_cell_idx += 1
            except Exception as e:
                print(f"\n[ERROR] Execution failed in Code Cell {code_cell_idx} (notebook cell {idx}):")
                traceback.print_exc()
                return False
                
    print("\n" + "=" * 80)
    print("[ALL CELLS PASSED] Notebook runs from start to finish without any error!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    validate_notebook()
