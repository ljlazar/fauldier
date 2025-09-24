<img src="fauldier_logo.svg" alt="alt text" width="30%" height="30%">

#

FAULDIER (**F**ramework for l**A**rge lang**U**age mode**L** assiste**D** l**I**fe cycl**E** invento**R**y) aims to automate the transformation of heterogeneous input data into standardized formats for **Life Cycle Assessment (LCA)**, utilizing **Large Language Models (LLMs)**.

## 🔑 Key Features

- **Process and Elementary Flow Mapping**  
  - Enables automated mapping of raw input data from a spreadsheet to the Brightway LCA software, with support for customizable, rule-based transformations to ensure compliance with database requirements.

- **LLM-Assisted Data Harmonization**  
  - Automates mapping of non-standardized input data to Life Cycle Inventory (LCI) database requirements using Large Language Models (LLMs).
  - Corrects **typographical errors**, resolves **linguistic variations**, and supports **multilingual inputs**.
  - Converts units. 
  - Harmonizes location granularity mismatches.
  - Selects proxies for missing processes.
  - 
- **Dynamic Adaptation to Database Updates** (not tested)  
  - LLM assistance enables the system to adapt to changes in database terminology, structural modifications, and integration with other databases.

- **Open & Transparent Implementation**  
  Built with **open databases** and **open-weight LLMs**.

- **Future-Oriented Design**  
  Aims to support **prospective modeling**, and **software coupling**, enabling handling of uncertain and non-standardized data inputs. 

## Current Limitations
- Database constraints (license restrictions) and token limitations.
- Performance variability across different LLMs and in between LLM runs.
- Performance of open-weight LLMs.
- Need for confidence metrics for mapped data.

## Future Directions
- Expand testing across multiple LCI databases and use cases.
- Develop pre-processing procedures.
- Develop confidence scoring for mappings.
- Explore integration with additional LLM architectures.

## Getting Started
### Prerequisites
- API to an Large Language Model

### Requirements
- Python
- Life Cycle Inventory database

### 📦 Installation
### Option 1: with brightway2 or Activity Browser
If you have [Brightway2](https://docs.brightway.dev/en/legacy/content/installation/installation.html) or [Activity Browser](https://github.com/LCA-ActivityBrowser/activity-browser), you only need to install [juptyerlab(https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html) [thermo](https://github.com/CalebBell/thermo) and [openai-python](https://github.com/openai/openai-python) and you can run the notebook in the example folder.

```bash
pip install jupyterlab thermo openai
```

### Option 2: from scratch
You can install the package including dependencies directly from the GitHub repository, via pip or run the /example/LCA_LLM.ipynb. 
```bash
pip install git+https://github.com/ljlazar/fauldier.git jupyterlab
```

### Option 3: run on binder
You can run the the /example/LCA_LLM.ipynb directly on [binder](https://mybinder.org/). Be aware not to save your LLM API_key if using binder (you have to put in your API_key several times unfortunately, if you do not save it).


## Citation
If you use FAULDIER in your research, please cite:
```
[Your Citation Here]
```

## License
[BSD-3-Clause](LICENSE) &copy; 2025 Lukas Lazar
