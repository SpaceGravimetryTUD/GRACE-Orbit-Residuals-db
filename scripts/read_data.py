import pandas as pd

# Shared list of fields
SATELLITE_FIELDS = [
    "datetime, ""timestamp",
    "latitude_A", "longitude_A", "altitude_A",
    "latitude_B", "longitude_B", "altitude_B"
]

def read_pkl(filepath: str) -> None: 
    df = pd.read_pickle(filepath).reset_index()
    return df

data = read_pkl("data/flat-data-test.pkl")

# Main should print the dataframe if the script is run directly
if __name__ == "__main__":
    print(data)