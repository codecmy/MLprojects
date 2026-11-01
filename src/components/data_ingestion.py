from dataclasses import dataclass
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.logger import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from src.exception import CustomException
from data_transformation import DataTransformation

@dataclass
class DataIngestionConfig:
    train_data_path: str = str(PROJECT_ROOT / "artifact" / "train.csv")
    test_data_path: str = str(PROJECT_ROOT / "artifact" / "test.csv")
    raw_data_path: str = str(PROJECT_ROOT / "artifact" / "raw.csv")


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Entered Data Ingestion Component")
        try:
            data_path = PROJECT_ROOT / "notebook" / "data" / "stud.csv"
            df = pd.read_csv(data_path)
            logging.info("Read the dataset as dataframe")
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)
            logging.info("Train Test Split initiated")
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)
            logging.info("Ingestion of Data Completed")
            return (self.ingestion_config.train_data_path, self.ingestion_config.test_data_path)
        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    obj = DataIngestion()
    train_data, test_data = obj.initiate_data_ingestion()
    DataTransformation_obj = DataTransformation()
    DataTransformation_obj.initiate_data_transformation(train_data, test_data)