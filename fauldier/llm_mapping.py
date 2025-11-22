import os
import pandas as pd

from IPython.display import display, HTML
from openai import OpenAI, BadRequestError

from . import helper as h

def transform_data_for_LLM(LCI_sheet_modify, product_list):
    """
    Prepare data for LLM classification by separating products and internal activities.

    Args:
        LCI_sheet_modify (pd.DataFrame): Input DataFrame with process data
        product_list (list): List of existing product names to identify internal activities

    Returns:
        tuple: (user_inputs, product_row, internal_activities, modified_df)
            - user_inputs: Formatted list of process inputs for LLM
            - product_row: DataFrame containing product information
            - internal_activities: DataFrame of internal production activities
            - modified_df: Input DataFrame without product/internal activities
    """

    # Get user inputs, filter products, convert to | separated list; save product rows
    product_row = LCI_sheet_modify[
        LCI_sheet_modify['Unnamed: 1'].str.contains('PRODUCTS', case=False, na=False)
    ].head(1)  # only take first (in case of by-products)

    # Drop product row
    LCI_sheet_modify_wo_product = LCI_sheet_modify.drop(index=product_row.index).copy()

    # Save all internal activities
    internal_activities = LCI_sheet_modify[
        LCI_sheet_modify['name'].isin(product_list)
    ]

    # Drop all internal activities
    LCI_sheet_modify_wo_production = LCI_sheet_modify.drop(
        index=internal_activities.index).copy()

    # Generate user input from sheet
    user_inputs = LCI_sheet_modify_wo_production.apply(
        lambda row: f"{row['name']} | {row['ORIGIN']}  | {row['UNIT']} | {row['QUANTITY']}",
        axis=1
    ).tolist()

    return user_inputs, product_row, internal_activities, LCI_sheet_modify_wo_production


def classify_input_batch(user_inputs: list[str], activities: list[str], biosphere_flows: list[str]) -> list[str]:
    """
    Format classification lists for LLM prompt.

    Args:
        user_inputs: List of process inputs to classify
        activities: Available background database activities
        biosphere_flows: Available biosphere flow categories

    Returns:
        tuple: (process_list_text, biosphere_list_text, inputs_text)
            Formatted text blocks for LLM prompt
    """
    process_list_text = "\n".join(f"- {p}" for p in activities)
    biosphere_list_text = "\n".join(f"- {p}" for p in biosphere_flows)
    inputs_text = "\n".join(f"{i+1}. {inp}" for i, inp in enumerate(user_inputs))
    display(HTML("<h4>LLM input</h4>"))
    display(HTML("<h5>LCI unmapped</h5>"))
    display(inputs_text)
    #display(HTML("<h7>Processes</h7>"))
    #display(process_list_text)
    #display(HTML("<h7>Elementary flows</h7>"))
    #display(biosphere_list_text)

    return process_list_text, biosphere_list_text, inputs_text


def prompt_LLM(user_inputs, process_list_text, biosphere_list_text, inputs_text):
    """
    Send mapping request to LLM and process response.

    Args:
        user_inputs: Original input strings
        process_list_text: Formatted database activities
        biosphere_list_text: Formatted biosphere flows
        inputs_text: Numbered list of inputs to classify

    Returns:
        list: LLM mapping results matching input order
    """

    # Read the prompt from the text file
    input_dir, output_dir = h.setup_input_output()
    file_path = os.path.abspath(os.path.join(input_dir, 'llm_prompt.txt'))
    with open(file_path, 'r') as file:
        prompt_txt = file.read()

    prompt = prompt_txt.format(process_list_text=process_list_text,
                               biosphere_list_text=biosphere_list_text,
                               inputs_text=inputs_text)

    # Read the configuration from the config file
    file_path = os.path.abspath(os.path.join(input_dir, 'llm_config.txt'))
    config = h.read_config(file_path) or {}

    # Prompt for each missing entry
    api_key = config.get("api_key")
    if h.is_missing(api_key):
        api_key = h.prompt_config(key="api_key", prompt="Enter your API key", secret=True)

    base_url = config.get("base_url")
    if h.is_missing(base_url):
        base_url = h.prompt_config(key="base_url", prompt="Enter base URL (e.g., https://api.llm.com)")

    model = config.get("model")
    if h.is_missing(model):
        model = h.prompt_config(key="model", prompt="Enter LLM name/ID (e.g., qwen3-235b-a22b)")

    # Extract the API key, model name, and base URL
    kwargs = {
        "api_key": api_key,
        "base_url": base_url
    }

    cleaned_kwargs = {k: v for k, v in kwargs.items() if v is not None}

    client = OpenAI(**cleaned_kwargs)

    temperature = config.get('temperature')
    top_p = config.get('top_p')

    try:
        response=client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": "You classify user inputs to known database processes or biosphere flows with name and location or category. You convert units if necessary."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            top_p=top_p,
            timeout=900
        )

    # for models not supporting temperature, top_p
    except BadRequestError:
        response=client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": "You classify user inputs to known database processes or biosphere flows with name and location or category. You convert units if necessary."},
                {"role": "user", "content": prompt}
            ],
        )

    # Parse response
    display(HTML("<h4>LLM output</h4>"))
    output_text = response.choices[0].message.content.strip()
    display(HTML("<h5>Raw response</h5>"))
    display(output_text)

    file_path = os.path.abspath(os.path.join('..', 'output', 'llm_output.txt'))
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n{output_text}\n") # Save response to txt file

    lines = output_text.splitlines()
    results = {}
    for line in lines:
        if "." in line:
            num, process = line.split(".", 1)
            try:
                idx = int(num.strip()) - 1
                results[idx] = process.strip()
            except ValueError:
                continue
    return [user_inputs[i] if results.get(i, "unknown").lower() == "unknown" else results[i] for i in
            range(len(user_inputs))]


def split_LLM_results(results):
    """
    Parse LLM mapping results into structured DataFrame.

    Args:
        results: Raw LLM classification results

    Returns:
        pd.DataFrame: Processed results with columns:
            - name: Classified process name
            - ORIGIN: Location information
            - UNIT: Measurement unit
            - QUANTITY: Numeric value
    """
    split_results = [
        (str(r).strip().split(" | ") + [""] * 4)[:4]
        if str(r).strip().lower() != "unknown"
        else ["unknown"] * 4
        for r in results
    ]

    LCI_sheet_modify_wo_production = pd.DataFrame()
    LCI_sheet_modify_wo_production['name'] = [r[0] for r in split_results]
    LCI_sheet_modify_wo_production['ORIGIN'] = [r[1] for r in
                                                            split_results]  # exception because later location is copied
    LCI_sheet_modify_wo_production['UNIT'] = [r[2] for r in split_results]
    LCI_sheet_modify_wo_production['QUANTITY'] = [
        float(r[3]) if r[3].strip() not in ('', 'N/A', None) else 0.0
        for r in split_results
    ]

    return LCI_sheet_modify_wo_production