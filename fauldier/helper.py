import numpy as np
import pandas as pd
import getpass
import os
import shutil

from IPython.display import display, HTML
from importlib import resources


def display_dataframe_scroll(df, max_height=400):
    """Display DataFrame with both horizontal and vertical scrolling in Jupyter."""
    html = f"""
    <div style="width:100%; max-height:{max_height}px; overflow:auto; border:1px solid #ddd;">
        {df.to_html()}
    </div>
    """
    display(HTML(html))


def setup_input_output():
    """Setup input/output folders. Copies input templates on first run only."""

    # Detect if running on MyBinder
    is_binder = 'BINDER_SERVICE_HOST' in os.environ or os.getenv('USER') == 'jovyan'

    if is_binder:
        # On MyBinder, use HOME directory which is always writable
        base_dir = os.environ.get('HOME', '/home/jovyan')
    else:
        # Locally, use user directory with platformdirs
        base_dir = os.path.join(os.path.expanduser('~'), 'fauldier')
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)

    output_dir = os.path.join(base_dir, 'output')
    input_dir = os.path.join(base_dir, 'input')

    if not os.path.exists(input_dir):
        input_templates = resources.files('fauldier') / 'data' / 'input'
        with resources.as_file(input_templates) as template_path:
            shutil.copytree(str(template_path), input_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    return input_dir, output_dir


def read_config(file_path):
    """Read config file into dictionary (key=value, #=comment)."""
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


def compare_results(df1, df2, float_tolerance=1e-8):
    """
    Compare DataFrames with numeric tolerance and string normalization.

    Returns:
        pandas.Series: 'Equal'/'Not Equal' per row
    Raises:
        ValueError: If columns don't match
    """

    # Fix column "quantity"
    df1["QUANTITY"] = pd.to_numeric(df1["QUANTITY"], errors="coerce")
    df2["QUANTITY"] = pd.to_numeric(df2["QUANTITY"], errors="coerce")

    # Replace missing values
    for df in [df1, df2]:
        df = df.replace(['nan', 'NaN', 'N/A', '', None], pd.NA).convert_dtypes()
        #df.replace(['nan', 'NaN', 'N/A', '', None], np.nan, inplace=True)
        #df = df.infer_objects(copy=False)

    # Standardize column names
    for df in [df1, df2]:
        df.columns = df.columns.str.strip().str.lower()

    # Reset indices and align columns
    df1 = df1.reset_index(drop=True).reindex(sorted(df1.columns), axis=1)
    df2 = df2.reset_index(drop=True).reindex(sorted(df2.columns), axis=1)

    # Check column mismatches
    if not (df1.columns == df2.columns).all():
        raise ValueError("Columns do not match between DataFrames.")

    # Convert numeric columns to consistent dtypes
    numeric_cols = []
    for col in df1.columns:
        if pd.api.types.is_numeric_dtype(df1[col]) or pd.api.types.is_numeric_dtype(df2[col]):
            numeric_cols.append(col)
            df1[col] = pd.to_numeric(df1[col], errors='coerce')
            df2[col] = pd.to_numeric(df2[col], errors='coerce')

    # Strip whitespace and normalize strings
    for col in df1.columns:
        if col not in numeric_cols:
            df1[col] = df1[col].astype(str).str.strip().str.normalize('NFKC')
            df2[col] = df2[col].astype(str).str.strip().str.normalize('NFKC')

    # Compare numeric columns with rounding
    for col in numeric_cols:
        df1[col] = df1[col].round(decimals=5)
        df2[col] = df2[col].round(decimals=5)

    # Print unprocessed and processed data
    display(HTML("<h5>Before mapping</h5>"))
    display(df1)

    display(HTML("<h5>After mapping</h5>"))
    display(df2)

    # Comparison logic
    comparison_df = pd.DataFrame(index=df1.index, columns=df1.columns)
    for col in df1.columns:
        if col in numeric_cols:
            comparison_df[col] = np.isclose(df1[col], df2[col], atol=float_tolerance, equal_nan=True)
        else:
            comparison_df[col] = (df1[col] == df2[col]) | (pd.isna(df1[col]) & pd.isna(df2[col]))

    # Equal, Non Equal label
    row_comparison = comparison_df.all(axis=1)
    result_df = row_comparison.apply(lambda x: 'Equal' if x else 'Not Equal')

    # Statistics
    num_equal = row_comparison.sum()
    total = len(row_comparison)
    matching_rate = ((total - num_equal) / total) * 100

    #display(HTML("<h5>Comparison</h5>"))
    #display(result_df.to_frame(name="Comparison"))
    print(f"Mapped entries: {total - num_equal}")
    print(f"Unmapped entries: {num_equal}")
    print(f"Simplified mapping rate: {matching_rate:.0f}%")
    return result_df


def is_missing(v):
    return v is None or (isinstance(v, str) and v.strip() == "")



def prompt_config(key: str, prompt: str, secret: bool = False) -> str:
    """
    Synchronous prompt that works reliably in Jupyter and terminals.
    - secret=True uses getpass (input is hidden).
    - secret=False uses input().
    - Asks user if they want to save the key-value pair to a file.
    """
    prompt_text = f"{prompt}: "
    if secret:
        v = getpass.getpass(prompt_text).strip()
    else:
        v = input(prompt_text).strip()

    if not v:
        raise RuntimeError(f"No value provided for '{key}'.")

    save_response = input(f"Do you want to save '{key}' to a file (not secure!)? (yes/no): ").strip().lower()
    if save_response in ['yes', 'y']:
        file_path = os.path.join('..', 'input', 'llm_config.txt')

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []

        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={v}\n"
                updated = True
                break
        if not updated:
            lines.append(f"{key}={v}\n")

        with open(file_path, 'w') as f:
            f.writelines(lines)

        if secret:
            print(f"Saved '{key}' to llm_config.txt.")
        else:
            print(f"Saved '{key} = {v}' to llm_config.txt.")

    else:
        print(f"Skipped saving '{key}' to file.")

    return v
