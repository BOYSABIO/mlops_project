"""
data_loader.py

Modular data ingestion utility for CSV and Excel files.
- Loads configuration from config.yaml
- Loads secrets from .env (using python-dotenv)
- Supports robust error handling and logging (configured by main.py)
- Designed for production and as a teaching example for MLOps best practices
"""

import os
import logging
import pandas as pd
import yaml
from dotenv import load_dotenv
from typing import Optional


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load configuration settings from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file

    Returns:
        dict: Configuration dictionary

    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the YAML is invalid
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def load_env(env_path: str = ".env"):
    """
    Load environment variables from a .env file if present.

    Args:
        env_path (str): Path to the .env file
    """
    load_dotenv(dotenv_path=env_path, override=True)


def load_data(
    path: str,
    file_type: str = "csv",
    sheet_name: Optional[str] = None,
    delimiter: str = ",",
    header: int = 0,
    encoding: str = "utf-8"
) -> pd.DataFrame:
    """
    Load data from a CSV or Excel file with validation and logging.

    Args:
        path (str): Path to the data file
        file_type (str): Either "csv" or "excel"
        sheet_name (Optional[str]): Sheet name (for Excel files)
        delimiter (str): Delimiter for CSV files
        header (int): Row number for column headers
        encoding (str): File encoding

    Returns:
        pd.DataFrame: Loaded data

    Raises:
        FileNotFoundError: If the data file does not exist
        ValueError: For unsupported file types or missing parameters
        Exception: For other data loading errors
    """
    if not path:
        logging.error("No data path specified in configuration.")
        raise ValueError("No data path specified in configuration.")

    if not os.path.isfile(path):
        logging.error(f"Data file does not exist: {path}")
        raise FileNotFoundError(f"Data file not found: {path}")

    try:
        if file_type == "csv":
            df = pd.read_csv(path, delimiter=delimiter,
                             header=header, encoding=encoding)
        elif file_type == "excel":
            df = pd.read_excel(path, sheet_name=sheet_name,
                               header=header, engine="openpyxl")
            # Warn if user forgot to specify a sheet and got multiple sheets
            if isinstance(df, dict):
                raise ValueError(
                    "Multiple sheets detected in Excel file. Please specify"
                    " a single 'sheet_name' in the configuration."
                )
        else:
            logging.error(f"Unsupported file type: {file_type}")
            raise ValueError(f"Unsupported file type: {file_type}")

        logging.info(
            f"Loaded data from {path} ({file_type}), shape={df.shape}")
        return df

    except Exception as e:
        logging.exception(f"Failed to load data: {e}")
        raise


def get_data(config_path: str = "config.yaml", env_path: str = ".env") -> pd.DataFrame:
    """
    Main entry point for loading data in MLOps pipelines.

    This function:
    - Loads environment variables (.env) for secrets/config
    - Loads YAML configuration for data source settings
    - Loads and returns the data as a DataFrame

    Args:
        config_path (str): Path to configuration file
        env_path (str): Path to .env file

    Returns:
        pd.DataFrame: Loaded data for downstream processing

    Raises:
        Exception: Any error in the configuration or data loading process
    """
    load_env(env_path)
    config = load_config(config_path)
    data_cfg = config.get("data_source", {})
    path = data_cfg.get("path")
    if not path:
        logging.error("No data path specified in configuration.")
        raise ValueError("No data path specified in configuration.")

    df = load_data(
        path=path,
        file_type=data_cfg.get("type", "csv"),
        sheet_name=data_cfg.get("sheet_name"),
        delimiter=data_cfg.get("delimiter", ","),
        header=data_cfg.get("header", 0),
        encoding=data_cfg.get("encoding", "utf-8"),
    )
    return df


if __name__ == "__main__":
    # Minimal logging for standalone/manual use only (main.py handles
    # logging in production)
    logging.basicConfig(
        # filename="logs/data_loader.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    try:
        df = get_data()
        print(f"Data loaded successfully. Shape: {df.shape}")
    except Exception as e:
        print(f"Failed to load data: {e}")
