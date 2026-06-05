# DIEF-MO

**AI-Ready Multi-Omics Data Integration & Encoding Framework**

## Overview

Multi-omics data integration is essential for analyzing complex biological
systems and for Artificial Intelligence (AI) applications. However, challenges
such as heterogeneity, lack of standardization, and missing traceability
compromise the quality and reproducibility of analyses.

**DIEF-MO** addresses these problems through a structured framework for
**standardization, encoding, and data lineage**, preparing data for integration
and use in machine learning models.

## Objective

Provide a standardized encoding framework for multi-omics data that:

- Preserves full data traceability (*data lineage*)
- Structures experiments and samples consistently
- Enables integration across different areas and data types
- Prepares data for use in AI models

## Identifier format

Each assay receives a unique standardized identifier composed of subcodes:

```
<EXPERIMENT>_<AREA>_<MATRIX>_<SEQ>
```

Example: `E001_PRO_M001_001`

| Part         | Meaning                                          |
|--------------|--------------------------------------------------|
| `E001`       | Experiment code                                  |
| `PRO`        | Responsible area                                 |
| `M001`       | Matrix / sample code                             |
| `001`        | Sequential identifier (auto-incremented)         |

The sequence is generated automatically per `experiment + area + matrix`
combination, ensuring stable and traceable identifiers.

## Core entities

- **area_code** — area responsible for the assay
- **activity_code** — data origin (experimental or literature)
- **matrix_code** — analyzed matrix identifier
- **matrix_type** — matrix type
- **experiment_code** — experiment identifier

## Features

- Standardization of multi-omics data
- Full traceability (*data lineage*)
- Integration of experimental and literature data
- Output compatible with Machine Learning pipelines
- Automated information extraction via regex (`decode_id`)
- Scalable and adaptable to different biological domains

## Getting started

### Requirements

- Python 3.10+

### Installation

```bash
git clone https://github.com/deisefs04/DIEF-MO.git
cd DIEF-MO
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

The interface opens at `http://localhost:8501`.

### Run the tests

```bash
python -m pytest
```

## Usage

The application provides four pages:

1. **Registration** — register areas, matrices, and experiments (master data).
2. **Generate ID** — select a registered experiment, area, and matrix to
   generate and persist a new identifier.
3. **Batch import** — upload an Excel file (`.xlsx`) containing the columns
   `experiment_code`, `area_code`, `matrix_code` to generate identifiers in
   bulk and download the result.
4. **History** — view all generated identifiers.

### Using the library directly

```python
from dief_mo import generate_id, decode_id

generate_id("E001", "PRO", "M001", 1)   # 'E001_PRO_M001_001'
decode_id("E001_PRO_M001_001")          # {'experiment': 'E001', 'area': 'PRO',
                                        #  'matrix': 'M001', 'seq': 1}
```

## Project structure

```
DIEF-MO/
├── app.py                  # Streamlit interface
├── dief_mo/
│   ├── __init__.py
│   ├── encoder.py          # generate_id / decode_id (core)
│   └── db.py               # SQLite persistence (master data + assays)
├── tests/
│   └── test_encoder.py
├── requirements.txt
└── LICENSE
```

## Use case

The framework was applied in a pilot study with real multi-omics data from
microorganism matrices, integrating experimental and literature data into a
structured tabular format ready for ingestion in AI pipelines.

## Authors

- **Deise Ferreira de Souza** — Instituto SENAI de Inovação em Sistemas Embarcados (ISI-SE)
- **Jorge Kamassury** — Instituto SENAI de Inovação em Sistemas Embarcados (ISI-SE)

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.