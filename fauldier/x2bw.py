import os
import pandas as pd

from IPython.display import display, HTML
from openai import OpenAI

from . import processing as p
from . import basic_mapping as m
from . import helper as h
from . import llm_mapping as llm

module_dir = os.path.dirname(__file__)


def x2bw_transformation(activity_database_name,
                        xls_file_path,
                        excluded_entries,
                        background_database_name,
                        LLM_mapping=False,
                        BG_DB_activities=[],
                        biosphere_flows=[],
                        ecoinvent_version='3.10',
                        ):
    """
    Convert spreadsheets to Brightway2 input format with optional LLM-based mapping.

    LCI data from spreadsheet file LCA_LCI_xy.xlsx and transforms it into the
    Brightway2 input file. Supports both LLM-based and exemplary rule-based
    mapping to background databases.

    Args:
        activity_database_name (str): Name for the activity database
        xls_file_path (str): Path to input spreadsheet file containing data sheets
        excluded_entries (list): List of sheet names to exclude from processing
        background_database_name (str): Name of the background database
        LLM_mapping (bool): If True, uses Large Language Model (LLM) for activity mapping
        BG_DB_activities (list): List of background database activities
        biosphere_flows (list): List of biosphere flows
        ecoinvent_version (str, optional): Ecoinvent version for name mapping.
                                           Defaults to '3.10'.

    Returns:
        pandas.DataFrame: Final merged Brightway2 input sheet saved as
                          'bw_input_sheet.xlsx'. Contains processed data with
                          standardized naming, units, locations, and database
                          classifications.

    Notes:
        - Handles by-product conversion to negative inputs (avoided burden approach)
        - Applies basic mapping with keywords such as "#electricity" and basic unit conversion
        - When LLM_mapping=True, uses LLM for mapping and unit transformation (see LLM_prompt.txt)
    """

    # Import LCI data sheet
    display(HTML("<h2>LCI data sheets</h2>"))
    file_path = xls_file_path
    sheet_name = 'SheetNames'
    df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=[1])
    sheet_names = p.combine_filtered_entries(df, excluded_entries)

    # Read and filter sheets
    LCI_sheet = {}

    for sheet_name in sheet_names:
        LCI_sheet[sheet_name] = p.read_and_filter_specific_sheet(xls_file_path, sheet_name)
        display(HTML(f"<h3>{sheet_name}</h3>"))
        display(LCI_sheet[sheet_name])

    # Handle by-products to avoided burden
    display(HTML("<h2>By-product handling</h2>"))
    product_list = []  # list to save products

    for sheet_name in sheet_names:
        df = LCI_sheet[sheet_name]
        df_processed, product_list = p.process_dataframe(df, product_list)
        LCI_sheet[sheet_name] = df_processed
        display(HTML(f"<h3>{sheet_name}</h3>"))
        display(df_processed)

    # Import DESCRIPTION sheet
    display(HTML("<h2>DESCRIPTION sheets</h2>"))
    LCI_sheet_description = {}

    for sheet_name in sheet_names:
        LCI_sheet_description[
            sheet_name], LCI_sheet_description = p.read_and_filter_specific_description_sheet(
            xls_file_path, sheet_name, LCI_sheet_description)
        display(HTML(f"<h3>{sheet_name}</h3>"))
        display(LCI_sheet_description[sheet_name])


    # Modify LCI sheet to fit to bw input sheet, map processes and elmentary flows
    display(HTML("<h2>Mapping of processes and elementary flows</h2>"))

    for sheet_name in sheet_names:
        display(HTML(f"<h3>{sheet_name}</h3>"))
        LCI_sheet_modify = LCI_sheet[sheet_name]

        # name
        LCI_sheet_modify['name'] = LCI_sheet_modify['FLOW NAME']

        # LLM mapping (if LLM_mapping == True)
        if LLM_mapping:

            # Get user inputs from DataFrame, filter products, convert to | separated list
            user_inputs, product_row, internal_activities, LCI_sheet_modify_wo_production = llm.transform_data_for_LLM(LCI_sheet_modify,
                                                                                       product_list)

            # Display and save before mapping
            LCI_sheet_modify_before_LLM = LCI_sheet_modify_wo_production[
                ['name', 'ORIGIN', 'UNIT', 'QUANTITY']].copy()

            # Classify results for LLM
            process_list_text, biosphere_list_text, inputs_text = llm.classify_input_batch(user_inputs,
                                                                                           BG_DB_activities,
                                                                                           biosphere_flows)
            # Get results from LLM prompt
            results = llm.prompt_LLM(user_inputs, process_list_text, biosphere_list_text, inputs_text)

            # Split LLM results into separate columns
            LCI_sheet_modify_wo_production = llm.split_LLM_results(results)

            # Recombine products and filtered list
            LCI_sheet_modify = pd.concat(
                [product_row, LCI_sheet_modify_wo_production, internal_activities],
                axis=0).drop_duplicates().reset_index(drop=True)

            # Compare results before and after mapping
            LCI_sheet_modify_after_LLM = LCI_sheet_modify_wo_production[['name', 'ORIGIN', 'UNIT', 'QUANTITY']].copy()
            h.compare_results(LCI_sheet_modify_before_LLM, LCI_sheet_modify_after_LLM)

        # Amount
        LCI_sheet_modify['amount'] = LCI_sheet_modify['QUANTITY']

        # Non LLM mapping
        if LLM_mapping == False:
            LCI_sheet_modify = m.map_common_names(LCI_sheet_modify)

            # modify ecoinvent 3.10 specific names (if sheet input is 3.11)
            if ecoinvent_version == '3.10':
                LCI_sheet_modify = m.ecoinvent_3_10_names(LCI_sheet_modify)

        # Units
        LCI_sheet_modify['unit'] = LCI_sheet_modify['UNIT'].apply(m.map_unit)

        # Apply exemplary unit conversion
        if LLM_mapping == False:
            LCI_sheet_modify = m.unit_conversion(LCI_sheet_modify)

        # Database
        LCI_sheet_modify['database'] = None

        # Categories
        LCI_sheet_modify['categories'] = None

        # Set category for common emissions
        if LLM_mapping == False:
            LCI_sheet_modify = m.set_category_to_air(LCI_sheet_modify)

        # categories provided in location
        LCI_sheet_modify = m.set_category_from_location(LCI_sheet_modify)

        # Location
        LCI_sheet_modify['location'] = LCI_sheet_modify['ORIGIN']
        LCI_sheet_modify = m.set_location(LCI_sheet_modify)

        # Type
        LCI_sheet_modify = m.set_type(LCI_sheet_modify)

        # Assign type to database
        LCI_sheet_modify['database'] = LCI_sheet_modify.apply(m.determine_database, axis=1,
                                                                                      args=(background_database_name,
                                                                                            activity_database_name))

        # Others
        LCI_sheet_modify['uncertainty type'] = None
        LCI_sheet_modify['loc'] = None
        LCI_sheet_modify['scale'] = None
        LCI_sheet_modify['shape'] = None
        LCI_sheet_modify['minimum'] = None
        LCI_sheet_modify['maximum'] = None

        # Save sheet in dictionary
        LCI_sheet[sheet_name] = LCI_sheet_modify

        # Display the DataFrame scrollable
        #h.display_dataframe_scroll(LCI_sheet_modify)

    # Read bw input sheet example
    display(HTML("<h2>Brightway input sheet example</h2>"))

    # Path to the file
    xls_file_path = os.path.abspath(os.path.join(module_dir, 'data', 'basic_example.xlsx'))

    # Sheet name to read and filter
    sheet_name = 'first process'

    # Read and filter the specified sheet
    bw_example_sheet = p.read_and_filter_specific_bw_sheet(xls_file_path, sheet_name)

    # Example to display the DataFrame
    display(bw_example_sheet)


    # Modify bw input sheet with description of LCI sheet and delete example data
    display(HTML("<h2>Add description of project partner sheet and delete example data</h2>"))
    bw_example_sheets = {}

    for sheet_name in sheet_names:
        bw_example_sheets = p.description_to_bw_input_sheet(bw_example_sheet, bw_example_sheets,
                                                            LCI_sheet_description, LCI_sheet,
                                                            sheet_name, activity_database_name)

    # Merging sheets
    display(HTML("<h2>Merging sheets, output sheet for bw input</h2>"))
    final_bw_input_sheet = p.merge_sheets(LCI_sheet, bw_example_sheets, sheet_names)

    # Save final sheet to spreadsheet, which can be used as input file to brightway2
    input_dir, output_dir = h.setup_input_output()
    file_path = os.path.abspath(os.path.join(output_dir, 'bw_input_sheet.xlsx'))
    final_bw_input_sheet.to_excel(file_path, index=False, header=False)
    h.display_dataframe_scroll(final_bw_input_sheet)
