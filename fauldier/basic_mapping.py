import pandas as pd
import numpy as np
import re

from IPython.display import display, HTML
from thermo import *


def map_common_names(LCI_sheet_modify):
    """
    Map common process names to standardized ecoinvent equivalents.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with 'name' column to standardize

    Returns:
        pd.DataFrame: Modified DataFrame with standardized process names
    """

    # Define the conditions
    conditions = [
        LCI_sheet_modify['name'].str.contains('#electricity', case=False, na=False),
        LCI_sheet_modify['name'].str.contains(
            'process heat|heating|industrial heat', case=False, na=False),
        LCI_sheet_modify['name'].str.contains('#natural gas', case=False, na=False),
        LCI_sheet_modify['name'].str.contains('waste water', case=False, na=False),
        LCI_sheet_modify['name'].str.contains('CO2, fossil', case=False, na=False),
        LCI_sheet_modify['name'].str.contains('CO2, biogenic', case=False, na=False),
        LCI_sheet_modify['name'].str.contains(r'#cooling(?!.*Water, cooling, unspecified natural origin\b)',
                                                          case=False, na=False, regex=True),

    ]

    # Define the choices corresponding to the conditions
    choices = [  # If 'name' contains xy
        'market group for electricity, medium voltage',
        'market for heat, from steam, in chemical industry',
        'market group for natural gas, high pressure',
        'market for wastewater, average',
        'Carbon dioxide, fossil',
        'Carbon dioxide, from soil or biomass stock',
        'market for cooling energy'
    ]

    # Ensuring original values are used when no conditions are met
    conditions.append(True)
    choices.append(LCI_sheet_modify['name'])

    # Apply conditions and choices, with default value for all other cases
    LCI_sheet_modify['name'] = np.select(conditions, choices)

    return LCI_sheet_modify


def ecoinvent_3_10_names(LCI_sheet_modify):
    """
    Adjust names for ecoinvent 3.10 compatibility.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with process names

    Returns:
        pd.DataFrame: Modified DataFrame with ecoinvent 3.10-compliant names
    """

    # Waste --> scrap
    LCI_sheet_modify['name'] = LCI_sheet_modify['name'].str.replace(
        'waste steel', 'scrap steel',  # regex=True
    ).str.replace(
        'waste aluminium', 'scrap aluminium',  # regex=True
    ).str.replace(
        'waste copper', 'scrap copper',  # regex=True
    )

    # acetic acid
    LCI_sheet_modify['name'] = LCI_sheet_modify['name'].str.replace(
        'market for acetic acid', 'market for acetic acid, without water, in 98% solution state',  # regex=True
    )

    # hexamethylenediamine
    LCI_sheet_modify.loc[
        LCI_sheet_modify['name'].eq('market for hexamethylenediamine'),
        'ORIGIN'
    ] = 'GLO'

    return LCI_sheet_modify


def unit_conversion(LCI_sheet_modify):
    """
    Convert units using substance-specific conversion functions.

    Applies multiple check_and_convert_* functions to handle different chemical substances.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with unit/amount columns

    Returns:
        pd.DataFrame: Modified DataFrame with standardized units
    """
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_heat, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_natural_gas, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_waste_water, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_water, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_ethanol, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_methanol, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_argon, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_nitrogen, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_toluene, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_acetone, axis=1)
    LCI_sheet_modify = LCI_sheet_modify.apply(check_and_convert_hexane, axis=1)

    # Give "chemical factory" a unit if not provided
    LCI_sheet_modify.loc[
        LCI_sheet_modify['name'].str.contains('market for chemical factory, organics', case=False,
                                                          na=False),
        'unit'] = "unit"

    return LCI_sheet_modify


def map_unit(unit):
    """
    Map unit abbreviations to full names.

    Args:
        unit (str): Unit abbreviation (kg, kWh, m3, etc.)

    Returns:
        str: Full unit name or original if no match
    """
    if unit == 'kg':
        return 'kilogram'
    if unit == 't':
        return 'ton'
    elif unit == 'kWh':
        return 'kilowatt hour'
    elif unit == 'm3':
        return 'cubic meter'
    elif unit == 'm2':
        return 'square meter'
    elif unit == 'MJ':
        return 'megajoule'
    elif unit == 'unit':
        return 'unit'
    elif unit == 'ml':
        return 'milliliter'
    elif unit == 'l':
        return 'liter'
    else:
        return unit


def check_and_convert_heat(row):
    """Convert heat units from kWh to MJ."""
    # Adjust if heat is provided in kWh --> MJ
    # Conversion factor from kWh to MJ
    conversion_heat = 3.6
    print(row['name'])
    if 'heat' in row['name'].lower() or 'heating' in row['name'].lower() or 'cooling' in row['name'].lower():
        if row['unit'] == 'kilowatt hour':
            row['unit'] = 'megajoule'
            row['amount'] *= conversion_heat
    return row


def check_and_convert_natural_gas(row):
    """Convert natural gas units from kg to m³."""
    conversion_natural_gas = 0.735 # 0.735 kg/m3 density according to ecoinvent "market group for natural gas, high pressure"
    if 'natural gas' in row['name'].lower():
        if row['unit'] == 'kilogram':
            row['unit'] = 'cubic meter'
            row['amount'] /= conversion_natural_gas
    return row


def check_and_convert_waste_water(row):
    """Convert waste water units from kg to m³."""
    conversion_waste_water = 998 #  kg/m3 density according to standard conditions
    if 'waste water' in row['name'].lower() or 'wastewater' in row['name'].lower():
        if row['unit'] == 'kilogram':
            row['unit'] = 'cubic meter'
            row['amount'] /= conversion_waste_water
    return row


def check_and_convert_water(row):
    """Convert water units from liters or mmol to kg."""
    rho_water = Chemical('water', T=293.15).rho #  kg/m3 density according to standard conditions
    if 'market for water, ultrapure' in row['name'].lower():
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1000 # l --> m3
            row['amount'] *= rho_water  # rho=m/V -->m = rho*V
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1000000  # l --> m3
            row['amount'] *= rho_water  # rho=m/V -->m = rho*V
        if row['unit'] == 'mmol':
            row['unit'] = 'kilogram'
            row['amount'] /= 1000 # mmol --> mol
            row['amount'] *= Chemical('water', T=293.15).MW  # rho=m/V -->m = rho*V
    return row


def check_and_convert_ethanol(row):
    """Convert ethanol units from ml or l to kg using density."""
    conversion_ethanol = Chemical('ethanol', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\bethanol\b[^\w]*', row['name'], re.IGNORECASE): # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6 # ml --> m3
            row['amount'] *= conversion_ethanol
            print('ethanol converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3 # l --> m3
            row['amount'] *= conversion_ethanol # m3 --> kg
    return row


def check_and_convert_methanol(row):
    """Convert methanol units from ml or l to kg using density."""
    conversion_methanol = Chemical('methanol', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\bmethanol\b[^\w]*', row['name'], re.IGNORECASE): # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6 # ml --> m3
            row['amount'] *= conversion_ethanol
            print('methanol converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3 # l --> m3
            row['amount'] *= conversion_methanol # m3 --> kg
    return row


def check_and_convert_argon(row):
    """Convert argon units from ml or l to kg using density."""
    conversion_argon = Chemical('argon', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\bargon\b[^\w]*', row['name'], re.IGNORECASE):  # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6  # ml --> m3
            row['amount'] *= conversion_argon
            print('methanol converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3  # l --> m3
            row['amount'] *= conversion_argon  # m3 --> kg
    return row


def check_and_convert_nitrogen(row):
    """Convert nitrogen units from ml or l to kg using density."""
    conversion_nitrogen = Chemical('nitrogen', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\bnitrogen\b[^\w]*', row['name'], re.IGNORECASE):  # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6  # ml --> m3
            row['amount'] *= conversion_nitrogen
            print('nitrogen converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3  # l --> m3
            row['amount'] *= conversion_nitrogen  # m3 --> kg
    return row


def check_and_convert_toluene(row):
    """Convert toluene units from ml/l to kg using density."""
    conversion_toluene = Chemical('toluene', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\btoluene\b[^\w]*', row['name'], re.IGNORECASE):  # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6  # ml --> m3
            row['amount'] *= conversion_toluene
            print('toluene converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3  # l --> m3
            row['amount'] *= conversion_toluene  # m3 --> kg
    return row


def check_and_convert_acetone(row):
    """Convert acetone units from ml or l to kg using density."""
    conversion_acetone = Chemical('acetone', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\bacetone\b[^\w]*', row['name'], re.IGNORECASE):  # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6  # ml --> m3
            row['amount'] *= conversion_acetone
            print('acetone converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3  # l --> m3
            row['amount'] *= conversion_acetone  # m3 --> kg
    return row


def check_and_convert_hexane(row):
    """Convert hexane units from ml or l to kg using density."""
    conversion_hexane = Chemical('hexane', T=293.15).rho  # kg/m3 density according to thermo
    if re.search(r'\bhexane\b[^\w]*', row['name'], re.IGNORECASE):  # includes , and . after word
        if row['unit'] == 'milliliter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e6  # ml --> m3
            row['amount'] *= conversion_hexane
            print('hexane converted ml --> m3, new value: ', row['amount'])
        if row['unit'] == 'liter':
            row['unit'] = 'kilogram'
            row['amount'] /= 1e3  # l --> m3
            row['amount'] *= conversion_hexane  # m3 --> kg
    return row


def set_category_to_air(LCI_sheet_modify):
    """
    Set 'categories' to 'air' for CO2-related processes.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with 'name' column

    Returns:
        pd.DataFrame: Modified DataFrame with updated categories
    """
    LCI_sheet_modify.loc[LCI_sheet_modify['name'].str.contains(
        "Carbon dioxide, fossil|Carbon dioxide, from soil or biomass stock", case=False,
        na=False), 'categories'] = 'air'

    return LCI_sheet_modify


def set_category_from_location(LCI_sheet_modify):
    """
    Set categories from ORIGIN column when containing environmental compartments.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with 'ORIGIN' column

    Returns:
        pd.DataFrame: Modified DataFrame with environmental categories
    """

    # For biosphere where destination (e.g. 'air') is provided in ORIGIN instead of e.g. RER,...
    LCI_sheet_modify.loc[
        LCI_sheet_modify['ORIGIN'].astype(str).str.contains(
            r'\b(?:water|air|natural|soil|inventory|economic)\b[:;,]*',
            regex=True, na=False), 'categories'
    ] = LCI_sheet_modify['ORIGIN']

    return LCI_sheet_modify


def set_location(LCI_sheet_modify):
    """
    Set location codes based on ORIGIN and specific rules.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with 'ORIGIN' column

    Returns:
        pd.DataFrame: Modified DataFrame with standardized locations
    """

    LCI_sheet_modify.loc[LCI_sheet_modify['ORIGIN'].isin(['EUR', 'EU']), 'location'] = 'RER'

    # If no entry is provided guess that is RER
    LCI_sheet_modify['location'] = LCI_sheet_modify['location'].replace('', pd.NA)
    LCI_sheet_modify['location'] = LCI_sheet_modify['location'].fillna('RER')

    # Activities that use EU w/o Switzerland instead of RER
    LCI_sheet_modify.loc[LCI_sheet_modify[
                                         'name'] == 'market group for natural gas, high pressure', 'location'] = (
                                                        'Europe without Switzerland')
    LCI_sheet_modify.loc[LCI_sheet_modify[
                                         'name'] == 'market for wastewater, average', 'location'] = (
                                                    'Europe without Switzerland')

    # Activities that use GLO instead of RER
    LCI_sheet_modify.loc[
        LCI_sheet_modify['name'] == 'market for cooling energy', 'location'] = 'GLO'
    LCI_sheet_modify.loc[
        LCI_sheet_modify['name'] == 'market for chemical factory, organics', 'location'] = 'GLO'

    return LCI_sheet_modify


def set_type(LCI_sheet_modify):
    """
    Classify processes as production/biosphere/technosphere.

    Args:
        LCI_sheet_modify (pd.DataFrame): DataFrame with 'name' column

    Returns:
        pd.DataFrame: Modified DataFrame with type classifications
    """
    conditions = [

        LCI_sheet_modify['Unnamed: 1'].str.contains('PRODUCTS', case=False, na=False),

        LCI_sheet_modify['categories'].astype(str).str.contains(r'(?:water|air|natural|soil)',
                                                                            regex=True, na=False),
    ]

    # Define the choices corresponding to the conditions
    choices = [
        'production',  # If 'name' contains 'production'
        'biosphere',
    ]

    # Apply conditions and choices, with default value for all other cases
    LCI_sheet_modify['type'] = np.select(conditions, choices, default='technosphere')

    return LCI_sheet_modify


def determine_database(row, background_database_name, activity_database_name):
    """
    Determine database name based on process type.

    Args:
        row (pd.Series): DataFrame row with 'type' column
        background_database_name (str): Name for background database
        activity_database_name (str): Name for activity database

    Returns:
        str: Database name based on process type
    """
    if row['type'] == 'biosphere':
        return 'biosphere3'
    elif row['type'] == 'technosphere':
        return background_database_name
    elif row['type'] == 'production':
        return activity_database_name
    else:
        return None

