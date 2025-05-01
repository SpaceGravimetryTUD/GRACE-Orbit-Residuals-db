import pytest
import pandas as pd

from src.utils.repair_month import repair_month  # adjust this import path

@pytest.fixture
def synthetic_dataframes_with_gap():
    """Creates synthetic month and next-month DataFrames with a 10-hour gap."""
    # Create March 1–2 with 5s intervals
    times_march = pd.date_range(start="2025-03-01", end="2025-04-01", freq="5s")  # Full March
    # Introduce 10h gap
    gap_start = pd.Timestamp("2025-03-01 10:00:00")
    gap_end = pd.Timestamp("2025-03-01 20:00:00")
    times_march = times_march[(times_march < gap_start) | (times_march > gap_end)]

    df_march = pd.DataFrame({
        "datetime": times_march,
        "value": range(len(times_march))
    })

    # Create full April 1–2 to borrow from
    times_april = pd.date_range(start="2025-04-01", end="2025-04-02", freq="5s")
    df_april = pd.DataFrame({
        "datetime": times_april,
        "value": range(len(times_april))
    })

    return df_march, df_april


def test_repair_month_from_dataframes(synthetic_dataframes_with_gap):
    df_march, df_april = synthetic_dataframes_with_gap

    repaired_df = repair_month(
        df_month=df_march,
        df_next_month=df_april,
        time_column="datetime",
        interval_seconds=5
    )

    # 1. Verify no missing timestamps
    repaired_times = pd.to_datetime(repaired_df["datetime"])
    expected_times = pd.date_range(start="2025-03-01", end="2025-04-01", freq="5s")  # <-- corrected here
    assert set(repaired_times) == set(expected_times), "Timestamps mismatch after repair."

    # 2. Check number of borrowed rows
    borrowed_rows = repaired_df[repaired_df['borrowed']]

    gap_seconds = (pd.Timestamp("2025-03-10 20:00:00") - pd.Timestamp("2025-03-10 10:00:00")).total_seconds()
    expected_borrowed = int(gap_seconds / 5)

    assert len
