
# Abalone Age Prediction MLOps Pipeline

This project predicts the age of abalone (in rings) using a machine learning pipeline with full MLOps best practices. It features:
- Data ingestion from MongoDB
- Data validation, transformation, and model training (Random Forest, XGBoost, etc.)
- Model tracking with MLflow/DagsHub
- Batch and real-time prediction APIs with FastAPI
- Automated testing with pytest
- Data and model versioning with DVC

## Project Structure
```
final_mlops_pipeline/
├── Abalone_Data/abalone.csv         # Raw data (for reference)
├── abaloneage/                      # Main package (components, utils, etc.)
├── final_model/                     # Saved model and preprocessor
├── sample_input.csv                 # Example input for batch prediction
├── app.py                           # FastAPI app
├── main.py                          # Pipeline runner
├── push_data.py                     # Script to push CSV data to MongoDB
├── requirements.txt                 # Python dependencies
├── test_predict.py                  # Pytest for model accuracy
└── ...
```

## Setup Instructions
1. **Clone the repo and install dependencies:**
	```powershell
	pip install -r requirements.txt
	```
2. **Set up MongoDB:**
	- Start your MongoDB instance (local or cloud).
	- Set the environment variable `MONGO_DB_URL` to your MongoDB connection string.
	- Push data to MongoDB:
	  ```powershell
	  python push_data.py
	  ```
3. **Configure DagsHub/MLflow:**
	- Set `DAGSHUB_USER_TOKEN` and (optionally) `DAGSHUB_USERNAME` as environment variables.
	- The pipeline will log experiments to your DagsHub MLflow repo.

## Running the Pipeline
```powershell
python main.py
```
Artifacts (model, preprocessor, metrics) will be saved in `final_model/` and `artifacts/`.

## Serving the Model with FastAPI
1. Start the API:
	```powershell
	uvicorn app:app --reload
	```
2. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.
3. Use `/predict` for batch CSV prediction and `/predict_single` for real-time JSON prediction.

## Testing
Run the test to check model accuracy:
```powershell
python -m pytest -v -s test_predict.py
```

## DVC Data Versioning (with MongoDB)
1. **Initialize DVC:**
	```powershell
	dvc init
	git add .dvc .gitignore
	git commit -m "Initialize DVC"
	```
2. **Add a data import stage from MongoDB:**
	- Create a script (e.g., `mongo_export.py`) that exports your MongoDB collection to a CSV (or use `push_data.py` in reverse).
	- Example DVC stage:
	  ```powershell
	dvc stage add -n get_data_from_mongo \
		-d mongo_export.py \
		-o Abalone_Data/abalone.csv \
		python mongo_export.py
	  ```
	- This will let you version the exported data with DVC.
3. **Track model artifacts:**
	```powershell
	dvc add final_model/model.pkl final_model/preprocessor.pkl
	git add final_model/model.pkl.dvc final_model/preprocessor.pkl.dvc
	git commit -m "Track model artifacts with DVC"
	```
4. **Push data and models to remote storage:**
	```powershell
	dvc remote add -d myremote <remote-storage-url>
	dvc push
	```

## Notes
- Data is ingested from MongoDB, not from a static CSV. Use DVC to version the exported snapshot.
- Update `sample_input.csv` with real samples for testing.
- All environment variables can be set in a `.env` file for convenience.

## Contact
For questions or contributions, open an issue or pull request.


Setup github secrets:
AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_REGION = us-east-1

AWS_ECR_LOGIN_URI = 
ECR_REPOSITORY_NAME = 


Docker Setup In EC2 commands to be Executed
#optinal

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker