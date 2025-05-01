import os
import pandas as pd

# Load your environment
from dotenv import load_dotenv
load_dotenv()


def read_pkl(filepath: str) -> None: 
    df = pd.read_pickle(filepath).reset_index() # nosec
    return df

# Main should print the dataframe if the script is run directly
if __name__ == "__main__":
    data = read_pkl("data/flat-data-test.pkl")
    print(data)