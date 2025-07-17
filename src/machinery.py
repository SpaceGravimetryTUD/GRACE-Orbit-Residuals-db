from dotenv import load_dotenv
import os               # Library for system operations, like reading environment variables

# Load environment variables
load_dotenv()

def showenv():
  f = open('.env','r')
  env_list=list(filter(None,[ s.split('=')[0].split('#')[0] for s in f.read().split('\n')]))
  f.close()
  print('Loaded the following env vars from .env:')
  for f in env_list:
      print(f'{f} = {os.getenv(f)}')

def getenv(name: str) -> str:
  value = os.getenv(name)
  if not value:
      raise EnvironmentError("{name} not found in environment variables.")
  return value

class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def inspect_df(df):
  print(f'{bc.OKGREEN}Data size:{bc.ENDC} {df.shape[0]} rows, {df.shape[1]} columns, {df.size} entries')
  print(f'{bc.OKGREEN}Data head:{bc.ENDC}\n{df.head(n=5)}')
  print(f'{bc.OKGREEN}Data tail:{bc.ENDC}\n{df.tail(n=5)}')
  print(f'{bc.OKGREEN}Data sample:{bc.ENDC}\n{df.sample(n=5)}')
  print(f'{bc.OKGREEN}Data info:{bc.ENDC}')
  df.info()
  print(f'{bc.OKGREEN}Data missing:{bc.ENDC}\n{df.isnull().sum()}')
  print(f'{bc.OKGREEN}Duplicated entries:{bc.ENDC}\n{df.duplicated().sum()}')
