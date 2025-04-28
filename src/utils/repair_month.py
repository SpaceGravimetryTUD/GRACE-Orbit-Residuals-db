import pandas as pd

def repair_month(df_month: pd.DataFrame , 
                 df_next_month: pd.DataFrame, 
                 time_column="datetime", 
                 interval_seconds=5):
    """
    Repair missing timestamps in a month DataFrame by borrowing from the next month DataFrame.

    Args:
        df_month (pd.DataFrame): DataFrame with data for the target month.
        df_next_month (pd.DataFrame): DataFrame with data for the next month.
        time_column (str): Name of the timestamp column.
        interval_seconds (int): Expected time interval between readings.

    Returns:
        pd.DataFrame: Repaired DataFrame with no missing timestamps.
    """
    # Copy to avoid modifying originals
    df_month = df_month.copy()
    df_next_month = df_next_month.copy()

    # Ensure timestamps are datetime
    df_month[time_column] = pd.to_datetime(df_month[time_column])
    df_next_month[time_column] = pd.to_datetime(df_next_month[time_column])

    # Compute expected full time range
    start_time = df_month[time_column].min().floor('D')
    end_time = (start_time + pd.DateOffset(months=1)).floor('D')
    expected_times = pd.date_range(start=start_time, end=end_time - pd.Timedelta(seconds=interval_seconds), freq=f"{interval_seconds}S")

    # Find missing timestamps
    real_times = df_month[time_column]
    missing_times = expected_times.difference(real_times)

    if missing_times.empty:
        df_month['borrowed'] = False
        return df_month

    if len(df_next_month) < len(missing_times):
        raise ValueError("Not enough data in df_next_month to borrow for missing timestamps.")

    # Borrow rows
    borrowed_rows = df_next_month.iloc[:len(missing_times)].copy()
    borrowed_rows[time_column] = missing_times.values
    borrowed_rows['borrowed'] = True

    # Mark original rows
    df_month['borrowed'] = False

    # Combine and sort
    df_repaired = pd.concat([df_month, borrowed_rows], ignore_index=True)
    df_repaired = df_repaired.sort_values(time_column).reset_index(drop=True)

    return df_repaired
