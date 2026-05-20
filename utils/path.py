from pathlib import Path
'''
Path(__file__).resolve() : create a correct path object
.parent : go one folder up
.parent : go another folder up 

'''

BASE_DIR = Path(__file__).resolve().parent.parent

RAWDATA_DB = BASE_DIR/"rawData"/"rawData.db"

JOBS_DB = BASE_DIR/"jobs.db"
TEST_DB = BASE_DIR/"transform"/"test.db"


