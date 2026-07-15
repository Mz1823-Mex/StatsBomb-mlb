# Feature Engineering Guide

## Overview

This document describes all sabermetric features calculated by the MLB Data Pipeline.

## Feature Categories

### 1. Batting Features

#### Basic Offensive Statistics

**AVG (Batting Average)**
- Formula: `hits / at_bats`
- Range: 0.0 - 1.0
- Description: Percentage of at-bats resulting in hits
- Interpretation: .300+ is considered excellent

**OBP (On-Base Percentage)**
- Formula: `(hits + walks + hit_by_pitch) / (at_bats + walks + hit_by_pitch + sacrifice_flies)`
- Range: 0.0 - 1.0
- Description: Percentage of plate appearances resulting in reaching base
- Interpretation: .350+ is considered excellent

**SLG (Slugging Percentage)**
- Formula: `(singles + 2×doubles + 3×triples + 4×home_runs) / at_bats`
- Range: 0.0 - 4.0
- Description: Total bases per at-bat
- Interpretation: .500+ is considered excellent

**OPS (On-base Plus Slugging)**
- Formula: `OBP + SLG`
- Range: 0.0 - 5.0
- Description: Combined offensive production metric
- Interpretation: .800+ is considered excellent (all-star level)

#### Advanced Batting Metrics

**ISO (Isolated Power)**
- Formula: `SLG - AVG`
- Range: 0.0 - 2.0
- Description: Extra-base hit rate; measures raw power
- Interpretation: .200+ indicates strong power

**BABIP (Batting Average on Balls In Play)**
- Formula: `(hits - home_runs) / (at_bats - strikeouts - home_runs + sacrifice_flies)`
- Range: 0.0 - 1.0
- Description: Batting average excluding home runs and strikeouts
- Interpretation: .300 is league average; indicates hit luck

**wOBA (Weighted On-Base Average)**
- Formula: `(0.69×walks + 0.72×HBP + 0.89×singles + 1.24×doubles + 1.56×triples + 1.95×HR) / PA`
- Range: 0.0 - 2.0
- Description: Advanced metric weighting each outcome by run value
- Interpretation: .330 is league average; best for comparing skill
- Weights based on 2026 season run values

#### Rate Statistics

**K% (Strikeout Rate)**
- Formula: `strikeouts / plate_appearances`
- Range: 0.0 - 1.0
- Description: Percentage of PAs ending in strikeout
- Interpretation: <15% is excellent; >25% indicates concern

**BB% (Walk Rate)**
- Formula: `walks / plate_appearances`
- Range: 0.0 - 0.3
- Description: Percentage of PAs resulting in walks
- Interpretation: 8%+ is strong selectivity

**Contact Rate**
- Formula: `(plate_appearances - strikeouts) / plate_appearances`
- Range: 0.0 - 1.0
- Description: Percentage of pitches put in play
- Interpretation: 75%+ is considered good

---

### 2. Pitching Features

#### Basic Pitching Statistics

**ERA (Earned Run Average)**
- Formula: `(earned_runs × 9) / innings_pitched`
- Range: 0.0 - 9.0+
- Description: Average earned runs allowed per 9 innings
- Interpretation: <3.00 is excellent; <4.00 is good; >5.00 is poor

**WHIP (Walks + Hits per Innings Pitched)**
- Formula: `(walks + hits_allowed) / innings_pitched`
- Range: 0.5 - 3.0+
- Description: Average baserunners allowed per inning
- Interpretation: <1.00 is excellent; >1.25 is concerning

**K9 (Strikeouts per 9 Innings)**
- Formula: `(strikeouts × 9) / innings_pitched`
- Range: 0.0 - 14.0
- Description: Average strikeouts per 9 innings pitched
- Interpretation: 9.0+ is elite; <6.0 is average

**BB9 (Walks per 9 Innings)**
- Formula: `(walks × 9) / innings_pitched`
- Range: 0.0 - 6.0
- Description: Average walks per 9 innings pitched
- Interpretation: <2.0 is excellent; >3.5 is concerning

#### Advanced Pitching Metrics

**FIP (Fielding Independent Pitching)**
- Formula: `((13×HR + 3×W - 2×K) / IP) + 3.10`
- Range: 0.0 - 9.0
- Description: ERA-like metric independent of defense
- Interpretation: Better than ERA for assessing true skill
- 2026 constant: 3.10 (league average)

**SIERA (Simplified ERA Approximation)**
- Formula: Complex - approximates ERA independent of defense
- Range: 0.0 - 9.0
- Description: Advanced measure of pitching skill
- Interpretation: More stable than ERA for predictive purposes

**LOB% (Left On Base Percentage)**
- Formula: `(H + W - ER) / (H + W - 1.4×HR)`
- Range: 0.0 - 1.0
- Description: Percentage of runners left on base (sequencing luck)
- Interpretation: 70%+ is strong; indicates ability to escape jams

---

### 3. Temporal Features

#### Rolling Averages
Computed for windows of 7, 15, and 30 games:
- Batting: AVG, OBP, SLG, OPS
- Pitching: ERA, WHIP, K9

Useful for capturing current form and momentum.

**Example:**
```
AVG_7game_rolling = average AVG over last 7 games
ERAS_15game_rolling = average ERA over last 15 games
```

#### Lag Features
Previous performance from N games ago (1, 3, 7):
- Batting: AVG, OBP, OPS, K%
- Pitching: ERA, WHIP

Capturesautocorrelation in performance.

#### Cumulative Statistics
Season-to-date totals:
- Batting: hits, HRs, RBIs, stolen bases
- Pitching: wins, losses, saves, innings pitched

---

### 4. Aggregate Features

#### Player-Level Aggregates
- Total games played
- Total at-bats
- Career average stats
- Season-to-date cumulative stats

#### Team-Level Aggregates
- Team average runs per game
- Team average runs allowed per game
- Team winning percentage
- Team strength of schedule

#### Position-Level Benchmarks
- Position average OPS
- Position average ERA (for pitchers)
- Position median salary

---

## Feature Calculation Pipeline

```
Raw Data
    ↓
[Clean & Validate]
    ↓
[Calculate Basic Features]
    ↓
[Derive Advanced Metrics]
    ↓
[Create Temporal Features]
    ↓
[Aggregate by Level]
    ↓
[Handle Missing Values]
    ↓
[Standardize for ML]
    ↓
ML-Ready Dataset
```

## Configuration

Feature parameters are defined in `config/features.yaml`:

```yaml
batting_features:
  AVG:
    formula: "hits / at_bats"
    min_value: 0.0
    max_value: 1.0
    required_fields: ["hits", "at_bats"]

rolling_windows: [7, 15, 30]
lag_periods: [1, 3, 7]
```

## Usage Example

```python
from src.features.build_features import FeatureBuilder
from src.utils.config_loader import load_config

# Load configuration
config = load_config("config/settings.yaml")

# Initialize feature builder
feature_builder = FeatureBuilder(config)

# Build features from raw data
df_raw = pd.read_csv("data/raw/player_stats.csv")
df_features = feature_builder.build(df_raw)

print(f"Generated {df_features.shape[1]} features")
print(df_features.columns)
```

## Data Quality

### Missing Value Handling
- Zero-fill: Home runs, RBIs for players without recent activity
- Forward-fill: Player names, team IDs for consistency
- Mean/median: For derived metrics

### Outlier Detection
- Method: Interquartile Range (IQR)
- Threshold: 3.0 × IQR
- Action: Cap extreme values

### Validation
- Check formula requirements met
- Validate result ranges
- Detect correlations
- Flag near-zero variance features

## Interpretation Guidelines

### Sabermetric Hierarchy (Best to Worst)

**For Batting:**
1. wOBA - Best overall offensive metric
2. OPS - Strong combined metric
3. OBP + SLG - Components of OPS
4. AVG - Limited value alone

**For Pitching:**
1. FIP - Best for skill assessment
2. SIERA - Good predictive value
3. ERA - Influenced by defense
4. WHIP - Useful supporting metric

### Context Matters
- Park factors affect hitting metrics
- Pitcher park context affects ERA
- Competition level varies
- Injury history important

## References

- Baseball Savant: https://baseballsavant.mlb.com
- Fangraphs Glossary: https://www.fangraphs.com/library
- Sabermetrics Resources: https://sabr.org
