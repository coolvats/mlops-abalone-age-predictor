import os
import sys

from abaloneage.exception.exception import PipelineException 
from abaloneage.logging.logger import logging

from abaloneage.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from abaloneage.entity.config_entity import ModelTrainerConfig

from abaloneage.utils.ml_utils.model.estimator import NetworkModel
from abaloneage.utils.main_utils.utils import save_object, load_object
from abaloneage.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import mlflow
from urllib.parse import urlparse

import dagshub
dagshub.auth.add_app_token(os.environ.get("DAGSHUB_USER_TOKEN"))
dagshub.init(repo_owner='edurekajuly24gcp', repo_name='final_mlops_pipeline', mlflow=True)

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise PipelineException(e,sys)
        
    def track_mlflow(self,best_model, metrics: dict):
        mlflow.set_registry_uri("https://dagshub.com/edurekajuly24gcp/final_mlops_pipeline.mlflow")
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        with mlflow.start_run():
            for k,v in metrics.items():
                mlflow.log_metric(k, v)
            mlflow.sklearn.log_model(best_model,"model")
            # Model registry does not work with file store
            if tracking_url_type_store != "file":

                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model.__class__.__name__)
            else:
                mlflow.sklearn.log_model(best_model, "model")


        
    def train_model(self,X_train,y_train,x_test,y_test):
        models = {
                "Random Forest": RandomForestRegressor(n_jobs=-1, random_state=42),
                "Decision Tree": DecisionTreeRegressor()}
        """
        comment
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
                }
        """
        params={
            "Decision Tree": {},
            "Random Forest":{
                'n_estimators': [16,32,64,128]
            }}
        """
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }
        """
        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=x_test,y_test=y_test,
                                          models=models,param=params)

        # choose best model by highest r2
        best_model_name = max(model_report, key=model_report.get)
        best_model = models[best_model_name]
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(x_test)

        train_metrics = {
            'r2': float(r2_score(y_train, y_train_pred)),
            'mse': float(mean_squared_error(y_train, y_train_pred)),
        }
        test_metrics = {
            'r2': float(r2_score(y_test, y_test_pred)),
            'mse': float(mean_squared_error(y_test, y_test_pred)),
        }

        # Track the experiments with mlflow
        self.track_mlflow(best_model, train_metrics)
        self.track_mlflow(best_model, test_metrics)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)
        # model pusher - also save raw model
        save_object("final_model/model.pkl", best_model)

        # create regression metric artifacts
        from abaloneage.entity.artifact_entity import RegressionMetricArtifact

        train_metric_artifact = RegressionMetricArtifact(r2_score=train_metrics['r2'], mse=train_metrics['mse'])
        test_metric_artifact = RegressionMetricArtifact(r2_score=test_metrics['r2'], mse=test_metrics['mse'])

        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=train_metric_artifact,
            test_metric_artifact=test_metric_artifact,
        )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact


        


       
    
    
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact

            
        except Exception as e:
            raise PipelineException(e,sys)
