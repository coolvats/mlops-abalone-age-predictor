from dataclasses import dataclass
from typing import Union

@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str

@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str

@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float
    
@dataclass
class RegressionMetricArtifact:
    r2_score: float
    mse: float
    
@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    # can be ClassificationMetricArtifact or RegressionMetricArtifact depending on problem
    train_metric_artifact: Union[ClassificationMetricArtifact, RegressionMetricArtifact]
    test_metric_artifact: Union[ClassificationMetricArtifact, RegressionMetricArtifact]
