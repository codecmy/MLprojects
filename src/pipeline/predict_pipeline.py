import pickle
import sys
from pathlib import Path

import pandas as pd

from src.exception import CustomException
from src.logger import logging


class PredictPipeline:
    def predict(self, features):
        try:
            artifact_dir = Path(__file__).resolve().parents[2] / "artifact"
            with (artifact_dir / "model.pkl").open("rb") as model_file:
                model = pickle.load(model_file)
            with (artifact_dir / "preprocessor.pkl").open("rb") as preprocessor_file:
                preprocessor = pickle.load(preprocessor_file)

            data_scaled = preprocessor.transform(features)
            pred = model.predict(data_scaled)
            return pred
        except Exception as e:
            logging.info("Exception occurred in prediction")
            raise CustomException(e, sys)


class CustomData:
    def __init__(
        self,
        gender: str,
        race_ethnicity: str,
        parental_level_of_education: str,
        lunch: str,
        test_preparation_course: str,
        reading_score: int,
        writing_score: int,
    ):
        self.gender = gender
        self.race_ethnicity = race_ethnicity
        self.parental_level_of_education = parental_level_of_education
        self.lunch = lunch
        self.test_preparation_course = test_preparation_course
        self.reading_score = reading_score
        self.writing_score = writing_score

    def get_data_as_dataframe(self):
        try:
            custom_data_input_dict = {
                "gender": [self.gender],
                "race_ethnicity": [self.race_ethnicity],
                "parental_level_of_education": [self.parental_level_of_education],
                "lunch": [self.lunch],
                "test_preparation_course": [self.test_preparation_course],
                "reading_score": [self.reading_score],
                "writing_score": [self.writing_score]
            }
            df = pd.DataFrame(custom_data_input_dict)
            logging.info("Dataframe Gathered")
            return df
        except Exception as e:
            logging.info("Exception occurred while creating prediction input")
            raise CustomException(e, sys)