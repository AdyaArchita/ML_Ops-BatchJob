# ML/MLOps Engineering Internship - Task 0

This repository contains a minimal MLOps-style batch job that computes trading signals from synthetic OHLCV data. It demonstrates reproducibility, observability, and deployment readiness.

## Deliverables
- `run.py`: Main processing script.
- `config.yaml`: Configuration file (seed, window, version).
- `data.csv`: Synthetic dataset with 10,000 rows.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Containerization setup.
- `metrics.json`: Machine-readable output from the last run.
- `run.log`: Detailed logs from the last run.

## Setup & Running Locally

### 1. Install Dependencies
Ensure you have Python 3.9+ installed. Run:
```bash
pip install -r requirements.txt
```

### 2. Execute Batch Job
Run the script using the required CLI arguments:
```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Running with Docker

### 1. Build the Image
```bash
docker build -t mlops-task .
```

### 2. Run the Container
```bash
docker run --rm mlops-task
```
This command will execute the job within the container, print the final metrics JSON to stdout, and maintain logs/metrics inside the environment.

## Example metrics.json Output
```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.499,
  "latency_ms": 127,
  "seed": 42,
  "status": "success"
}
```

## Design Decisions
- **Rolling Mean**: Used `min_periods=1` in `pandas.rolling()` to ensure that the initial rows (where the window is not yet full) still receive a signal based on available data.
- **Reproducibility**: `numpy.random.seed` is set globally from the config file to ensure deterministic output.
- **Observability**: Implemented structured logging to `run.log` and success/error reporting in `metrics.json`.