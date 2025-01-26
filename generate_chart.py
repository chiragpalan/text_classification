import sqlite3
import pandas as pd
import plotly.graph_objects as go
import os

# Define GitHub repository paths
username = "chiragpalan"
repo_name = "stocks_prediction_rnn_v2"
nifty50_db = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/nifty50_data_v1.db"
predictions_db = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/predictions/predictions.db"

# Output chart file
output_file = "docs/chart.html"

# Helper function to download databases locally
def download_db(db_url, local_path):
    import requests
    response = requests.get(db_url)
    with open(local_path, "wb") as f:
        f.write(response.content)

# Fetch data from nifty50_data_v1.db
def fetch_nifty_data():
    local_nifty_db = "nifty50_data_v1.db"
    download_db(nifty50_db, local_nifty_db)
    conn = sqlite3.connect(local_nifty_db)
    query = "SELECT Datetime, Open, High, Low, Close FROM table_name"
    nifty_data = pd.read_sql_query(query, conn)
    conn.close()
    os.remove(local_nifty_db)
    
    # Convert Datetime column to datetime format
    nifty_data["Datetime"] = pd.to_datetime(nifty_data["Datetime"])
    
    # Drop duplicate rows, keeping the last entry
    nifty_data = nifty_data.drop_duplicates(subset="Datetime", keep="last")
    
    return nifty_data

# Fetch data from predictions.db
def fetch_predictions_data():
    local_predictions_db = "predictions.db"
    download_db(predictions_db, local_predictions_db)
    conn = sqlite3.connect(local_predictions_db)
    query = """
        SELECT Datetime, Predicted_Open, Predicted_High, Predicted_Low, Predicted_Close
        FROM table_name
    """
    predictions_data = pd.read_sql_query(query, conn)
    conn.close()
    os.remove(local_predictions_db)
    
    # Convert Datetime column to datetime format
    predictions_data["Datetime"] = pd.to_datetime(predictions_data["Datetime"])
    
    # Drop duplicate rows, keeping the last entry
    predictions_data = predictions_data.drop_duplicates(subset="Datetime", keep="last")
    
    return predictions_data

# Merge data and create candlestick chart
def create_candlestick_chart():
    nifty_data = fetch_nifty_data()
    predictions_data = fetch_predictions_data()
    
    # Perform left join on Datetime
    merged_data = pd.merge(nifty_data, predictions_data, on="Datetime", how="left")
    
    # Plot candlestick chart
    fig = go.Figure()
    
    # Add actual candlesticks
    fig.add_trace(
        go.Candlestick(
            x=merged_data["Datetime"],
            open=merged_data["Open"],
            high=merged_data["High"],
            low=merged_data["Low"],
            close=merged_data["Close"],
            name="Actual"
        )
    )
    
    # Add predicted data as scatter points
    fig.add_trace(
        go.Scatter(
            x=merged_data["Datetime"],
            y=merged_data["Predicted_Close"],
            mode="lines+markers",
            name="Predicted Close",
            line=dict(color="blue", dash="dot"),
        )
    )
    
    fig.update_layout(
        title="Nifty 50 Candlestick Chart with Predictions",
        xaxis_title="Datetime",
        yaxis_title="Price",
        legend_title="Legend",
    )
    
    # Save chart as an HTML file
    fig.write_html(output_file)

# Main script
if __name__ == "__main__":
    create_candlestick_chart()
