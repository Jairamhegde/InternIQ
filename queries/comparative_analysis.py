from sqlalchemy import false
from dbconnection.dbconnect import connect_database
import pandas as pd

def compare_role_trend(*roles):
    parameter = ",".join(['%s']*len(roles))
    db = connect_database('clean_data')
    print(parameter)
    query = f'''
    select to_char(posted_date::date,'month') as month,title,count(*) as postings
    from job_data
    where title in ({parameter})
    group by to_char(posted_date::date,'month'),title
    order by month desc;
    '''
    df = pd.read_sql_query(query,db,params = (*roles,))

    if not df.empty:
        df = (df.pivot_table(index='month',columns='title',values='postings',fill_value=0)
        .reset_index())
        df =df.sort_values(by=['month'],ascending=[False]).reset_index(drop=True)
    return df
