# Phylogram Analysis for Principal Variable Identification

This project implements four methodologies (SM1, SM2, SM3, SM4) to analyze phylograms and extract a set of key variables (rVP) that explain the differences between high and low-performance scenarios.

## Prerequisites

- Python 3.8 or higher
- Git

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <URL_DE_TU_REPOSITORIO>
    cd analise_filogramas
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # Para Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Directory Structure

Ensure your input data is organized as follows inside the data/ folder::

```
data/
├── B2Coutput/
│   └── 1-tree.newick
├── W2Coutput/
│   └── 1-tree.newick
├── B4Coutput/
│   └── 1-tree.newick
├── W4Coutput/
│   └── 1-tree.newick
├── B8Coutput/
│   └── 1-tree.newick
├── W8Coutput/
│   └── 1-tree.newick
├── B16Coutput/
│   └── 1-tree.newick
├── W16Coutput/
│   └── 1-tree.newick
└── Main/
    └── output/
        └── 1-tree.newick
```

## Usage

To run the complete analysis, simply run the main script from the root of your project:

```bash
python main_analysis.py
```

The script will print the results of each stage (SM1-SM4) and the final set of rVP variables. The clades and other generated files will be saved in the data/SM1C1C2_output/ folder.