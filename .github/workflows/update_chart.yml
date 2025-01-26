import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go


def connect_to_database(db_path):
    """Connect to an SQLite database and validate its existence."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file {db_path} does not exist.")
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.DatabaseError:
        raise sqlite3.DatabaseError(f"The file {db_path} is not a valid SQLite database.")


def generate_candlestick_charts():
    # Database paths
    nifty50_db_path = "databases/nifty50_data_v1.db"
    predictions_db_path = "databases/predictions.db"

    # Connect to databases
    nifty50_conn = connect_to_database(nifty50_db_path)
    predictions_conn = connect_to_database(predictions_db_path)

    # Fetch table names from nifty50_data_v1.db (excluding sqlite_sequence)
    nifty50_tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('sqlite_sequence');",
        nifty50_conn
    )

    # Create output folder for charts
    output_folder = "charts"
    os.makedirs(output_folder, exist_ok=True)

    # Loop through each table in nifty50_data_v1.db
    for table_name in nifty50_tables['name']:
        # Read data from nifty50_data_v1.db
        nifty50_data = pd.read_sql(f"SELECT * FROM {table_name};", nifty50_conn)
        nifty50_data['Datetime'] = pd.to_datetime(nifty50_data['Datetime'])
        nifty50_data = nifty50_data.drop_duplicates(subset='Datetime', keep='last')

        # Read corresponding predictions table from predictions.db
        predictions_table = f"{table_name}_predictions"
        try:
            predictions_data = pd.read_sql(f"SELECT * FROM {predictions_table};", predictions_conn)
            predictions_data['Datetime'] = pd.to_datetime(predictions_data['Datetime'])
            predictions_data = predictions_data.drop_duplicates(subset='Datetime', keep='last')

            # Perform a left join
            merged_data = pd.merge(
                nifty50_data,
                predictions_data,
                on="Datetime",
                how="left"
            )
        except Exception as e:
            print(f"Skipping table {predictions_table} due to error: {e}")
            continue

        # Create candlestick chart
        fig = go.Figure()

        # Actual data
        fig.add_trace(go.Candlestick(
            x=merged_data['Datetime'],
            open=merged_data['Open'],
            high=merged_data['High'],
            low=merged_data['Low'],
            close=merged_data['Close'],
            name='Actual'
        ))

        # Predicted data
        if all(col in merged_data for col in ['Predicted_Open', 'Predicted_High', 'Predicted_Low', 'Predicted_Close']):
            fig.add_trace(go.Candlestick(
                x=merged_data['Datetime'],
                open=merged_data['Predicted_Open'],
                high=merged_data['Predicted_High'],
                low=merged_data['Predicted_Low'],
                close=merged_data['Predicted_Close'],
                name='Predicted',
                increasing_line_color='cyan',
                decreasing_line_color='magenta'
            ))

        # Update layout
        fig.update_layout(
            title=f"Candlestick Chart for {table_name}",
            xaxis_title="Datetime",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False
        )

        # Save chart as HTML
        chart_path = os.path.join(output_folder, f"{table_name}.html")
        fig.write_html(chart_path)

    # Close database connections
    nifty50_conn.close()
    predictions_conn.close()


if __name__ == "__main__":
    generate_candlestick_charts()
