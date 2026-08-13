from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from queries.analysis import job_postings
from datetime import datetime

app = FastAPI()

# Allow React app (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/job-postings')
def get_job_postings(year: int = datetime.now().year):
    data = job_postings(year)
    return data.to_dict(orient='records')










    
    


