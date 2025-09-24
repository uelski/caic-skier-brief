import json
import pandas as pd
from bs4 import BeautifulSoup as bsoup
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level from scripts/ to ml/

IN = os.path.join(project_root, 'data', 'raw', 'all_new_forecasts.json')
MANUAL_FORECASTS = os.path.join(project_root, 'data', 'raw', 'manual_forecasts.json')
OUT = os.path.join(project_root, 'data', 'normalized', 'forecasts_normalized.json') 

def strip_html(html):
    text = str(html)
    return bsoup(text, "html.parser").get_text()

def remove_empty_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['Summary_clean'] != ""]
    df = df[(df['Below Treeline'] != "noRating") & (df['Treeline'] != "noRating") & (df['Above Treeline'] != "noRating")]
    return df

def create_manual_forecasts_df():
    with open(MANUAL_FORECASTS, 'r') as f:
        manual_forecasts = json.load(f)
    manual_forecast_df = pd.DataFrame(manual_forecasts)
    manual_forecast_df["datetime"] = pd.to_datetime(manual_forecast_df["date"])
    return manual_forecast_df

def normalize_data(data_path: str) -> pd.DataFrame:

    with open(data_path, 'r') as f:
        forecasts = json.load(f)

    # remove polygons and clean summary
    for forecast in forecasts:
        forecast.pop('polygons', None)
        
        summary_dict = json.loads(forecast['Summary'])
        forecast['Summary_en'] = summary_dict.get('en', None)
    
    #create dataframe
    forecast_df = pd.DataFrame(forecasts)
    print(forecast_df.shape)

    # strip html  
    forecast_df['Summary_clean'] = forecast_df['Summary_en'].apply(strip_html)

    # remove empty fields
    forecast_df = remove_empty_fields(forecast_df)

    # make datetime
    forecast_df["datetime"] = pd.to_datetime(forecast_df["date"])

    # choose fields
    df = forecast_df[["datetime", "Above Treeline", "Treeline", "Below Treeline", "Summary_clean", "date"]]

    # merge with manual forecasts
    manual_forecast_df = create_manual_forecasts_df()
    df = pd.concat([df, manual_forecast_df], ignore_index=True)

    return df
    

def main():
    data_path = IN
    data = normalize_data(data_path)
    # write to json file
    print(data.shape)
    data.to_json(OUT, orient='records')

if __name__ == '__main__':
    main()