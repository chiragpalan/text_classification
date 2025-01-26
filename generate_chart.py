import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go

# Paths to databases
nifty50_db_path = "databases/nifty50_data_v1.db"
predictions_db_path = "databases/predictions.db"
output_dir = "charts"

# Create output directory if not exists
os.makedirs(output_dir, exist_ok=True)

# Function to process and generate charts
def generate_candlestick_charts():
    # Connect to databases
    nifty50_conn = sqlite3.connect(nifty50_db_path)
    predictions_conn = sqlite3.connect(predictions_db_path)

    # Fetch table names from nifty50_data_v1.db excluding sqlite_sequence
    nifty50_tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';", nifty50_conn)
    nifty50_tables = nifty50_tables['name'].tolist()

    # Loop through each table and generate charts
    for table in nifty50_tables:
        try:
            # Load data from nifty50_data_v1.db
            nifty50_df = pd.read_sql(f"SELECT * FROM {table};", nifty50_conn)

            # Drop duplicates by Datetime, keeping the last entry
            nifty50_df['Datetime'] = pd.to_datetime(nifty50_df['Datetime'])
            nifty50_df = nifty50_df.drop_duplicates(subset='Datetime', keep='last')

            # Load corresponding data from predictions.db
            prediction_table = f"{table}_predictions"
            predictions_df = pd.read_sql(f"SELECT * FROM {prediction_table};", predictions_conn)

            # Drop duplicates by Datetime, keeping the last entry
            predictions_df['Datetime'] = pd.to_datetime(predictions_df['Datetime'])
            predictions_df = predictions_df.drop_duplicates(subset='Datetime', keep='last')

            # Perform left join on Datetime
            merged_df = pd.merge(nifty50_df, predictions_df, on='Datetime', how='left')

            # Ensure required columns exist
            required_columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Predicted_Open', 'Predicted_High', 'Predicted_Low', 'Predicted_Close']
            if not all(col in merged_df.columns for col in required_columns):
                print(f"Skipping {table}: Missing required columns.")
                continue

            # Create candlestick chart
            fig = go.Figure()

            # Actual Data
            fig.add_trace(
                go.Candlestick(
                    x=merged_df['Datetime'],
                    open=merged_df['Open'],
                    high=merged_df['High'],
                    low=merged_df['Low'],
                    close=merged_df['Close'],
                    name="Actual",
                )
            )

            # Predicted Data
            fig.add_trace(
                go.Candlestick(
                    x=merged_df['Datetime'],
                    open=merged_df['Predicted_Open'],
                    high=merged_df['Predicted_High'],
                    low=merged_df['Predicted_Low'],
                    close=merged_df['Predicted_Close'],
                    name="Predicted",
                    increasing_line_color="blue",
                    decreasing_line_color="orange",
                )
            )

            # Customize layout
            fig.update_layout(
                title=f"Candlestick Chart for {table}",
                xaxis_title="Datetime",
                yaxis_title="Price",
                template="plotly_dark",
            )

            # Save chart as HTML
            output_file = os.path.join(output_dir, f"{table}.html")
            fig.write_html(output_file)
            print(f"Chart for {table} saved to {output_file}")

        except Exception as e:
            print(f"Error processing table {table}: {e}")

    # Close connections
    nifty50_conn.close()
    predictions_conn.close()

# Run the function
if __name__ == "__main__":
    generate_candlestick_charts()
