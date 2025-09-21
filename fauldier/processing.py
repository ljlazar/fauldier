import pandas as pd
import numpy as np
from IPython.display import display, HTML


def combine_filtered_entries(df, excluded_entries):
    """
    Filter entries until 'ANNEX' is found, excluding specified entries.

    Args:
        df (pd.DataFrame): Input DataFrame with entries
        excluded_entries (list): Entries to exclude

    Returns:
        list: Filtered entries stopping at 'ANNEX'
    """
    filtered_entries = []
    for entry in df.iloc[:, 0]:
        entry = str(entry)  # Convert entry to string to ensure proper handling
        if entry == "ANNEX":
            break  # Stop adding entries as soon as 'ANNEX' is encountered
        if entry not in excluded_entries:
            filtered_entries.append(entry)  # Add entry as a full string

    return filtered_entries


def read_and_filter_specific_sheet(file_path, sheet_name):
    """
    Read spreadsheet, skip rows, fill merged cells, and filter content.

    Args:
        file_path (str): Path to spreadsheet file
        sheet_name (str): Sheet to read

    Returns:
        pd.DataFrame: Processed DataFrame or None if sheet not found
    """

    # Load the spreadsheet file
    xls = pd.ExcelFile(file_path)

    # Check if the specified sheet exists
    if sheet_name in xls.sheet_names:

        # Read the specified sheet into a DataFrame, skipping the first 10 rows and excluding column A
        df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=12, usecols='B:N')

        # Assuming 'B' is the second column, and columns are labeled with integers starting from 0
        column_b_index = 0

        # Iterate through the DataFrame and fill down the values for merged cells in Column B
        for i in range(len(df)):
            if pd.isnull(df.iloc[i, column_b_index]) and i > 0:
                df.iloc[i, column_b_index] = df.iloc[i - 1, column_b_index]

        # Drop heading row
        texts_to_ignore = [
            "FLOW NAME"
        ]
        for text in texts_to_ignore:
            df = df[~df.apply(lambda row: row.astype(str).str.contains(text).any(), axis=1)]

        # Drop rows with NaN values
        df = df.dropna(how='all')

        # Drop rows w/o values such as subheadings etc.
        df = df.dropna(subset="QUANTITY", how='all')

        return df
    else:
        print(f"Sheet '{sheet_name}' not found in the spreadsheet file.")
        return None


def process_dataframe(df, product_list):
    """
    Handle products/by-products and update product list.

    Args:
        df (pd.DataFrame): Input DataFrame
        product_list (list): List to append product names

    Returns:
        tuple: (modified DataFrame, updated product list)
    """
    # Track count of 'PRODUCTS'
    products_count = 0
    for index, row in df.iterrows():
        if row['Unnamed: 1'] == 'PRODUCTS':
            products_count += 1
            if products_count > 1:  # If more than one 'PRODUCTS', change and modify quantity
                if not (df['DESCRIPTION'] == 'no avoided burden').any():  # Statement in sheet if no avoided burden
                    df.at[index, 'Unnamed: 1'] = 'INPUTS'
                    df.at[index, 'QUANTITY'] *= -1

                df = df[df['DESCRIPTION'] != "no avoided burden"]  # drop by-product rows

            product_list.append(df.at[index, 'FLOW NAME'])  # add product to product list

    return df, product_list


def read_and_filter_specific_description_sheet(file_path, sheet_name, LCI_sheet_description):
    """
    Read description from spreadsheet.

    Args:
        file_path (str): Spreadsheet file path
        sheet_name (str): Sheet name to read
        LCI_sheet_description: Target dict for storage

    Returns:
        tuple: (DataFrame, updated description dict)
    """

    # Load the spreadsheet file
    xls = pd.ExcelFile(file_path)

    # Check if the specified sheet exists
    if sheet_name in xls.sheet_names:
        # Read the specified sheet into a DataFrame, skipping the first 10 rows and excluding column A
        df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=2, nrows=5, usecols='B,D', index_col=0)
        return df, LCI_sheet_description
    else:
        print(f"Sheet '{sheet_name}' not found in the spreadsheet file.")
        return None


def read_and_filter_specific_bw_sheet(file_path, sheet_name):
    """
    Read Brightway example sheet with minimal processing.

    Args:
        file_path (str): Spreadsheet file path
        sheet_name (str): Sheet name to read

    Returns:
        pd.DataFrame: Raw DataFrame or None if missing
    """

    # Load the spreadsheet file
    xls = pd.ExcelFile(file_path)

    # Check if the specified sheet exists
    if sheet_name in xls.sheet_names:
        # Read the specified sheet into a DataFrame, skipping the first 10 rows and excluding column A
        df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=1, header=None, engine="openpyxl")
        return df
    else:
        print(f"Sheet '{sheet_name}' not found in the spreadsheet file.")
        return None


def description_to_bw_input_sheet(bw_example_sheet, bw_example_sheets, LCI_sheet_description,
                                  LCI_sheet, sheet_name, activity_database_name):
    """
    Merge project data into Brightway example template.

    Args:
        bw_example_sheet: Template DataFrame
        bw_example_sheets: Target dict for results
        LCI_sheet_description: Source metadata
        LCI_sheet: Process data source
        sheet_name (str): Current sheet name
        activity_database_name (str): Database name

    Returns:
        dict: Updated bw_example_sheets
    """
    bw_example_sheet_modify = bw_example_sheet.copy()
    LCI_sheet_description_modify = LCI_sheet_description[sheet_name]
    LCI_sheet_modify = LCI_sheet[sheet_name]
    LCI_sheet_modify = LCI_sheet_modify.iloc[0]  # first row is used ("Product")

    # Insert description data in bw example sheet
    bw_example_sheet_modify.iloc[0, 1] = activity_database_name

    bw_example_sheet_modify.iloc[1, 1] = activity_database_name

    bw_example_sheet_modify.iloc[4, 1] = LCI_sheet_description_modify.loc[
        'Process name', LCI_sheet_description_modify.columns[0]]

    bw_example_sheet_modify.iloc[5, 1] = activity_database_name
    process_name = LCI_sheet_description_modify.loc[
        'Process name', LCI_sheet_description_modify.columns[0]]
    bw_example_sheet_modify.iloc[6, 1] = f"{activity_database_name}-{process_name}"

    bw_example_sheet_modify.iloc[7, 1] = LCI_sheet_description_modify.loc[
        'Description of the process:', LCI_sheet_description_modify.columns[0]]

    bw_example_sheet_modify.iloc[8, 1] = None

    bw_example_sheet_modify.iloc[9, 1] = LCI_sheet_modify.loc['location']

    bw_example_sheet_modify.iloc[12, 1] = LCI_sheet_modify.loc['unit']

    # Delete entries in bw input sheet
    bw_example_sheet_modify = bw_example_sheet_modify.iloc[:15]
    #display(bw_example_sheet_modify)

    # Write modified sheet to dictionary
    bw_example_sheets[sheet_name] = bw_example_sheet_modify
    display(sheet_name)
    #display(bw_example_sheets[sheet_name])

    return bw_example_sheets


def merge_sheets(LCI_sheet, bw_example_sheets, sheet_names):
    """
    Combine processed sheets into final output format.

    Args:
        LCI_sheet: Process data
        bw_example_sheets: Template data
        sheet_names (list): Sheets to process

    Returns:
        pd.DataFrame: Final merged DataFrame
    """
    is_first_iteration = True
    is_first_iteration_2 = True
    final_bw_input_sheet = None

    for sheet_name in sheet_names:

        # Selecting columns
        name_position = LCI_sheet[sheet_name].columns.get_loc('name')
        LCI_sheet_selected = LCI_sheet[sheet_name].iloc[:, name_position:]

        if is_first_iteration:
            bw_example_sheet_selected = bw_example_sheets[sheet_name].iloc[:, :]
            display(bw_example_sheet_selected)
            display(LCI_sheet_selected)
            is_first_iteration = False
        else:
            bw_example_sheet_selected = bw_example_sheets[sheet_name].iloc[3:, :]

        if is_first_iteration_2:
            new_bw_example_sheet_data = pd.DataFrame(
                np.concatenate([bw_example_sheet_selected.values, LCI_sheet_selected.values]),
                columns=bw_example_sheet_selected.columns
            )
            final_bw_input_sheet = new_bw_example_sheet_data
            is_first_iteration_2 = False
        else:
            new_bw_example_sheet_data = pd.DataFrame(
                np.concatenate([bw_example_sheet_selected.values, LCI_sheet_selected.values]),
                columns=bw_example_sheet_selected.columns
            )
            final_bw_input_sheet = pd.DataFrame(
                np.concatenate([final_bw_input_sheet.values, new_bw_example_sheet_data.values]),
                columns=final_bw_input_sheet.columns
            )

    return final_bw_input_sheet