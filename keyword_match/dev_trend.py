
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
    "frontend": """
                A Frontend Developer is responsible for designing, building, and maintaining the
                user-facing part of web applications, translating designs into responsive, accessible,
                and performant interfaces that run in the browser. The role involves building reusable
                UI components, managing client-side state, consuming REST and GraphQL APIs, and
                ensuring a consistent experience across browsers and devices.

                Typical responsibilities include implementing responsive layouts, building and
                maintaining component libraries, managing application state, optimizing page load and
                rendering performance, ensuring cross-browser compatibility, writing unit and UI tests,
                collaborating with designers on pixel-accurate implementation, and improving
                accessibility for users relying on assistive technology.

                Common job titles include Frontend Developer, Frontend Engineer, UI Developer, Web
                Developer, React Developer, Angular Developer, Vue Developer, Next.js Developer, and
                JavaScript Developer.

                Common technologies include HTML, CSS, JavaScript, TypeScript, React, Angular, Vue,
                Next.js, Redux, Context API, Sass, Tailwind CSS, Bootstrap, Material UI, Webpack, Vite,
                npm, Figma, Jest, Cypress, DOM APIs, Fetch, Axios, and responsive/accessible web design
                principles.
                """,

    "fullstack": """
                A Full Stack Developer is responsible for designing, building, and maintaining both the
                client-facing and server-side parts of a web application, working across the entire
                stack from database to user interface. The role involves designing schemas, building
                APIs, implementing business logic, and building the interfaces that consume those APIs.

                Typical responsibilities include developing and consuming REST or GraphQL APIs,
                designing and integrating databases, implementing authentication end to end, building
                responsive user interfaces, writing tests across both frontend and backend layers,
                deploying and maintaining applications on cloud infrastructure, and owning a feature
                from database schema through to the deployed UI.

                Common job titles include Full Stack Developer, Full Stack Engineer, MERN Stack
                Developer, MEAN Stack Developer, Python Full Stack Developer, Java Full Stack Developer,
                and .NET Full Stack Developer.

                Common technologies include React, Angular, Vue, Next.js, Node.js, Express, Django,
                Flask, FastAPI, Spring Boot, HTML, CSS, JavaScript, TypeScript, SQL, MySQL, PostgreSQL,
                MongoDB, REST API, GraphQL, Docker, Kubernetes, AWS, Git, and CI/CD pipelines spanning
                the whole application lifecycle.
                """,

    "backend": """
                A Backend Developer is responsible for designing, developing, testing, deploying, and
                maintaining server-side applications that power web and mobile applications. The role
                involves building scalable backend services, designing REST APIs and GraphQL APIs,
                implementing business logic, integrating databases, optimizing application performance,
                ensuring security, and maintaining cloud-based applications.

                Typical responsibilities include developing RESTful APIs, designing microservices,
                implementing authentication and authorization, writing reusable and maintainable code,
                debugging production issues, optimizing SQL queries, integrating third-party services,
                managing databases, improving scalability, ensuring high availability, writing unit and
                integration tests, deploying applications to cloud platforms, and collaborating with
                frontend developers.

                Common job titles include Backend Developer, Backend Engineer, Backend Software
                Engineer, Python Developer, Java Developer, Spring Boot Developer, Django Developer,
                Flask Developer, FastAPI Developer, Node.js Developer, Express.js Developer, Golang
                Developer, PHP Developer, Laravel Developer, Ruby on Rails Developer, API Developer,
                and Software Engineer Backend.

                Common technologies include Python, Java, Spring Boot, Django, Flask, FastAPI, Node.js,
                Express.js, Golang, PHP, Laravel, Ruby on Rails, REST API, GraphQL, gRPC, SQL,
                PostgreSQL, MySQL, Oracle, MongoDB, Redis, Cassandra, Elasticsearch, RabbitMQ, Kafka,
                Docker, Kubernetes, AWS, Azure, GCP, Linux, Git, Nginx, Apache, CI/CD, JWT, OAuth2,
                Microservices, and Distributed Systems.
                """,

    "machine learning": """
                A Machine Learning Engineer is responsible for designing, training, evaluating, and
                deploying machine learning and deep learning models into production systems. The role
                is engineering-heavy: taking a model from experimentation to a reliable, monitored
                service that other systems depend on.

                Typical responsibilities include building and training neural networks, fine-tuning and
                deploying large language models, engineering retrieval-augmented generation pipelines,
                optimizing model inference and latency, building model-serving infrastructure, setting
                up MLOps pipelines for continuous training and deployment, monitoring models in
                production for drift, and integrating models into applications via APIs.

                Common job titles include Machine Learning Engineer, ML Engineer, Deep Learning
                Engineer, Computer Vision Engineer, NLP Engineer, LLM Engineer, Generative AI Engineer,
                MLOps Engineer, and AI Engineer.

                Common technologies include TensorFlow, PyTorch, Keras, Hugging Face Transformers,
                LangChain, LlamaIndex, OpenAI API, vector databases such as Pinecone, ChromaDB and
                FAISS, CUDA, model serving tools such as TorchServe or Triton, Docker, Kubernetes,
                MLflow, CNNs, RNNs, LSTMs, Transformers, BERT, GPT, and diffusion models.
                """,

    "data science": """
                A Data Scientist is responsible for analyzing data to answer business questions, build
                predictive models, and communicate insights that inform decisions made by stakeholders
                and leadership. The role is analysis-and-communication-heavy: turning raw data into a
                recommendation, report, or dashboard a non-technical audience can act on.

                Typical responsibilities include exploratory data analysis, cleaning and wrangling messy
                datasets, running statistical tests and hypothesis testing, building dashboards and
                reports for stakeholders, designing and analyzing A/B tests, building forecasting and
                recommendation models, presenting findings to business and product teams, and defining
                the KPIs used to track a product or business.

                Common job titles include Data Scientist, Data Analyst, Business Analyst, Analytics
                Engineer, Business Intelligence Analyst, Research Analyst, Quantitative Analyst, and
                Decision Scientist.

                Common technologies include Python, R, SQL, Excel, Power BI, Tableau, Pandas, NumPy,
                SciPy, Matplotlib, Seaborn, Plotly, Jupyter Notebook, scikit-learn, linear and logistic
                regression, decision trees, random forests, XGBoost, A/B testing frameworks, and
                statistical inference methods such as hypothesis testing and confidence intervals.
                """,

    "mobile": """
                A Mobile App Developer is responsible for designing, building, testing, and deploying
                native or cross-platform applications for iOS and Android devices. The role involves
                building on-device user interfaces, managing local storage, integrating with backend
                APIs, and shipping apps through the App Store and Play Store.

                Typical responsibilities include building responsive mobile UI screens, integrating
                REST or GraphQL APIs, handling offline data storage and syncing, implementing push
                notifications, managing app state and navigation, optimizing app performance and memory
                usage, testing across multiple devices and OS versions, and publishing and maintaining
                releases on the App Store and Google Play Store.

                Common job titles include Mobile App Developer, Android Developer, iOS Developer,
                Flutter Developer, React Native Developer, Kotlin Developer, Swift Developer, Mobile
                Engineer, and Cross-Platform App Developer.

                Common technologies include Kotlin, Java, Swift, Objective-C, Flutter, Dart, React
                Native, Android SDK, Jetpack Compose, SwiftUI, Xcode, Android Studio, Firebase, SQLite,
                Room, Core Data, REST API, Push Notifications, Play Store and App Store deployment, and
                MVVM architecture.
                """,

    "big data": """
                A Big Data Engineer is responsible for designing, building, and maintaining large-scale
                data pipelines and distributed systems that ingest, process, and store massive volumes
                of structured and unstructured data. The role is infrastructure-heavy: building the
                pipelines that other teams' analytics and models depend on.

                Typical responsibilities include building ETL and ELT pipelines, managing distributed
                storage and compute clusters, optimizing large-scale batch and streaming data jobs,
                orchestrating data workflows, ensuring data quality and reliability at scale, designing
                data warehouses and lakehouses, and scaling infrastructure to handle growing data
                volume.

                Common job titles include Big Data Engineer, Data Engineer, Hadoop Developer, Spark
                Developer, ETL Developer, Data Pipeline Engineer, and Data Platform Engineer.

                Common technologies include Hadoop, Apache Spark, Hive, Kafka, Flink, Airflow, HDFS,
                Scala, Java, Python, SQL, NoSQL databases such as Cassandra and HBase, Snowflake,
                Redshift, BigQuery, Databricks, AWS EMR, Azure Data Factory, GCP Dataflow, and data
                warehousing and distributed systems design.
                """,
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







    

