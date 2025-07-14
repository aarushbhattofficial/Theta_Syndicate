```markdown
# Z‑Score Backtester

A one‑stop Jupyter notebook pipeline for backtesting z‑score–based momentum strategies on Indian equity indices.

## 📂 Project Structure

```

.
├── all.ipynb                # Main notebook to run end‑to‑end
├── data/                    # Historical OHLCV CSVs for various indices
├── auxiliary/               # Precomputed signals & weights
│   ├── backtester\_weights.csv
│   └── trading\_signals.csv
├── split\_ohlcv\_data/        # Per‑symbol CSVs for Open/High/Low/Close/Volume
│   ├── all\_open.csv
│   ├── all\_close.csv
│   └── …
├── z\_scores.csv             # Raw z‑scores for the selected universe
├── z\_scores\_mean.csv        # Rolling‑mean z‑scores
├── functions\_.py            # Helper functions & class definitions
├── results/                 # Output files & plots from the backtester
└── README.md                # This file

````

## 🚀 Usage

1. **Install dependencies**  
   ```bash
   pip install pandas numpy matplotlib
````

2. **Open and run**
   Launch `all.ipynb` in JupyterLab or Jupyter Notebook.
   It imports `functions_.py`, reads data from `data/`, `auxiliary/`, and `split_ohlcv_data/`, and writes outputs into `results/`.

## 📖 What’s Inside

* **`all.ipynb`**

  * Computes or loads z‑scores (`z_scores.csv`, `z_scores_mean.csv`)
  * Runs the backtest with your chosen parameters.
  * Generates daily trading weights and equity curves.
  * Generates performance tables and plots.