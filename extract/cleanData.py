
def clean_data(dataset):
    import pandas as pd
    df=pd.DataFrame(dataset)
    df['Salary']=df['Salary'].str.replace("₹","",regex=False)
    df['Salary']=df['Salary'].str.replace(",","",regex=False)
    sal=df['Salary'].str.split("-",expand=True)
    df['Min_sal']=sal[0]
    df['Max_sal']=sal[1]
    df.drop('Salary',axis=1,inplace=True)
    df['Min_sal']=pd.to_numeric(df['Min_sal'],errors='coerce')
    df['Max_sal']=pd.to_numeric(df['Max_sal'],errors='coerce')
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSIGHTS_DIR = BASE_DIR / "insights"
    INSIGHTS_DIR.mkdir(exist_ok=True)
    df.to_csv(INSIGHTS_DIR / "cleaned.csv", index=False, na_rep='null')

        