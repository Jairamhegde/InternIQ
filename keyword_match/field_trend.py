from keyword_match.dev_trend import similarity_check
from dbconnection.dbconnect import connect_database
from collections import defaultdict


def check_field_trend():
    field_freq = {
    "backend" :0,
    "frontend" : 0,
    "fullstack" : 0,
    "machine learning" : 0,
    "data science" : 0
    }

    conn = connect_database()
    cur = conn.cursor()
    query = '''
    select j.title, s.name
    from job_data j
    join job_skills js on j.job_id = js.job_id
    join skills s on js.skill_id = s.skill_id
    where j.posted_date :: date >= current_date - interval '100 day';
    '''
    cur.execute(query)
    rows = cur.fetchall()
    skill_map = defaultdict(list)
    for row in rows:
        title = row[0]
        skill = row[1]
        skill_map[title].append(skill)

    for key, value in skill_map.items():
        s = similarity_check(key, key, value)[0]
        if s in field_freq:
            field_freq[s] += 1
    sorted_freq = dict(sorted(field_freq.items(), key=lambda item: item[1], reverse=True))
    return sorted_freq

        
        


        
        








