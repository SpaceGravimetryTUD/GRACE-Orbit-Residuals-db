import pandas as pd
from src.machinery import getenv

def read_pkl(filepath: str) -> None:
    df = pd.read_pickle(filepath).reset_index() # nosec
    return df

# Main should print the dataframe if the script is run directly
if __name__ == "__main__":
    data = read_pkl(getenv('DATA_PATH'))
    print(data)
