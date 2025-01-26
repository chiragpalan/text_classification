import pandas as pd
import plotly.graph_objects as go

def process_table(conn, table_name):
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.tz_localize(None)  # Convert to datetime without timezone
    df = df.drop_duplicates(subset=['Datetime'], keep='last')  # Drop duplicates
    return df

def left_join_dfs(df1, df2):
    return pd.merge(df1, df2, on='Datetime', how='left')

def create_candlestick_chart(df, title, filename):
    fig = go.Figure(data=[go.Candlestick(x=df['Datetime'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title=title, xaxis_title='Datetime', yaxis_title='Price')
    fig.write_html(f'docs/{filename}.html')

# Process all tables in nifty50_data_v1.db
dfs_nifty50 = {table: process_table(conn_nifty50, table) for table in tables_nifty50}

# Process all tables in predictions.db
dfs_pred = {table: process_table(conn_pred, table) for table in tables_pred}

# Generate charts for each table pair
for table in tables_nifty50:
    if table in dfs_pred:
        df_merged = left_join_dfs(dfs_nifty50[table], dfs_pred[table])
        create_candlestick_chart(df_merged, f'{table} Candlestick Chart', f'candlestick_chart_{table}')
