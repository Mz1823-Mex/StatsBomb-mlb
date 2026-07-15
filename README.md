# MLB Data Pipeline & ML Engineering 🏟️⚾

**Professional-grade data extraction, feature engineering, and predictive modeling for MLB 2026 season**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Data Pipeline](#data-pipeline)
- [Features & Sabermetrics](#features--sabermetrics)
- [Machine Learning](#machine-learning)
- [Development](#development)
- [Contributing](#contributing)

---

## 🎯 Overview

This repository implements a **production-ready ML pipeline** for MLB statistical analysis and predictive modeling. It combines:

- **Data Engineering**: Automated extraction from MLB Stats API with fallback sources
- **Feature Engineering**: Comprehensive sabermetric calculations (AVG, OBP, SLG, OPS, ERA, WHIP, FIP, etc.)
- **Data Science**: ML models for predicting player performance and game outcomes
- **DevOps**: GitHub Actions CI/CD, data validation, artifact versioning

### Key Features

✅ **Reproducible**: Version-controlled data, models, and metrics  
✅ **Scalable**: Modular architecture supporting parallel processing  
✅ **Maintainable**: Type hints, docstrings, logging, comprehensive tests  
✅ **Production-Ready**: Error handling, data validation, monitoring  
✅ **ML-Focused**: Proper train/val/test splits, no data leakage, baseline models

---

## 📁 Project Structure

```
StatsBomb-mlb/
├── .github/workflows/          # GitHub Actions CI/CD
│   ├── fetch.yml              # Scheduled data extraction
│   └── train.yml              # Manual model training
├── config/                     # Configuration files
│   ├── settings.yaml          # Main settings
│   ├── features.yaml          # Sabermetric definitions
│   └── data_sources.yaml      # API & data source config
├── data/                       # Data directories
│   ├── raw/                   # Unprocessed API responses
│   ├── interim/               # Cleaned intermediate data
│   ├── processed/             # Final ML-ready datasets
│   └── validation/            # Data quality reports
├── src/                        # Main source code
│   ├── api/                   # MLB Stats API client
│   ├── etl/                   # Extract, Transform, Load
│   ├── features/              # Feature engineering & sabermetrics
│   ├── models/                # ML model training & inference
│   ├── evaluation/            # Model evaluation & validation
│   ├── scraping/              # Web scraping (fallback)
│   └── utils/                 # Utilities (logging, config, validation)
├── tests/                      # Unit and integration tests
├── notebooks/                  # Jupyter notebooks (exploration)
├── outputs/                    # Model artifacts & metrics
├── docs/                       # Documentation
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

---

## 🏗️ Architecture

### Data Flow

```
MLB Stats API
     ↓
[Extract] → data/raw/*.csv
     ↓
[Clean] → data/interim/*.parquet
     ↓
[Features] → data/processed/*.parquet
     ↓
[Validate] → data/validation/
     ↓
[Train/Eval] → outputs/models/ + outputs/metrics/
```

### Module Organization

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **api** | HTTP client for MLB Stats API | `mlb_client.py` |
| **etl** | Data extraction and cleaning | `extract_mlb.py`, `clean_dataset.py`, `transform.py` |
| **features** | Sabermetric calculations | `sabermetrics.py`, `build_features.py`, `aggregations.py` |
| **models** | ML pipeline | `train.py`, `preprocessing.py`, `baseline.py` |
| **evaluation** | Validation & metrics | `validate_dataset.py`, `metrics.py`, `performance.py` |
| **utils** | Common utilities | `logger.py`, `config_loader.py`, `validators.py`, `constants.py` |

---

## 🔧 Setup & Installation

### Prerequisites

- Python 3.10+
- pip or conda
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/Mz1823-Mex/StatsBomb-mlb.git
cd StatsBomb-mlb
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -e .  # Install in development mode
```

4. **Verify installation**

```bash
python -c "import src; print('✅ Installation successful')"
```

---

## ⚙️ Configuration

### Main Configuration File: `config/settings.yaml`

```yaml
data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"
  formats:
    raw: "csv"
    processed: "parquet"

model:
  train_ratio: 0.60
  val_ratio: 0.20
  test_ratio: 0.20
  random_state: 42

api:
  mlb_stats_base_url: "https://statsapi.mlb.com/api/v1"
  timeout: 30
  max_retries: 3
```

### Feature Configuration: `config/features.yaml`

Defines all sabermetric calculations:
- Batting features: AVG, OBP, SLG, OPS, ISO, BABIP, wOBA
- Pitching features: ERA, WHIP, K9, BB9, FIP, SIERA
- Temporal features: Rolling means, lag features
- Aggregations: Player, team, and position-level metrics

### Data Sources: `config/data_sources.yaml`

API endpoints, validation rules, and fallback sources.

---

## 🚀 Quick Start

### 1. Extract Data from MLB Stats API

```python
from src.etl.extract_mlb import MLBDataExtractor
from src.utils.config_loader import load_config

config = load_config("config/settings.yaml")
extractor = MLBDataExtractor(config)

# Extract 2026 season data
df_batting = extractor.extract_player_stats(stat_type="hitting", season=2026)
df_pitching = extractor.extract_player_stats(stat_type="pitching", season=2026)

print(f"✅ Extracted {len(df_batting)} batting records")
print(f"✅ Extracted {len(df_pitching)} pitching records")
```

### 2. Clean & Validate Data

```python
from src.etl.clean_dataset import DataCleaner
from src.evaluation.validate_dataset import DataValidator

cleaner = DataCleaner(config)
df_clean = cleaner.clean(df_batting)

validator = DataValidator(config)
validator.validate(df_clean)
print("✅ Data validation passed")
```

### 3. Build Sabermetric Features

```python
from src.features.build_features import FeatureBuilder

feature_builder = FeatureBuilder(config)
df_features = feature_builder.build(df_clean)

print(f"✅ Generated {df_features.shape[1]} features")
print(df_features.head())
```

### 4. Train ML Model

```python
from src.models.train import ModelTrainer

trainer = ModelTrainer(config)
model, metrics = trainer.train(df_features)

print(f"✅ Model trained with R² = {metrics['r2']:.4f}")
```

---

## 📊 Data Pipeline

### Stages

1. **Extract** (`src/etl/extract_mlb.py`)
   - Fetch player stats from MLB Stats API
   - Handle rate limiting and retries
   - Save raw CSV files

2. **Clean** (`src/etl/clean_dataset.py`)
   - Remove duplicates
   - Handle missing values (explicit strategy per column)
   - Type conversion and validation
   - Outlier detection

3. **Transform** (`src/etl/transform.py`)
   - Standardize column names
   - Merge data from multiple sources
   - Create unified dataset structure

4. **Validate** (`src/evaluation/validate_dataset.py`)
   - Check schema compliance
   - Verify data ranges
   - Consistency checks
   - Generate quality reports

### Dataset Structure

| Column | Type | Description |
|--------|------|-------------|
| `player_id` | int | MLB Player ID |
| `player_name` | str | Player name |
| `season` | int | Season (e.g., 2026) |
| `date` | datetime | Game/record date |
| `team_id` | str | Team abbreviation |
| `position` | str | Player position |
| `plate_appearances` | int | PA |
| `at_bats` | int | AB |
| `hits` | int | H |
| `home_runs` | int | HR |
| ... | ... | ... |

---

## ⚾ Features & Sabermetrics

### Batting Metrics

| Feature | Formula | Range | Description |
|---------|---------|-------|-------------|
| **AVG** | H / AB | 0.0-1.0 | Batting Average |
| **OBP** | (H + W + HBP) / (AB + W + HBP + SF) | 0.0-1.0 | On-Base % |
| **SLG** | TB / AB | 0.0-4.0 | Slugging % |
| **OPS** | OBP + SLG | 0.0-5.0 | On-Base + Slugging |
| **wOBA** | Weighted OBP | 0.0-2.0 | Advanced metric |
| **ISO** | SLG - AVG | 0.0-2.0 | Extra-base hit rate |
| **BABIP** | (H - HR) / (AB - K - HR + SF) | 0.0-1.0 | Balls in play avg |

### Pitching Metrics

| Feature | Formula | Range | Description |
|---------|---------|-------|-------------|
| **ERA** | (ER × 9) / IP | 0.0-15.0 | Earned Run Avg |
| **WHIP** | (W + H) / IP | 0.5-3.0 | Walks + Hits / IP |
| **K9** | (K × 9) / IP | 0.0-14.0 | Strikeouts per 9 |
| **FIP** | ((13×HR + 3×W - 2×K) / IP) + 3.10 | 0.0-9.0 | Defense-Independent |
| **SIERA** | Advanced ERA estimator | 0.0-9.0 | Simplified ERA |
| **LOB%** | (H + W - ER) / (H + W - 1.4×HR) | 0.0-1.0 | Left On Base % |

### Temporal Features

- **Rolling Means**: 7, 15, 30-game averages
- **Lag Features**: 1, 3, 7-game previous performance
- **Cumulative Stats**: Season-to-date totals
- **Aggregations**: Player, team, position-level metrics

See `config/features.yaml` for complete definitions and formulas.

---

## 🤖 Machine Learning

### Pipeline

```
Raw Data
   ↓
[Train/Val/Test Split] (60/20/20)
   ↓
[Preprocessing] (standardization, missing values, outliers)
   ↓
[Feature Selection] (mutual information, variance)
   ↓
[Baseline Model] (linear regression, tree-based)
   ↓
[Hyperparameter Tuning]
   ↓
[Evaluation] (R², RMSE, MAE, cross-validation)
   ↓
[Save Artifacts] (model.pkl, metrics.json, predictions.csv)
```

### Model Training

```python
from src.models.train import ModelTrainer
from src.utils.config_loader import load_config

config = load_config("config/settings.yaml")
trainer = ModelTrainer(config)

# Train with automatic preprocessing and validation split
model, metrics, predictions = trainer.train(
    df_features,
    target_column="next_game_avg",
    model_type="random_forest"
)

# Evaluate
print(f"Train R²: {metrics['train_r2']:.4f}")
print(f"Val R²: {metrics['val_r2']:.4f}")
print(f"Test R²: {metrics['test_r2']:.4f}")
```

### Evaluation Metrics

- **Regression**: R², RMSE, MAE, MAPE
- **Classification** (if applicable): Accuracy, Precision, Recall, F1
- **Cross-validation**: K-fold scores with confidence intervals

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_features.py -v

# Run specific test
pytest tests/test_features.py::test_batting_avg -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/

# Check imports
isort src/ tests/
```

### Logging

The project uses structured logging with JSON and standard formats:

```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__, level="INFO", format_type="standard")
logger.info("Pipeline started")
logger.debug("Processing player 123")
logger.warning("Missing data in game 456")
logger.error("API timeout", exc_info=True)
```

Logs are saved to `logs/` directory with automatic rotation (10MB per file, 5 backups).

---

## 🔄 GitHub Actions

### Automated Workflows

#### `fetch.yml` - Scheduled Data Extraction
- Runs daily at 12:00 UTC
- Extracts latest 2026 season data
- Validates dataset
- Commits updated files to repo

```yaml
on:
  schedule:
    - cron: '0 12 * * *'
```

#### `train.yml` - Manual Model Training
- Triggered on demand via `workflow_dispatch`
- Trains models on latest data
- Uploads artifacts (models, metrics)
- Creates artifact versioning

```yaml
on:
  workflow_dispatch:
```

---

## 📚 Documentation

- **`docs/API.md`**: API client usage and endpoints
- **`docs/FEATURES.md`**: Detailed feature engineering guide
- **`docs/ARCHITECTURE.md`**: System design and data flow

---

## 🛠️ Troubleshooting

### Issue: "API rate limit exceeded"
**Solution**: The client automatically implements exponential backoff. Check `config/settings.yaml` for `api.rate_limit` settings.

### Issue: "Missing required columns in data"
**Solution**: Check `config/data_sources.yaml` for `required_fields`. Ensure API responses include all necessary fields.

### Issue: "Data validation failed"
**Solution**: Check `logs/` directory for detailed validation errors. Review `src/evaluation/validate_dataset.py`.

### Issue: "Model performance degraded"
**Solution**: 
1. Check for data leakage (ensure proper train/val/test splits)
2. Verify feature distributions
3. Review recent data changes in `data/interim/`

---

## 📝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run: `pytest tests/` and `black src/ tests/`
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Mz1823-Mex**  
Email: 11demayo@proton.me  
Repository: https://github.com/Mz1823-Mex/StatsBomb-mlb

---

## 🙏 Acknowledgments

- MLB Stats API for public baseball statistics
- Sabermetrics community for metric definitions
- scikit-learn, pandas, and Python data science ecosystem

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/Mz1823-Mex/StatsBomb-mlb/issues)
- Check [Discussions](https://github.com/Mz1823-Mex/StatsBomb-mlb/discussions)
- Review [Documentation](docs/)

---

**Last Updated**: 2026-07-15  
**Status**: 🚀 Production Ready
