<img src="fauldier_logo.svg" alt="alt text" width="30%" height="30%">

#

FAULDIER (**F**ramework for l**A**rge lang**U**age mode**L** assiste**D** l**I**fe cycl**E** invento**R**y) aims to automate the transformation of heterogeneous inventory data into standardized formats for **Life Cycle Assessment (LCA)**, utilizing **Large Language Models (LLMs)**.

## Table of Contents
- [Description](#description)
- [Getting Started](#getting-started)
- [Citation](#citation)
- [License](#license)

## Description
For a comprehensive overview, please refer to the following publication:  
```
[Reference coming soon]
```
### Key Features

- **Process and Elementary Flow Mapping**  
  - Transforms incomplete inventory data from spreadsheets into a Brightway-compatible LCA database.  
  - Supports customizable, rule-based transformation.

- **LLM-Assisted Mapping and Harmonization**  
  - Automates mapping of non-standardized input data to Life Cycle Inventory (LCI) database formats using LLMs.  
  - Corrects typographical errors, resolves linguistic variations, and supports multilingual inputs.  
  - Converts units and harmonizes location granularity mismatches.  
  - Selects proxies for missing processes.

- **Dynamic Adaptation to Databases and Database Updates** *(not tested)*  
  - In principle, the LLM-based approach enables adaptation to changes in database terminology, structural modifications, and integration with other databases.

- **Open & Transparent Implementation**  
  - Built with open software, databases and open-weight LLMs.

- **Future-Oriented Design**  
  - Designed to support prospective modeling and software coupling, enabling handling of uncertain and non-standardized data inputs.

### **Current Limitations**
- Database constraints (e.g., license restrictions) and token limitations.  
- Performance variability across different LLMs and between runs.  
- Limited performance of open-weight LLMs.
- Lack of confidence metrics for mapped data.

### **Future Directions**
- Broaden testing across multiple LCI databases and diverse use cases.  
- Develop pre-processing strategy for improved efficiency.  
- Implement confidence scoring for mappings.  
- Explore integration with additional LLM architectures to improve mapping results.

## Getting Started

### **Requirements**
- Access to an LLM API.  
- Python (tested with **3.10**)  
- Life Cycle Inventory database (tested with **FORWAST**)  

### Installation

#### Option 1: With brightway2 environment
If you already have [Brightway2](https://docs.brightway.dev/en/legacy/content/installation/installation.html) or [Activity Browser](https://github.com/LCA-ActivityBrowser/activity-browser) installed, you only need to add [JuptyerLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html), [thermo](https://github.com/CalebBell/thermo), and [openai-python](https://github.com/openai/openai-python).
```bash
pip install jupyterlab thermo openai
```
#### Option 2: Install from GitHub
You can install the package and its main dependencies directly from the GitHub repository using pip.
```bash
pip install git+https://github.com/ljlazar/fauldier.git jupyterlab
```

#### Option 3: Run on binder
Run the example notebook '/example/LCA_LLM.ipyn' directly in a cloud environment with [Binder](https://mybinder.org/). No local installation is required.

### First Steps
To see an example, run the `LCA_LLM.ipynb` notebook located in the `/example/` directory.

The notebook includes instructions on how to restore the FORWAST database if you do not have it installed (this can also be done via Brightway or the Activity Browser: Import database > Import remote data > Forwast).

## Citation
If you use FAULDIER in your research, please cite:
```
[Reference coming soon]
```
Thank you!

## License
[BSD-3-Clause](LICENSE) &copy; 2025 Lukas Lazar
