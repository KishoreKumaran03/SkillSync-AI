# SkillSync AI Industry Skill Database

CAREER_DATABASE = {
    "Software Engineer": {
        "required_skills": [
            "Data Structures", "Algorithms", "Java", "Python", "C++", 
            "Object-Oriented Programming (OOP)", "Database Management Systems (DBMS)", 
            "SQL", "Git", "Software Development Life Cycle (SDLC)", 
            "Operating Systems", "Computer Networks", "System Design"
        ],
        "recommended_certifications": [
            "Oracle Certified Professional: Java SE Developer",
            "Google IT Automation with Python Professional Certificate",
            "Meta Software Engineer Professional Certificate",
            "NPTEL: Programming in Java / Python for Data Science"
        ],
        "recommended_projects": [
            "Task Management System (CRUD application using Python/Java and SQL)",
            "E-commerce Backend API (RESTful service with user authentication and database integration)",
            "Multi-threaded Web Server (low-level network communication project)"
        ],
        "interview_topics": [
            "Object-Oriented Concepts (Inheritance, Polymorphism, Encapsulation, Abstraction)",
            "Data Structures (Arrays, Linked Lists, Trees, Graphs, Hash Maps, Stacks, Queues)",
            "Algorithms (Sorting, Searching, Dynamic Programming, Greedy, Recursion)",
            "SQL Queries (Joins, Indexing, Normalization, Transactions)",
            "System Design basics (Scalability, Load Balancing, Caching, CAP Theorem)"
        ]
    },
    "AI Engineer": {
        "required_skills": [
            "Python", "Machine Learning", "Deep Learning", "Neural Networks",
            "TensorFlow", "PyTorch", "Natural Language Processing (NLP)", 
            "Computer Vision", "Git", "Scikit-Learn", "Numpy", "Pandas", 
            "Linear Algebra", "Probability & Statistics", "Data Preprocessing"
        ],
        "recommended_certifications": [
            "DeepLearning.AI TensorFlow Developer Professional Certificate",
            "Google Cloud Professional Machine Learning Engineer",
            "DeepLearning.AI Generative AI with Large Language Models",
            "NPTEL: Deep Learning / Introduction to Machine Learning"
        ],
        "recommended_projects": [
            "Image Classification Model using Convolutional Neural Networks (CNNs)",
            "Sentiment Analysis Tool using NLP and Recurrent Neural Networks (RNNs) or Transformers",
            "End-to-End MLOps Pipeline (deploying a predictive model using FastAPI and Docker)"
        ],
        "interview_topics": [
            "Supervised vs Unsupervised Learning algorithms",
            "Overfitting, Underfitting, and Regularization techniques (L1/L2, Dropout)",
            "Deep Learning architecture details (CNNs, RNNs, LSTMs, Transformers, Attention Mechanism)",
            "Model evaluation metrics (Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix)",
            "Optimizers (SGD, Adam, RMSprop) and Loss Functions"
        ]
    },
    "Data Scientist": {
        "required_skills": [
            "Python", "R", "SQL", "Statistics", "Probability", "Data Visualization",
            "Machine Learning", "Data Mining", "Pandas", "Scikit-Learn", 
            "Jupyter Notebooks", "Feature Engineering", "A/B Testing", 
            "Tableau", "Power BI"
        ],
        "recommended_certifications": [
            "IBM Data Science Professional Certificate",
            "Google Advanced Data Analytics Professional Certificate",
            "Microsoft Certified: Azure Data Scientist Associate",
            "NPTEL: Data Science for Engineers"
        ],
        "recommended_projects": [
            "Predictive Analytics Dashboard (forecasting business sales or stock prices)",
            "Customer Segmentation Analysis (clustering users using K-Means and RFM analysis)",
            "A/B Testing Simulator (designing and executing statistical hypothesis tests on web traffic)"
        ],
        "interview_topics": [
            "Probability distributions and Central Limit Theorem",
            "Hypothesis testing (p-values, Type I/II errors, t-test, ANOVA, Chi-Square)",
            "Linear and Logistic Regression assumptions and mathematical foundations",
            "Dimensionality reduction techniques (PCA, t-SNE)",
            "Bias-Variance tradeoff"
        ]
    },
    "Data Analyst": {
        "required_skills": [
            "SQL", "Power BI", "Excel", "Python", "Tableau", "Statistics",
            "Data Visualization", "Data Cleaning", "Pandas", "Matplotlib", 
            "Seaborn", "Data Warehousing", "ETL Processes", "Reporting"
        ],
        "recommended_certifications": [
            "Google Data Analytics Professional Certificate",
            "Microsoft Certified: Power BI Data Analyst Associate",
            "Tableau Desktop Certified Associate",
            "NPTEL: Business Analytics for Management Decision"
        ],
        "recommended_projects": [
            "Interactive Business Intelligence Dashboard (tracking KPIs for sales or operations)",
            "SQL-Based Exploratory Data Analysis (cleaning and extracting trends from a massive public dataset)",
            "Automated ETL Pipeline (writing Python scripts to fetch, clean, and load data into a SQL database)"
        ],
        "interview_topics": [
            "Advanced SQL queries (Window functions, Subqueries, CTEs, Aggregations)",
            "Data visualization best practices and storytelling",
            "Data cleansing techniques (handling missing values, outliers, duplicates)",
            "Key Performance Indicators (KPIs) formulation and metrics definition",
            "Excel functions (VLOOKUP/XLOOKUP, Pivot Tables, Index-Match)"
        ]
    },
    "Embedded Engineer": {
        "required_skills": [
            "C", "Embedded C", "Microcontrollers", "RTOS", "PCB Design",
            "ARM Architecture", "I2C", "SPI", "UART", "GPIO", 
            "Firmware Development", "Debugging (JTAG/GDB)", "Oscilloscopes", 
            "Multimeters", "Assembly Language"
        ],
        "recommended_certifications": [
            "ARM Accredited Engineer (AAE)",
            "Coursera: Introduction to Embedded Systems Software and Development",
            "NPTEL: Embedded Systems / Microprocessors and Microcontrollers"
        ],
        "recommended_projects": [
            "Smart Home Automation Node (developing firmware using ESP32, RTOS, and MQTT)",
            "Obstacle Avoiding Robot (programming microcontrollers to handle sensors and motors in real-time)",
            "PCB Design for a Custom Microcontroller Board (using KiCad/Altium Designer)"
        ],
        "interview_topics": [
            "Interrupt handling, Interrupt Service Routines (ISRs), and context switching",
            "Memory management in embedded systems (Stack vs Heap, Flash vs RAM, Static allocation)",
            "Real-Time Operating System (RTOS) concepts (Tasks, Semaphores, Mutexes, Priority Inversion)",
            "Communication protocols details (SPI, I2C, UART, CAN, USB)",
            "Volatile keyword and registers manipulation"
        ]
    },
    "VLSI Engineer": {
        "required_skills": [
            "Verilog", "SystemVerilog", "VHDL", "Digital Design", "FPGA",
            "ASIC Design Flow", "Static Timing Analysis (STA)", "CMOS",
            "VLSI Architectures", "EDA Tools (Cadence/Synopsys)", "UVM", 
            "Logic Synthesis", "Scripting (Tcl/Perl/Python)"
        ],
        "recommended_certifications": [
            "Intel FPGA Certified Engineer",
            "Coursera: VLSI CAD Part I & II",
            "NPTEL: VLSI Design / Digital VLSI Testing"
        ],
        "recommended_projects": [
            "MIPS 32-bit RISC Processor Design (writing synthesizeable Verilog code and simulating it)",
            "FPGA-Based Video Processing Engine (implementing filters on live video stream on a development board)",
            "UVM-Based Verification Suite (verifying a dual-port RAM or FIFO using SystemVerilog UVM)"
        ],
        "interview_topics": [
            "Digital Design fundamentals (FSMs, Flip-Flops, Setup/Hold time, Clock Domain Crossing)",
            "Setup and Hold time violations and resolution techniques",
            "CMOS logic Gates, stick diagrams, and electrical characteristics",
            "FPGA Architecture (LUTs, CLBs, Routing Matrix, DSP slices)",
            "Verilog blocking vs non-blocking assignments"
        ]
    },
    "Cybersecurity Analyst": {
        "required_skills": [
            "Network Security", "Information Security", "Linux", "Firewalls", 
            "Ethical Hacking", "Vulnerability Assessment", "SIEM Tools", 
            "Incident Response", "Cryptography", "Wireshark", "Metasploit", 
            "Nmap", "OWASP Top 10", "Penetration Testing"
        ],
        "recommended_certifications": [
            "CompTIA Security+",
            "Certified Information Systems Security Professional (CISSP)",
            "Certified Ethical Hacker (CEH)",
            "NPTEL: Cryptography and Network Security"
        ],
        "recommended_projects": [
            "Vulnerability Assessment and Penetration Testing Report (analyzing a sandbox web app)",
            "Network Traffic Monitoring System (using Wireshark/Snort to detect intrusion patterns)",
            "Secure Web Application (implementing robust authentication, hashing, and defense against SQLi/XSS)"
        ],
        "interview_topics": [
            "OSI Model and security at each layer",
            "Symmetric vs Asymmetric Cryptography and SSL/TLS handshake",
            "OWASP Top 10 vulnerabilities (SQL Injection, Cross-Site Scripting, Broken Auth) and remediation",
            "IDS vs IPS and Firewall configuration principles",
            "Incident Response lifecycle"
        ]
    },
    "Cloud Engineer": {
        "required_skills": [
            "AWS", "Microsoft Azure", "Google Cloud Platform (GCP)", "Docker", 
            "Kubernetes", "Linux", "Terraform", "Infrastructure as Code (IaC)",
            "CI/CD Pipelines", "Networking (VPC, DNS, CDN)", "Cloud Security", 
            "Serverless (Lambda/Cloud Functions)", "Bash Scripting"
        ],
        "recommended_certifications": [
            "AWS Certified Solutions Architect – Associate",
            "Microsoft Certified: Azure Solutions Architect Expert",
            "Google Cloud Certified Associate Cloud Engineer",
            "HashiCorp Certified: Terraform Associate"
        ],
        "recommended_projects": [
            "Multi-tier Cloud Architecture Deployment (using Terraform to spin up VPCs, Load Balancers, and EC2s on AWS)",
            "Containerized Microservices Orchestration (building Docker images and deploying them to Kubernetes)",
            "Serverless Web API (building a serverless backend using AWS Lambda, API Gateway, and DynamoDB)"
        ],
        "interview_topics": [
            "Cloud computing service models (IaaS, PaaS, SaaS) and deployment models",
            "Docker containerization vs Virtual Machines",
            "Kubernetes components (Pods, Services, Deployments, Kubelet, Control Plane)",
            "High Availability, Fault Tolerance, and Disaster Recovery strategies in the cloud",
            "Identity and Access Management (IAM) best practices"
        ]
    },
    "Full Stack Developer": {
        "required_skills": [
            "HTML5", "CSS3", "JavaScript", "React.js", "Node.js", "Express.js",
            "MongoDB", "SQL", "Git", "REST APIs", "TypeScript", 
            "Next.js", "Tailwind CSS", "Redux", "Web Performance Optimization"
        ],
        "recommended_certifications": [
            "Meta Front-End / Back-End Developer Professional Certificate",
            "IBM Full Stack Software Developer Professional Certificate",
            "NPTEL: Modern Application Development"
        ],
        "recommended_projects": [
            "Social Media Application (using MERN stack with JWT authentication and real-time messaging using Socket.io)",
            "Collaborative Kanban Board (Trello clone with drag-and-drop features and persistent state in MongoDB/PostgreSQL)",
            "SEO-Optimized Blog Engine (using Next.js, headless CMS, and Tailwind CSS)"
        ],
        "interview_topics": [
            "DOM manipulation, event bubbling, and JavaScript Event Loop",
            "React hook lifecycle and state management (Redux, Context API, Zustand)",
            "REST API design constraints and HTTP status codes",
            "Database indexing and relational vs non-relational database selection criteria",
            "Web security basics (CORS, CSRF, JWT, XSS)"
        ]
    },
    "DevOps Engineer": {
        "required_skills": [
            "Linux", "Git", "Docker", "Kubernetes", "Jenkins", "GitHub Actions",
            "Terraform", "Ansible", "Bash Scripting", "Python", "Prometheus", 
            "Grafana", "CI/CD", "AWS", "Nginx"
        ],
        "recommended_certifications": [
            "Certified Kubernetes Administrator (CKA)",
            "AWS Certified DevOps Engineer – Professional",
            "Puppet / Ansible Certified Associate",
            "NPTEL: Software Engineering / Cloud Computing"
        ],
        "recommended_projects": [
            "Automated CI/CD Pipeline (setting up a Jenkins/GitHub Actions pipeline for automated linting, testing, and Docker push)",
            "Infrastructure Monitoring Dashboard (setting up Prometheus and Grafana on a Kubernetes cluster to monitor node metrics)",
            "Infrastructure Provisioning & Configuration (using Terraform to build servers and Ansible to configure them automatically)"
        ],
        "interview_topics": [
            "Continuous Integration vs Continuous Deployment/Delivery (CI/CD) workflows",
            "Infrastructure as Code (IaC) advantages and Terraform state management",
            "Kubernetes architecture, self-healing, and rolling update strategies",
            "Monitoring, logging, and alerting practices (ELK Stack, Prometheus, Grafana)",
            "Linux system administration concepts (Process management, SSH, File permissions, Cron jobs)"
        ]
    }
}
