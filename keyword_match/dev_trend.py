
from dbconnection.dbconnect import connect_database
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BACKEND_JOB_TITLES = {
    "backend developer",
    "back end developer",
    "backend engineer",
    "back end engineer",
    "backend software engineer",
    "backend software developer",
    "backend programmer",
    "backend application developer",
    "backend architect",
    "backend lead",
    "backend intern",
    "backend trainee",

    "python developer",
    "python backend developer",
    "django developer",
    "django backend developer",
    "flask developer",
    "fastapi developer",
    "fast api developer",

    "java developer",
    "java backend developer",
    "spring developer",
    "spring boot developer",
    "spring boot engineer",
    "j2ee developer",

    ".net developer",
    "asp.net developer",
    "asp.net core developer",
    "c# developer",

    "node.js developer",
    "nodejs developer",
    "node developer",
    "express developer",
    "express.js developer",

    "php developer",
    "laravel developer",
    "codeigniter developer",

    "golang developer",
    "go developer",

    "ruby developer",
    "ruby on rails developer",

    "scala developer",
    "kotlin backend developer",

    "api developer",
    "api engineer",
    "microservices developer",
    "microservices engineer",

    "software engineer",
    "software developer",
    "application developer",
    "server-side developer",

    "rest api developer",
    "graphql developer",

    "cloud backend developer",
    "aws backend developer",
    "azure backend developer",
    "gcp backend developer",

    "database developer",
    "sql developer",
    "postgresql developer",
    "mysql developer",

    "devops backend engineer"
}

FRONTEND_JOB_TITLES = {
    "frontend developer",
    "front end developer",
    "frontend engineer",
    "front end engineer",
    "frontend software engineer",
    "frontend software developer",
    "frontend programmer",
    "frontend architect",
    "frontend intern",
    "frontend trainee",

    "web developer",
    "web application developer",
    "ui developer",
    "ui engineer",
    "user interface developer",

    "javascript developer",
    "typescript developer",

    "react developer",
    "react.js developer",
    "reactjs developer",

    "angular developer",
    "angularjs developer",

    "vue developer",
    "vue.js developer",
    "vuejs developer",

    "next.js developer",
    "nextjs developer",

    "nuxt developer",

    "html developer",
    "css developer",

    "bootstrap developer",
    "tailwind css developer",

    "frontend web developer",
    "client-side developer",

    "ui frontend developer",
    "web ui developer",

    "javascript engineer",
    "react engineer",
    "angular engineer",
    "vue engineer",

    "software engineer",
    "software developer",

    "mobile web developer",

    "accessibility developer",
    "responsive web developer",

    "spa developer",
    "single page application developer"
}

BACKEND_KEYWORDS = {
    "backend",
    "back end",
    "python",
    "django",
    "flask",
    "fastapi",
    "fast api",
    "java",
    "spring",
    "spring boot",
    "node",
    "nodejs",
    "node.js",
    "express",
    "laravel",
    "php",
    ".net",
    "asp.net",
    "golang",
    "go developer",
    "ruby",
    "rails",
    "api",
    "microservice"
}

FRONTEND_KEYWORDS = {
    "frontend",
    "front end",
    "react",
    "reactjs",
    "react.js",
    "angular",
    "angularjs",
    "vue",
    "vuejs",
    "vue.js",
    "next",
    "nextjs",
    "next.js",
    "javascript",
    "typescript",
    "html",
    "css",
    "tailwind",
    "bootstrap",
    "ui developer",
    "web developer"
}

FULL_STACK_JOB_TITLES = {
    "full stack developer",
    "fullstack developer",
    "full-stack developer",

    "full stack engineer",
    "fullstack engineer",
    "full-stack engineer",

    "full stack software engineer",
    "full stack software developer",

    "full stack web developer",
    "full stack web engineer",

    "mern stack developer",
    "mern developer",

    "mean stack developer",
    "mean developer",

    "lamp stack developer",

    "java full stack developer",
    "java full stack engineer",

    "python full stack developer",
    "python full stack engineer",

    "dot net full stack developer",
    ".net full stack developer",
    "asp.net full stack developer",

    "php full stack developer",

    "react node developer",
    "react nodejs developer",

    "react full stack developer",

    "angular full stack developer",

    "django react developer",

    "software engineer full stack",

    "full stack intern",
    "full stack engineer intern",
    "full stack developer intern",
    "full stack trainee",

    "senior full stack developer",
    "junior full stack developer",
    "associate full stack developer",
    "lead full stack developer",
    "principal full stack engineer"
}

AI_ML_JOB_TITLES = {
    "ai engineer",
    "artificial intelligence engineer",
    "machine learning engineer",
    "ml engineer",
    "deep learning engineer",
    "computer vision engineer",
    "nlp engineer",
    "llm engineer",
    "generative ai engineer",
    "genai engineer",
    "ai developer",
    "machine learning developer",
    "ai software engineer",
    "ai research engineer",
    "research engineer ai",
    "research scientist ai",
    "applied ai engineer",
    "applied scientist",
    "ml researcher",
    "ai researcher",
    "prompt engineer",
    "ai intern",
    "machine learning intern",
    "ml intern",
    "computer vision intern",
    "nlp intern",
    "genai intern",
    "artificial intelligence intern"
}

AI_ML_KEYWORDS = {
    "ai",
    "artificial",
    "intelligence",
    "machine",
    "learning",
    "ml",
    "deep",
    "neural",
    "llm",
    "genai",
    "generative",
    "nlp",
    "vision",
    "cv",
    "transformer",
    "diffusion",
    "bert",
    "gpt",
    "prompt",
    "machine learning"
}

FULLSTACK_KEYWORDS = {
    # Core terms
    "fullstack",
    "full",
    "stack",
    
    # Popular stacks
    "mern",
    "mean",
    "lamp",
    "mevn",

    # Framework combinations
    "react",
    "angular",
    "vue",
    "nodejs",
    "express",
    "nextjs",
    "nestjs",

    # Common combinations
    "frontend",
    "backend",
}


def normalize_title(title):
    title = title.lower()
    title = re.sub(r"[^a-zA-Z0-9\s]"," ",title)
    title = re.sub(r"\s+"," ",title)
    return title

def get_job_skills(job_title):
    conn = connect_database("clean_data")
    cur = conn.cursor()
    query = '''
        SELECT s.name 
        FROM job_data j
        join job_skills js on j.job_id = js.job_id
        join skills s on js.skill_id = s.skill_id
        where j.title = %s
        '''
    cur.execute(query,(job_title,))
    rows = cur.fetchall()
    newset = [normalize_title(row[0]) for row in rows]
    return newset

def score_job_field(title,skills):
    title = normalize_title(title)
    backend_score = 0
    frontend_score = 0
    fullstack_score = 0
    aiml_score = 0

    if title in BACKEND_JOB_TITLES:
        backend_score += 10
    if title in FRONTEND_JOB_TITLES:
        frontend_score += 10
    if title in FULL_STACK_JOB_TITLES:
        fullstack_score += 10
    if title in AI_ML_JOB_TITLES:
        aiml_score += 10
    
    for skill in skills:
        if skill in BACKEND_KEYWORDS:
            backend_score += 1
        if skill in FRONTEND_KEYWORDS:
            frontend_score += 1
        if skill in AI_ML_KEYWORDS:
            aiml_score += 1
        if skill in FULLSTACK_KEYWORDS:
            fullstack_score += 1
    print(f"fullstack : {fullstack_score}\nbackend : {backend_score}\n Frontend : {frontend_score}\n aiml : {aiml_score}")
    
    if fullstack_score >= backend_score and fullstack_score >= frontend_score and fullstack_score >= aiml_score:
        return f"Fullstack{fullstack_score}"
    elif backend_score >= fullstack_score and backend_score >= frontend_score and backend_score >= aiml_score:
        return f"backend{backend_score}"
    elif frontend_score >= fullstack_score and frontend_score >= backend_score and frontend_score >= aiml_score:
        return f"Frontend{frontend_score}"
    else:
        return f"aiml{aiml_score}"

dictionaries = {
    "frontend" : """
                frontend frontend developer frontend engineer ui developer web developer javascript developer
                react developer reactjs developer angular developer vue developer nextjs developer html css developer
                typescript javascript html css sass bootstrap tailwind material ui responsive web design
                user interface ui ux client side browser dom ajax fetch axios redux context api state management
                single page application spa progressive web app pwa web components accessibility responsive layouts
                figma adobe xd pixel perfect cross browser compatibility frontend optimization performance optimization
                webpack vite npm yarn git testing jest cypress frontend application user experience animations
                develop responsive interfaces build reusable components implement user interface collaborate with designers
                """,
    "fullstack" : """
                full stack developer fullstack developer full stack engineer fullstack engineer full stack software engineer
                mern stack developer mean stack developer lamp stack developer mevn stack developer
                python full stack developer java full stack developer dotnet full stack developer php full stack developer
                frontend backend react nodejs express django flask fastapi spring boot angular vue nextjs
                html css javascript typescript sql mysql postgresql mongodb redis rest api graphql authentication
                docker kubernetes aws git ci cd software architecture end to end application development
                develop frontend and backend build complete web applications design database integrate apis
                deploy maintain scalable applications collaborate across frontend backend full lifecycle development
                """,
    "backend" :"""
                A Backend Developer is responsible for designing, developing, testing, deploying, and maintaining server-side applications that power web and mobile applications. The role involves building scalable backend services, designing REST APIs and GraphQL APIs, implementing business logic, integrating databases, optimizing application performance, ensuring security, and maintaining cloud-based applications.

                Typical responsibilities include developing RESTful APIs, designing microservices, implementing authentication and authorization, writing reusable and maintainable code, debugging production issues, optimizing SQL queries, integrating third-party services, managing databases, improving scalability, ensuring high availability, writing unit and integration tests, deploying applications to cloud platforms, and collaborating with frontend developers.

                Common job titles include Backend Developer, Backend Engineer, Backend Software Engineer, Python Developer, Java Developer, Spring Boot Developer, Django Developer, Flask Developer, FastAPI Developer, Node.js Developer, Express.js Developer, Golang Developer, PHP Developer, Laravel Developer, Ruby on Rails Developer, API Developer, and Software Engineer Backend.

                Common technologies include Python, Java, Spring Boot, Django, Flask, FastAPI, Node.js, Express.js, Golang, PHP, Laravel, Ruby on Rails, REST API, GraphQL, gRPC, SQL, PostgreSQL, MySQL, Oracle, MongoDB, Redis, Cassandra, Elasticsearch, RabbitMQ, Kafka, Docker, Kubernetes, AWS, Azure, GCP, Linux, Git, Nginx, Apache, CI/CD, JWT, OAuth2, Authentication, Authorization, Microservices, Distributed Systems, Object-Oriented Programming, Concurrency, Multithreading, Caching, Logging, Monitoring, Cloud Deployment, and Software Architecture.

                Backend developers are expected to understand server-side programming, API development, database management, software architecture, security best practices, cloud computing, scalability, performance optimization, debugging, testing, deployment, and the complete backend software development lifecycle.
                """,
    "machine learning" : """
                artificial intelligence ai engineer ai developer machine learning engineer ml engineer
                deep learning engineer computer vision engineer nlp engineer llm engineer generative ai engineer
                prompt engineer ai researcher research scientist applied scientist machine learning developer
                tensorflow pytorch keras scikit learn huggingface transformers langchain llamaindex openai
                large language models llm retrieval augmented generation rag embeddings vector database pinecone chromadb faiss
                computer vision image processing object detection segmentation ocr facial recognition
                natural language processing nlp text classification sentiment analysis summarization translation
                supervised learning unsupervised learning reinforcement learning neural networks cnn rnn lstm transformer bert gpt diffusion
                model training model evaluation hyperparameter tuning feature engineering inference deployment mlops
                python pandas numpy matplotlib seaborn jupyter notebook data preprocessing prediction classification regression clustering
                """,
    "data science" : """
                data scientist data science engineer data analyst business analyst analytics engineer business intelligence analyst
                research analyst quantitative analyst statistical analyst decision scientist
                python r sql excel power bi tableau pandas numpy scipy matplotlib seaborn plotly
                data cleaning exploratory data analysis eda feature engineering feature selection statistics probability hypothesis testing
                linear regression logistic regression decision tree random forest xgboost lightgbm clustering kmeans dbscan
                classification regression forecasting recommendation systems time series anomaly detection
                machine learning predictive analytics statistical modeling data visualization dashboards reporting
                jupyter notebook data wrangling data preprocessing insights business intelligence descriptive analytics
                inferential statistics correlation covariance sampling distributions experimentation a b testing
                """
    
    }

corpus = list(dictionaries.values())
labels = list(dictionaries.keys())

vectorizer = TfidfVectorizer(stop_words="english")
embeded_word = vectorizer.fit_transform(corpus)

def similarity_check(title,description,skills):
    text = f"{title} {description} {' '.join(skills)}"
    job_vector = vectorizer.transform([text])
    similarity = cosine_similarity(job_vector,embeded_word)[0]
    
    best_idx = similarity.argmax()
    return labels[best_idx] , round(similarity[best_idx],3)






    

