# A Study on Adoption of Online Vehicle Insurance in Bengaluru
This repository contains the replication pipeline, statistical code, econometric models, and de-identified primary dataset for the empirical study: "A Study on Adoption of Online Vehicle Insurance in Bengaluru".


# 1. Project Overview & Abstract
Motor insurance represents the largest non-life retail insurance sector in India and is legally mandatory under the Motor Vehicles Act, 1988 (and its 2019 Amendment). While digital ecosystems (UPI, India Stack, web aggregators, and D2C InsurTech carriers) provide lower premiums and instant issuance, an urban market paradox persists in Bengaluru: a notable segment of tech-literate vehicle owners continues to purchase and renew motor insurance through traditional offline intermediaries (agents, brokers, and dealership desks).
Grounding the investigation in an Integrated UTAUT2 & Risk-Trust Theoretical Model, this study investigates the structural, financial, and psychological determinants governing digital channel choice versus offline intermediary retention. Primary data was gathered from validated vehicle owners across Bengaluru.


# 2. Theoretical Framework
The empirical model bridges utilitarian technology adoption theory with executory financial contract risk (Intergrated UTAUT2 & Risk-Trust Model) to find out the behavioural intention of the consumers.


# 3. Repository Architecture
├── data/
│   ├── raw/
│   │   └── survey_responses_raw.xlsx          # Raw survey output (N=237)
│   ├── processed/
│   │   ├── survey_responses_audited_232.csv   # Screened & validated dataset (N=232)
│   │   └── data_dictionary.md                 # Complete variable codebook
├── notebooks/
│   ├── 01_data_cleaning_and_validation.ipynb  # Screening audit & missing data checks
│   ├── 02_scale_reliability_cronbach.ipynb    # Item variances & Cronbach's Alpha
│   ├── 03_descriptive_and_bivariate.ipynb     # Frequencies, crosstabs, and Chi-square
│   └── 04_econometric_modeling.ipynb          # Binary Logistic Regression & OLS models
├── scripts/
│   ├── run_all_analysis.py                    # End-to-end command-line reproduction
│   └── econometric_utils.py                   # Helper functions for odds ratios & diagnostics
├── outputs/
│   ├── tables/                                # Exported regression and crosstab CSVs
│   └── figures/                               # Exported charts and model plots
├── requirements.txt                           # Frozen Python dependencies
├── LICENSE                                    # Open-source license (MIT)
└── README.md                                  # Repository documentation


# 4. Installation and Setup
Prerequisites
Python 3.9, 3.10, or 3.11

# Environment Installation
Clone the repository:
git clone [https://github.com/your-username/online-motor-insurance-adoption-bengaluru.git](https://github.com/your-username/online-motor-insurance-adoption-bengaluru.git)
cd online-motor-insurance-adoption-bengaluru

# Create and activate a virtual environment:
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
# On Windows
python -m venv venv
venv\Scripts\activate

# Install required dependencies:
pip install --upgrade pip
pip install -r requirements.txt

# Core Dependencies (requirements.txt)
Plaintext
numpy>=1.23.0
pandas>=1.5.0
scipy>=1.9.0
statsmodels>=0.13.5
matplotlib>=3.6.0
seaborn>=0.12.0
openpyxl>=3.0.10


# 5. Replication Workflow
One-Click Command Line Execution.
To reproduce all descriptive metrics, scale reliabilities, Chi-square contingency tests, and regression models:

python scripts/run_all_analysis.py


# 6. Data and Code Availability
The datasets and computational pipelines are deposited under open-access protocols to support scientific transparency and verification:
Zenodo Archive DOI: https://doi.org/10.5281/zenodo.22999479
License: All code is distributed under the MIT License. Primary survey response records are licensed under CC-BY 4.0 International.


# 7. Citation & Academic Attribution
If you utilize this dataset, methodological design, or econometric code in your research, please cite the work as follows:
Divyam Kumar. (2026). A Study On Adoption Of Online Vehicle Insurance In Bengaluru: Empirical dataset and replication code (Version 1.0). Zenodo. (https://doi.org/10.5281/zenodo.22999479)


# 8. Contact & Research Inquiries
For academic inquiries, methodological clarifications, or collaboration:
Researcher: Divyam Kumar
Email: divyam0718@gmail.com
