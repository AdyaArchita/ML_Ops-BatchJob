import argparse
import json
import logging
import os
import sys
import time
import pandas as pd
import yaml
import numpy as np

def setup_logging(log_file):
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr)
        ]
    )

def load_config(config_path):
    """Loads and validates the YAML configuration."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    required_fields = ['seed', 'window', 'version']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field in config: {field}")
    
    return config

def write_metrics(output_path, metrics):
    """Writes metrics to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)

def run_job(args):
    start_time = time.time()
    version = "unknown"
    
    try:
        # 1. Setup Logging
        setup_logging(args.log_file)
        logging.info("Starting MLOps Batch Job")
        
        # 2. Load Config
        logging.info(f"Loading config from: {args.config}")
        config = load_config(args.config)
        version = config['version']
        seed = config['seed']
        window = config['window']
        logging.info(f"Config validated: seed={seed}, window={window}, version={version}")
        
        # 3. Set Seed
        np.random.seed(seed)
        logging.info(f"Deterministic seed set: {seed}")
        
        # 4. Load Data
        logging.info(f"Loading data from: {args.input}")
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input data file not found: {args.input}")
        
        df = pd.read_csv(args.input)
        if df.empty:
            raise ValueError("Input CSV is empty")
        
        if 'close' not in df.columns:
            raise ValueError("Required column 'close' missing from input data")
        
        rows_processed = len(df)
        logging.info(f"Successfully loaded {rows_processed} rows")
        
        # 5. Processing - Rolling Mean
        logging.info(f"Computing rolling mean with window size: {window}")
        # Strategy: Use min_periods=1 to compute mean for the first window-1 rows
        # This ensuring every row gets a signal calculation.
        df['rolling_mean'] = df['close'].rolling(window=window, min_periods=1).mean()
        
        # 6. Signal Generation
        logging.info("Generating binary signals")
        df['signal'] = (df['close'] > df['rolling_mean']).astype(int)
        
        signal_rate = float(df['signal'].mean())
        
        # 7. Finalize Metrics
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        
        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        
        logging.info(f"Job completed successfully. signal_rate={metrics['value']}, latency={latency_ms}ms")
        
        write_metrics(args.output, metrics)
        print(json.dumps(metrics, indent=2))
        sys.exit(0)
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Job failed: {error_msg}")
        
        error_metrics = {
            "version": version,
            "status": "error",
            "error_message": error_msg
        }
        
        # Ensure we at least try to write error metrics
        try:
            write_metrics(args.output, error_metrics)
        except:
            pass
            
        print(json.dumps(error_metrics, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MLOps Batch Job for Trading Signals")
    parser.add_argument("--input", required=True, help="Path to input data CSV")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument("--output", required=True, help="Path to output metrics JSON")
    parser.add_argument("--log-file", required=True, help="Path to log file")
    
    args = parser.parse_args()
    run_job(args)
