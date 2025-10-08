# Avalanche Data Prediction
[CAIC](https://avalanche.state.co.us/) forecast data driving danger level predictions.

## Background
This project's first iteration was created while I was part of the University of Denver's Master of Science in Data Science program, as part of the deep learning course. I had reached out to the CAIC for historical forecast data, including the summary text and corresponding danger levels per the three elevation tiers, 'below treeline', 'treeline', and 'above treeline'. After receiving the data in json, the data was cleaned and parsed, before being used with TensorFlow and multiple deep learning techniques within a single notebook. This new iteration uses a larger set of data, with pytorch, and as part of a full stack application.

## Structure
Here I will briefly outline the structure of the main subdirectories.

### /client
A react/typescript app initialized using [Vite](https://vite.dev/). Deployed using cloudlfare workers to [caic.uelski.dev](https://caic.uelski.dev/). A user can select one of the deep learning models trained on the forecast data, input a summary and see the predicted danger levels per elevation tier, as well as the associated scores from the prediction model. There is also the capability to pull the most recent of the forecast data to view as well as select a number of forecasts to view from the training data. <br>

FUTURE GOAL:<br>
Use the forecast data as part of a reinforcement learning cycle with an open source LLM that will show users a context-driven brief based on the forecast summary and avalanche conditions.

### /server
This is the FastAPI backend that serves the api endpoints used on the frontend. It includes code to pull the model artifacts from Google Cloud Storage, use predictors built in the /ml directory and serve predictions given an inputted forecast summary. Deployed on GCP Cloud Run.

### /ml
This is where the deep learning models are trained, tested and predictor classes are built for the different models. Artifacts are saved locally before being uploaded to GCS before a deployment. The model training uses pytorch and scikit-learn with the json data that was sent from the CAIC.
