<img src="fauldier_logo.svg" alt="alt text" width="30%" height="30%">

**F**ramework for l**A**rge lang**U**age mode**L** assiste**D** l**I**fe cycl**E** invento**R**y

## Overview
FAULDIER is an framework designed to automate e the transformation of heterogeneous input data into standardized formats for **Life Cycle Assessment (LCA)**. Leveraging **Large Language Models (LLMs)**, FAULDIER addresses the persistent challenges of aligning raw user inputs with Life Cycle Inventory (LCI) database nomenclature, enabling more efficient and accurate LCA modeling.

## Key Features
- **Automated Data Harmonization**  
  - Resolves naming inconsistencies between user inputs and LCI databases.  
  - Classifies flow types and harmonizes units and locations.
- **Error Handling & Robustness**  
  - Corrects typographical errors and manages linguistic variations.  
  - Handles location granularity mismatches and unit inconsistencies.
- **Multilingual Support**  
  - Processes inputs in multiple languages for global applicability.
- **Proxy Selection**  
  - Suggests suitable proxies for missing processes.
- **Prospective Modeling & Uncertainty Analysis**  
  - Facilitates advanced LCA applications by reducing manual preprocessing.

## Why FAULDIER?
Traditional rule-based mapping approaches often fail due to:
- Linguistic variations and typos.
- Unit and location mismatches.
- Lack of adaptability to evolving data and terminology.

FAULDIER overcomes these limitations by using LLMs to interpret and map data intelligently, even under non-standardized conditions.

## Performance Highlights
- **Name-Mapping Accuracy:** ~60% in real-world simulation scenarios.
- **Unit Conversion Error:** <1% in most cases.
- **Robustness:** Handles multilingual entries, typos, and inconsistent units effectively.

## Current Limitations
- Database constraints and token limitations.
- Performance variability across different LLMs.
- Need for confidence metrics for mapped data.

## Future Directions
- Expand testing across multiple LCI databases and use cases.
- Develop confidence scoring for mappings.
- Explore integration with additional LLM architectures.
- Improve scalability for large datasets.

## Getting Started
### Prerequisites
- Python 3.10+
- Access to an LLM API 


### Installation
```bash
git clone https://github.com/your-org/fauldier.git
cd fauldier
pip install -r requirements.txt
```

### Usage
```bash
python fauldier.py --input your_data.csv --database ecoinvent
```

## Citation
If you use FAULDIER in your research, please cite:
```
[Your Citation Here]
```

## License
[MIT License](LICENSE)
