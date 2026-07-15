# System Architecture

## Overview

The MLB Data Pipeline follows a modular, layered architecture designed for maintainability, scalability, and testing.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources                              │
│  MLB Stats API  │  Baseball Reference  │  Fangraphs         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              API & Scraping Layer                            │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│    │ MLBClient    │  │ BBRefScraper │  │FangraphsScraper│   │
│    └────┬─────────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│              ETL (Extract, Transform, Load)                  │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│    │ Extract  │→ │  Clean   │→ │Transform │               │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│         └─────────────┼─────────────┘                       │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│              Data Storage Layer                               │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│    │  Raw Data  │  │ Interim Data │  │Processed   │        │
│    │  (CSV)     │  │ (Parquet)   │  │ Data       │        │
│    └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│          Feature Engineering Layer                            │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│    │Sabermetrics  │  │Rolling/Lag   │  │ Aggregations │     │
│    │ Calculations │  │ Features     │  │              │     │
│    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│           └──────────────┬──────────────────┘              │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│          Evaluation & Validation Layer                         │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│    │Data Quality  │  │Schema Check  │  │Range Check   │     │
│    │              │  │              │  │              │     │
│    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│           └──────────────┬──────────────────┘              │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│              ML Pipeline Layer                                │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│    │Preprocessing │  │Model Training│  │Hyperparameter│     │
│    │              │  │              │  │ Tuning       │     │
│    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│           └──────────────┬──────────────────┘              │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│              Evaluation & Output Layer                         │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│    │Model Metrics │  │ Predictions  │  │Artifacts     │     │
│    │              │  │              │  │              │     │
│    └──────────────┘  └──────────────┘  └──────────────┘     │
└───���─────────────────────────────────────────────────────────────┘
```

## Module Structure

### src/api/
**Purpose**: Interface with external data sources

- `mlb_client.py`: HTTP client for MLB Stats API
  - Handles rate limiting and retries
  - Manages session pooling
  - Provides typed method interfaces

**Dependencies**: requests, urllib3

---

### src/etl/
**Purpose**: Extract, clean, and transform data

- `extract_mlb.py`: Fetch data from MLB API
  - Player statistics extraction
  - Team data retrieval
  - Batch processing with retry logic

- `clean_dataset.py`: Data cleaning and validation
  - Remove duplicates
  - Handle missing values
  - Type conversion
  - Outlier detection

- `transform.py`: Data transformation
  - Column standardization
  - Data merging
  - Schema alignment

**Dependencies**: pandas, numpy

---

### src/features/
**Purpose**: Feature engineering and sabermetric calculations

- `sabermetrics.py`: Sabermetric formula implementations
  - Batting metrics (AVG, OBP, SLG, OPS, wOBA, etc.)
  - Pitching metrics (ERA, WHIP, K9, FIP, etc.)
  - Vectorized calculations for performance

- `build_features.py`: Feature engineering pipeline
  - Orchestrate feature calculation
  - Handle feature interactions
  - Manage feature versioning

- `aggregations.py`: Aggregate features
  - Player-level aggregates
  - Team-level aggregates
  - Position-level benchmarks

**Dependencies**: pandas, numpy

---

### src/models/
**Purpose**: Machine learning model training and inference

- `preprocessing.py`: ML preprocessing
  - Feature scaling and normalization
  - Missing value imputation
  - Feature selection

- `train.py`: Model training pipeline
  - Data splitting (train/val/test)
  - Model training
  - Hyperparameter tuning
  - Cross-validation

- `baseline.py`: Baseline models
  - Simple linear regression
  - Tree-based baselines
  - Performance benchmarking

**Dependencies**: scikit-learn, joblib

---

### src/evaluation/
**Purpose**: Data validation and model evaluation

- `validate_dataset.py`: Data quality checks
  - Schema validation
  - Value range checks
  - Consistency validation

- `metrics.py`: ML evaluation metrics
  - Regression metrics (R², RMSE, MAE)
  - Classification metrics
  - Custom metrics

- `performance.py`: Model performance analysis
  - Feature importance
  - Prediction analysis
  - Error analysis

**Dependencies**: scikit-learn, pandas

---

### src/utils/
**Purpose**: Shared utilities and helpers

- `logger.py`: Logging infrastructure
  - JSON and standard formatters
  - File and console handlers
  - Rotating file handler

- `config_loader.py`: Configuration management
  - YAML file loading
  - Configuration validation
  - Settings access

- `validators.py`: Data validation utilities
  - Schema checking
  - Type validation
  - Range checking

- `constants.py`: Global constants
  - Directory paths
  - API endpoints
  - Default parameters

**Dependencies**: pyyaml, pydantic

---

### src/scraping/
**Purpose**: Web scraping for fallback data sources

- `scraper.py`: Scraper implementations
  - Baseball Reference scraper
  - Fangraphs scraper
  - HTML parsing and data extraction

**Dependencies**: requests, beautifulsoup4

---

## Data Flow

### 1. Extraction Phase
```
MLB API → MLBClient → Raw CSV
```

### 2. Cleaning Phase
```
Raw CSV → DataCleaner → Cleaned Parquet → validation/
```

### 3. Feature Engineering Phase
```
Cleaned Data → Sabermetrics → Features → Aggregations → Processed Parquet
```

### 4. ML Pipeline Phase
```
Processed Data → Preprocessing → Train/Val/Test Split → Model Training → Evaluation
```

### 5. Output Phase
```
Metrics → outputs/metrics/
Models → outputs/models/
Artifacts → outputs/artifacts/
```

## Design Principles

### 1. Modularity
- Each module has single responsibility
- Clear interfaces between modules
- Minimal coupling
- Maximum cohesion

### 2. Testability
- Pure functions where possible
- Dependency injection
- Fixture-based test data
- Isolated unit tests

### 3. Maintainability
- Type hints throughout
- Comprehensive docstrings
- Clear naming conventions
- Consistent code style (Black)

### 4. Scalability
- Parallel processing support
- Batch processing capabilities
- Efficient data structures (Parquet)
- Vectorized operations

### 5. Reproducibility
- Version-controlled configurations
- Fixed random seeds
- Explicit data transformations
- Artifact versioning

## Configuration Hierarchy

```
config/
├── settings.yaml         # Main configuration
├── features.yaml         # Feature definitions
└── data_sources.yaml     # Data source configuration
```

Configurations are loaded in this order:
1. Load defaults from code (src/utils/constants.py)
2. Override with config files
3. Override with environment variables
4. Override with command-line arguments

## Error Handling Strategy

### API Errors
- Automatic retry with exponential backoff
- Fallback to alternative data sources
- Graceful degradation

### Data Validation Errors
- Log detailed error information
- Save validation reports
- Halt pipeline or skip problematic data

### Model Training Errors
- Check data splits for leakage
- Verify feature distributions
- Log model convergence issues

## Deployment Considerations

### GitHub Actions Workflows
- `fetch.yml`: Scheduled daily data extraction
- `train.yml`: On-demand model training

### Data Storage
- Raw data: CSV (archival)
- Interim data: Parquet (compressed)
- Models: Joblib (serialized)
- Metrics: JSON (versioned)

### Monitoring
- Structured logging to files
- API call tracking
- Data quality metrics
- Model performance tracking

## Performance Optimization

### Data Processing
- Vectorized operations (NumPy)
- Lazy loading where possible
- Chunked batch processing
- Parallel workers for I/O

### Model Training
- Feature scaling for faster convergence
- Early stopping on validation plateau
- Cross-validation with parallel jobs
- Grid search optimization

### Storage
- Parquet compression
- Partitioned datasets
- Artifact caching
- Version management
