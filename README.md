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

### Secondary entities (lineage)

Derived from the core entities to capture provenance:

- **batch** — a batch of work belonging to an experiment
- **sample** — a sample belonging to a batch and referencing a matrix

An identifier can be generated directly or from a registered sample, in which
case the experiment and matrix are derived from the sample's lineage
(`sample → batch → experiment`, `sample → matrix`).

## Features

- Standardization of multi-omics data
- Controlled vocabularies and code validation, so identifiers stay consistent
- Full data lineage: experiment → batch → sample → identifier, traceable per ID
- Integration of experimental and literature data
- Data-quality checks (completeness, orphan references) and a documented data dictionary
- AI-ready export: one row per identifier with full resolved metadata and lineage (CSV/Excel)
- ISA-Tab-aligned study/assay tables and a FAIR-style metadata record (downloadable bundle)
- In-place editing of registered entities and search/activity filtering of the dataset
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

The application provides eight pages:

1. **Overview** — summary counts of registered data and generated identifiers.
2. **Registration** — register core data (areas, matrices, experiments) and
   lineage entities (batches, samples), using controlled vocabularies and
   validated codes.
3. **Generate ID** — generate an identifier from a registered sample (with
   derived lineage) or directly from experiment + area + matrix.
4. **Batch import** — upload an Excel file (`.xlsx`) with the columns
   `experiment_code`, `area_code`, `matrix_code` to generate identifiers in bulk.
5. **Lineage** — trace any identifier back through sample, batch and experiment,
   and browse the full experiment tree.
6. **Data quality** — completeness checks, orphan-reference detection and the
   data dictionary for the exported dataset.
7. **FAIR / ISA-Tab** — ISA-aligned study/assay tables, a FAIR metadata record,
   and a downloadable bundle (investigation, study, assay, dataset, metadata).
8. **History** — browse all generated identifiers and export the AI-ready
   dataset (CSV/Excel).

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
│   ├── encoder.py          # generate_id / decode_id / validate_code (core)
│   ├── vocab.py            # controlled vocabularies (edit to match your catalog)
│   ├── datadict.py         # data dictionary for the exported dataset
│   ├── isa.py              # ISA-Tab-aligned & FAIR exports
│   └── db.py               # SQLite persistence (entities, lineage, quality)
├── tests/
│   ├── test_encoder.py
│   ├── test_db.py
│   └── test_isa.py
├── requirements.txt
└── LICENSE
```

## Use case

The framework was applied in a pilot study with real multi-omics data from
microorganism matrices, integrating experimental and literature data into a
structured tabular format ready for ingestion in AI pipelines.

## Standards & FAIR

DIEF-MO exports an **ISA-Tab-aligned** representation (investigation, study and
assay files) and a **FAIR-style metadata record** (JSON), available as a single
downloadable bundle from the *FAIR / ISA-Tab* page. The output follows ISA-Tab
conventions but is **not** validated against the ISA specification by a certified
tool; fully validated ISA output via the `isatools` library is on the roadmap.

## Roadmap

Planned extensions, aligned with the framework described above:

- Validated ISA-Tab/ISA-JSON output via the `isatools` library, with ontology
  term sources (OBI, NCBITaxon) and MIAME/MIAPE checklists.
- Optional hosted database for shared, persistent multi-user deployments.

## Authors

- **Deise Ferreira de Souza** — Instituto SENAI de Inovação em Sistemas Embarcados (ISI-SE)
- **Jorge Kamassury** — Instituto SENAI de Inovação em Sistemas Embarcados (ISI-SE)

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.