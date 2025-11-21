from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import json
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
import PyPDF2
import docx
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'skillmate_secret_key_2023'
CORS(app, supports_credentials=True)

# Mock database
users_db = {}

# Expanded job roles database with 25+ IT roles
job_roles_db = {
    "Frontend Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Vue", "Angular", "TypeScript", "Responsive Design", "UI/UX Principles", "Git", "Webpack", "REST APIs", "SASS", "Bootstrap", "jQuery"],
        "description": "Builds user-facing components of web applications"
    },
    "Backend Developer": {
        "skills": ["Python", "Java", "Node.js", "SQL", "NoSQL", "API Development", "Server Management", "Docker", "Linux", "AWS", "Microservices", "REST", "GraphQL", "Spring Boot", "Express.js", "Django", "Flask"],
        "description": "Works on server-side logic and database management"
    },
    "Full Stack Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Python", "SQL", "MongoDB", "Git", "Docker", "REST APIs", "AWS", "TypeScript", "Express.js", "Redux"],
        "description": "Handles both frontend and backend development"
    },
    "QA Engineer (Testing)": {
        "skills": ["Test Automation", "Selenium", "Cypress", "JUnit", "TestNG", "Python", "Java", "API Testing", "Performance Testing", "Agile", "JIRA", "Postman", "JMeter", "Manual Testing", "Test Planning", "SQL", "Git", "CI/CD"],
        "description": "Ensures software quality through testing"
    },
    "DevOps Engineer": {
        "skills": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "GitLab", "Terraform", "Ansible", "Linux", "Python", "Bash", "Monitoring", "Cloud Formation", "Helm"],
        "description": "Manages infrastructure and deployment pipelines"
    },
    "Data Scientist": {
        "skills": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "TensorFlow", "PyTorch", "Data Visualization", "Big Data", "Deep Learning", "Natural Language Processing", "Computer Vision"],
        "description": "Extracts insights from data using statistical methods"
    },
    "Data Analyst": {
        "skills": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Statistics", "Data Visualization", "Pandas", "Data Cleaning", "Business Intelligence", "R", "Google Analytics"],
        "description": "Analyzes data to support business decisions"
    },
    "Machine Learning Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "MLOps", "AWS SageMaker", "Data Pipelines", "Model Deployment", "Natural Language Processing", "Computer Vision"],
        "description": "Builds and deploys machine learning models"
    },
    "Cloud Engineer": {
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux", "Networking", "Security", "Python", "Infrastructure as Code", "CI/CD", "Cloud Formation"],
        "description": "Designs and manages cloud infrastructure"
    },
    "Security Engineer": {
        "skills": ["Network Security", "Cybersecurity", "Penetration Testing", "Firewalls", "Encryption", "Security Protocols", "Python", "Linux", "Ethical Hacking", "Vulnerability Assessment", "SIEM", "SOC"],
        "description": "Protects systems and networks from cyber threats"
    },
    "Mobile Developer (iOS)": {
        "skills": ["Swift", "Objective-C", "Xcode", "iOS SDK", "UIKit", "Core Data", "REST APIs", "Git", "CocoaPods", "Auto Layout", "MVVM", "Core Animation"],
        "description": "Develops applications for iOS devices"
    },
    "Mobile Developer (Android)": {
        "skills": ["Java", "Kotlin", "Android Studio", "Android SDK", "REST APIs", "Git", "Material Design", "Room Database", "Retrofit", "MVVM", "Coroutines", "Firebase"],
        "description": "Develops applications for Android devices"
    },
    "UX/UI Designer": {
        "skills": ["Figma", "Adobe XD", "Sketch", "User Research", "Wireframing", "Prototyping", "User Testing", "Design Systems", "Interaction Design", "Visual Design", "Accessibility", "HTML/CSS"],
        "description": "Designs user interfaces and experiences"
    },
    "Product Manager": {
        "skills": ["Product Strategy", "Market Research", "User Stories", "Agile", "Scrum", "Roadmapping", "Analytics", "Stakeholder Management", "A/B Testing", "Prioritization", "Business Analysis"],
        "description": "Defines product vision and manages development"
    },
    "Database Administrator": {
        "skills": ["SQL", "MySQL", "PostgreSQL", "Oracle", "MongoDB", "Database Design", "Performance Tuning", "Backup/Recovery", "Security", "NoSQL", "Data Modeling", "ETL"],
        "description": "Manages and maintains database systems"
    },
    "Network Engineer": {
        "skills": ["Cisco", "Juniper", "TCP/IP", "Routing", "Switching", "Firewalls", "VPN", "Network Security", "Wireshark", "Linux", "Python", "Cloud Networking"],
        "description": "Designs and maintains computer networks"
    },
    "Systems Administrator": {
        "skills": ["Linux", "Windows Server", "Active Directory", "PowerShell", "Bash", "Virtualization", "Backup Solutions", "Monitoring", "Security", "Networking", "Docker", "AWS"],
        "description": "Manages and maintains IT infrastructure"
    },
    "Business Analyst": {
        "skills": ["Requirements Gathering", "Process Modeling", "SQL", "Excel", "PowerPoint", "JIRA", "Confluence", "UML", "Stakeholder Management", "Data Analysis", "Agile Methodology"],
        "description": "Bridges business needs with technical solutions"
    },
    "Technical Writer": {
        "skills": ["Technical Documentation", "API Documentation", "Markdown", "Git", "Content Management", "User Guides", "Style Guides", "Research", "Editing", "Tools Documentation"],
        "description": "Creates technical documentation and manuals"
    },
    "Scrum Master": {
        "skills": ["Agile Methodology", "Scrum Framework", "JIRA", "Confluence", "Team Facilitation", "Conflict Resolution", "Coaching", "Metrics Tracking", "Retrospectives", "Stakeholder Communication"],
        "description": "Facilitates agile development processes"
    },
    "Site Reliability Engineer (SRE)": {
        "skills": ["Linux", "Python", "Go", "Monitoring", "Alerting", "Incident Management", "Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Performance Optimization"],
        "description": "Ensures system reliability and performance"
    },
    "Blockchain Developer": {
        "skills": ["Solidity", "Ethereum", "Smart Contracts", "Web3.js", "Cryptography", "Node.js", "React", "Truffle", "Ganache", "Blockchain Architecture", "DeFi", "NFTs"],
        "description": "Develops decentralized applications"
    },
    "Game Developer": {
        "skills": ["C++", "C#", "Unity", "Unreal Engine", "3D Mathematics", "Game Physics", "AI Programming", "Multiplayer Networking", "Shader Programming", "Optimization", "VR/AR Development"],
        "description": "Creates video games and interactive experiences"
    },
    "Embedded Systems Engineer": {
        "skills": ["C", "C++", "Python", "Microcontrollers", "RTOS", "Embedded Linux", "Device Drivers", "Hardware Interfaces", "Debugging", "Communication Protocols", "PCB Design"],
        "description": "Develops software for hardware devices"
    },
    "AI Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "MLOps", "Data Pipelines", "Cloud AI Services"],
        "description": "Builds artificial intelligence systems"
    },
    "IT Project Manager": {
        "skills": ["Project Management", "Agile", "Waterfall", "Risk Management", "Budgeting", "Stakeholder Management", "JIRA", "MS Project", "Team Leadership", "Scope Management", "Quality Assurance"],
        "description": "Manages IT projects from conception to delivery"
    }
}

# Expanded learning resources database with 25+ IT roles
learning_resources_db = {
    # Existing skills (keeping your original ones)
    "Python": {
        "courses": [
            {"name": "Python for Everybody - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python", "level": "Beginner"},
            {"name": "Complete Python Bootcamp - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "level": "Beginner"},
            {"name": "Advanced Python Programming - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/advanced-python-programming/", "level": "Advanced"}
        ],
        "certifications": [
            {"name": "PCEP - Certified Entry-Level Python Programmer", "issuer": "Python Institute", "url": "https://pythoninstitute.org/pcep"},
            {"name": "PCAP - Certified Associate in Python Programming", "issuer": "Python Institute", "url": "https://pythoninstitute.org/pcap"},
            {"name": "Python for Data Science - IBM", "issuer": "IBM", "url": "https://www.coursera.org/professional-certificates/ibm-data-science"}
        ],
        "youtube": [
            {"name": "Python Full Course for Beginners", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "duration": "6:14:07"},
            {"name": "Python Tutorial - Python for Beginners", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "duration": "4:26:52"},
            {"name": "Advanced Python Programming", "channel": "Tech With Tim", "url": "https://www.youtube.com/playlist?list=PLzMcBGfZo4-kSJVMyYeOQ8CXJ3z1k7gHn", "duration": "Playlist"}
        ]
    },
    "JavaScript": {
        "courses": [
            {"name": "The Complete JavaScript Course 2024 - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-javascript-course/", "level": "Beginner to Advanced"},
            {"name": "JavaScript Algorithms and Data Structures - freeCodeCamp", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "level": "Intermediate"},
            {"name": "Modern JavaScript From The Beginning - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/modern-javascript-from-the-beginning/", "level": "All Levels"}
        ],
        "certifications": [
            {"name": "JavaScript Developer Certification", "issuer": "W3Schools", "url": "https://www.w3schools.com/cert/cert_javascript.asp"},
            {"name": "MTA: JavaScript Certification", "issuer": "Microsoft", "url": "https://docs.microsoft.com/en-us/learn/certifications/mta-javascript/"}
        ],
        "youtube": [
            {"name": "JavaScript Tutorial for Beginners", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=W6NZfCO5SIk", "duration": "1:00:00"},
            {"name": "Learn JavaScript - Full Course for Beginners", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg", "duration": "3:26:43"},
            {"name": "JavaScript Advanced Concepts", "channel": "CodeWithHarry", "url": "https://www.youtube.com/playlist?list=PLu0W_9lII9ahR1blWXxgSlL4y9iQBnLpR", "duration": "Playlist"}
        ]
    },
    "React": {
        "courses": [
            {"name": "The Complete React Developer Course - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/react-2nd-edition/", "level": "Beginner to Advanced"},
            {"name": "React - The Complete Guide - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "level": "All Levels"},
            {"name": "Frontend Development with React - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/front-end-react", "level": "Intermediate"}
        ],
        "certifications": [
            {"name": "React Developer Certification", "issuer": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/"},
            {"name": "Meta React Native Specialization", "issuer": "Coursera", "url": "https://www.coursera.org/specializations/meta-react-native"}
        ],
        "youtube": [
            {"name": "React JS Full Course for Beginners", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=SqcY0GlETPk", "duration": "7:23:21"},
            {"name": "Learn React In 30 Minutes", "channel": "Web Dev Simplified", "url": "https://www.youtube.com/watch?v=hQAHSlTtcmY", "duration": "30:00"},
            {"name": "React Tutorial for Beginners", "channel": "CodeWithHarry", "url": "https://www.youtube.com/watch?v=IR6smI_YJDE", "duration": "5:38:31"}
        ]
    },
    # New skills for additional roles
    "Docker": {
        "courses": [
            {"name": "Docker Mastery - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-mastery/", "level": "Beginner to Advanced"},
            {"name": "Docker & Kubernetes: The Practical Guide - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", "level": "Intermediate"},
            {"name": "Getting Started with Docker - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/getting-started-with-docker", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Docker Certified Associate", "issuer": "Docker", "url": "https://www.docker.com/certification/"},
            {"name": "Kubernetes and Cloud Native Associate", "issuer": "Linux Foundation", "url": "https://training.linuxfoundation.org/certification/kubernetes-cloud-native-associate/"}
        ],
        "youtube": [
            {"name": "Docker Tutorial for Beginners", "channel": "TechWorld with Nana", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "duration": "2:46:15"},
            {"name": "Learn Docker in 1 Hour", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "duration": "1:10:00"},
            {"name": "Docker Complete Course", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=9zUHg7xjIqQ", "duration": "3:53:40"}
        ]
    },
    "Kubernetes": {
        "courses": [
            {"name": "Kubernetes for Absolute Beginners - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/learn-kubernetes/", "level": "Beginner"},
            {"name": "Certified Kubernetes Administrator (CKA) - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/certified-kubernetes-administrator-with-practice-tests/", "level": "Advanced"},
            {"name": "Introduction to Kubernetes - edX", "platform": "edX", "url": "https://www.edx.org/learn/kubernetes", "level": "Intermediate"}
        ],
        "certifications": [
            {"name": "Certified Kubernetes Administrator (CKA)", "issuer": "Linux Foundation", "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/"},
            {"name": "Certified Kubernetes Application Developer (CKAD)", "issuer": "Linux Foundation", "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/"}
        ],
        "youtube": [
            {"name": "Kubernetes Tutorial for Beginners", "channel": "TechWorld with Nana", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "duration": "3:10:00"},
            {"name": "Kubernetes Course - Full Beginners Tutorial", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=d6WC5n9G_sM", "duration": "4:15:00"},
            {"name": "Learn Kubernetes in 1 Hour", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=7bA0gTroJjw", "duration": "1:00:00"}
        ]
    },
    "AWS": {
        "courses": [
            {"name": "AWS Certified Solutions Architect - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/", "level": "Intermediate"},
            {"name": "AWS Cloud Practitioner Essentials", "platform": "AWS", "url": "https://www.aws.training/Details/eLearning?id=60697", "level": "Beginner"},
            {"name": "AWS Certified Developer - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/aws-certified-developer-associate-dva-c01/", "level": "Intermediate"}
        ],
        "certifications": [
            {"name": "AWS Certified Cloud Practitioner", "issuer": "Amazon", "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/"},
            {"name": "AWS Certified Solutions Architect", "issuer": "Amazon", "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/"},
            {"name": "AWS Certified Developer", "issuer": "Amazon", "url": "https://aws.amazon.com/certification/certified-developer-associate/"}
        ],
        "youtube": [
            {"name": "AWS Tutorial for Beginners", "channel": "Simplilearn", "url": "https://www.youtube.com/watch?v=ulprqHHWlng", "duration": "9:26:12"},
            {"name": "AWS Full Course", "channel": "Edureka", "url": "https://www.youtube.com/watch?v=3hLmDS179YE", "duration": "10:15:33"},
            {"name": "AWS Certified Solutions Architect", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=Ia-UEYYR44s", "duration": "12:14:39"}
        ]
    },
    "Machine Learning": {
        "courses": [
            {"name": "Machine Learning by Andrew Ng - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/machine-learning", "level": "Intermediate"},
            {"name": "Python for Data Science and Machine Learning - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/", "level": "Beginner to Advanced"},
            {"name": "Deep Learning Specialization - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning", "level": "Advanced"}
        ],
        "certifications": [
            {"name": "TensorFlow Developer Certificate", "issuer": "Google", "url": "https://www.tensorflow.org/certificate"},
            {"name": "AWS Certified Machine Learning", "issuer": "Amazon", "url": "https://aws.amazon.com/certification/certified-machine-learning-speciality/"},
            {"name": "Microsoft Certified: Azure AI Engineer", "issuer": "Microsoft", "url": "https://docs.microsoft.com/en-us/learn/certifications/azure-ai-engineer/"}
        ],
        "youtube": [
            {"name": "Machine Learning Course for Beginners", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=NWONeJKn6kc", "duration": "10:17:57"},
            {"name": "Machine Learning Full Course", "channel": "Simplilearn", "url": "https://www.youtube.com/watch?v=GwIo3gDZCVQ", "duration": "9:52:18"},
            {"name": "Deep Learning Specialization", "channel": "DeepLearningAI", "url": "https://www.youtube.com/playlist?list=PLkDaE6sCZn6Hn0vK8co82zjQtt3T2Nkqc", "duration": "Playlist"}
        ]
    },
    "Java": {
        "courses": [
            {"name": "Java Programming Masterclass - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/", "level": "Beginner to Advanced"},
            {"name": "Object Oriented Programming in Java - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/object-oriented-java", "level": "Intermediate"},
            {"name": "Java Programming and Software Engineering Fundamentals - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/java-programming", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Oracle Certified Associate, Java SE 8 Programmer", "issuer": "Oracle", "url": "https://education.oracle.com/java-se-8-programmer-i/pexam_1Z0-808"},
            {"name": "Oracle Certified Professional, Java SE 11 Developer", "issuer": "Oracle", "url": "https://education.oracle.com/java-se-11-developer/pexam_1Z0-819"}
        ],
        "youtube": [
            {"name": "Java Tutorial for Beginners", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=eIrMbAQSU34", "duration": "2:30:00"},
            {"name": "Java Full Course", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=xk4_1vDrzzo", "duration": "12:00:00"},
            {"name": "Java Programming Tutorial", "channel": "CodeWithHarry", "url": "https://www.youtube.com/watch?v=BGTx91t8q50", "duration": "9:30:00"}
        ]
    },
    "Swift": {
        "courses": [
            {"name": "iOS & Swift - The Complete iOS App Development Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/ios-13-app-development-bootcamp/", "level": "Beginner"},
            {"name": "SwiftUI Masterclass - iOS App Development", "platform": "Udemy", "url": "https://www.udemy.com/course/swiftui-masterclass-course-ios-app-with-swift/", "level": "Intermediate"},
            {"name": "Develop iOS Apps with Swift - Apple", "platform": "Apple", "url": "https://developer.apple.com/learn/curriculum/", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Apple Certified iOS Technician", "issuer": "Apple", "url": "https://www.apple.com/support/programs/"},
            {"name": "iOS Development with Swift Certification", "issuer": "Coursera", "url": "https://www.coursera.org/specializations/app-development"}
        ],
        "youtube": [
            {"name": "Swift Tutorial for Beginners", "channel": "CodeWithChris", "url": "https://www.youtube.com/watch?v=comQ1-x2a1Q", "duration": "3:22:00"},
            {"name": "Learn Swift Programming", "channel": "Sean Allen", "url": "https://www.youtube.com/playlist?list=PL8seg1JPkqgF5wazzCKSq3EEfqt3t8mvA", "duration": "Playlist"},
            {"name": "SwiftUI Tutorial for Beginners", "channel": "DesignCode", "url": "https://www.youtube.com/watch?v=HXoVSbwWUIk", "duration": "4:30:00"}
        ]
    },
    "Kotlin": {
        "courses": [
            {"name": "Kotlin for Java Developers - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/kotlin-for-java-developers", "level": "Intermediate"},
            {"name": "Android Kotlin Development Masterclass - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/android-kotlin-developer/", "level": "Beginner to Advanced"},
            {"name": "Kotlin Bootcamp for Programmers - Google", "platform": "Google", "url": "https://developer.android.com/courses/kotlin-bootcamp/overview", "level": "Intermediate"}
        ],
        "certifications": [
            {"name": "Associate Android Developer", "issuer": "Google", "url": "https://developers.google.com/certification/associate-android-developer"},
            {"name": "Kotlin Certified Developer", "issuer": "JetBrains", "url": "https://kotlinlang.org/certification/"}
        ],
        "youtube": [
            {"name": "Kotlin Tutorial for Beginners", "channel": "Coding with Mitch", "url": "https://www.youtube.com/watch?v=VEqhzCFmEQI", "duration": "2:25:00"},
            {"name": "Learn Kotlin - Full Course for Beginners", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=F9UC9DY-vIU", "duration": "2:37:00"},
            {"name": "Kotlin Android Development", "channel": "Philipp Lackner", "url": "https://www.youtube.com/playlist?list=PLQkwcJG4YTCSpJ2NLhDTHhi6XBNfk9WiC", "duration": "Playlist"}
        ]
    },
    "Figma": {
        "courses": [
            {"name": "UI/UX Design with Figma - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/ui-ux-design-with-figma/", "level": "Beginner"},
            {"name": "Figma UI UX Design Essentials - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/figma-ux-ui-design-web-design-mobile-app-design/", "level": "Beginner"},
            {"name": "Learn Figma - UI/UX Design Essential Training", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/learning-figma", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Figma Certification", "issuer": "Figma", "url": "https://www.figma.com/education/"},
            {"name": "UI/UX Design Specialization", "issuer": "Coursera", "url": "https://www.coursera.org/specializations/ui-ux-design"}
        ],
        "youtube": [
            {"name": "Figma Tutorial for UI Design", "channel": "DesignCourse", "url": "https://www.youtube.com/watch?v=HZuk6Wkx_Eg", "duration": "1:47:23"},
            {"name": "Learn Figma in 25 Minutes", "channel": "Flux Academy", "url": "https://www.youtube.com/watch?v=FTFaQWZBqQ8", "duration": "25:00"},
            {"name": "Figma UI Design Tutorial", "channel": "Bring Your Own Laptop", "url": "https://www.youtube.com/watch?v=XRONgtKqcIc", "duration": "2:15:00"}
        ]
    },
    "Product Strategy": {
        "courses": [
            {"name": "Digital Product Management Specialization - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/product-management", "level": "Intermediate"},
            {"name": "Become a Product Manager - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/become-a-product-manager/", "level": "Beginner"},
            {"name": "Product Management Fundamentals - edX", "platform": "edX", "url": "https://www.edx.org/learn/product-management", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Product Manager Certification", "issuer": "Product School", "url": "https://productschool.com/product-manager-certification/"},
            {"name": "Professional Product Manager", "issuer": "280 Group", "url": "https://280group.com/product-management-certification/"}
        ],
        "youtube": [
            {"name": "Product Management Full Course", "channel": "Simplilearn", "url": "https://www.youtube.com/watch?v=8WL9Vd0VU_0", "duration": "6:30:00"},
            {"name": "Product Management Tutorial", "channel": "CareerFoundry", "url": "https://www.youtube.com/watch?v=6sUIlihdW4E", "duration": "1:15:00"},
            {"name": "Product Management Fundamentals", "channel": "Product Manager HQ", "url": "https://www.youtube.com/playlist?list=PLRK9-6x1qPRXJt0a9vCGy_0Wf5sQX8x9T", "duration": "Playlist"}
        ]
    },
    "Cybersecurity": {
        "courses": [
            {"name": "Introduction to Cyber Security Specialization - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/intro-cyber-security", "level": "Beginner"},
            {"name": "The Complete Cyber Security Course - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-internet-security-privacy-course-volume-1/", "level": "Beginner to Advanced"},
            {"name": "Cybersecurity for Everyone - edX", "platform": "edX", "url": "https://www.edx.org/learn/cybersecurity", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "CompTIA Security+", "issuer": "CompTIA", "url": "https://www.comptia.org/certifications/security"},
            {"name": "Certified Ethical Hacker (CEH)", "issuer": "EC-Council", "url": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/"},
            {"name": "CISSP", "issuer": "ISC2", "url": "https://www.isc2.org/Certifications/CISSP"}
        ],
        "youtube": [
            {"name": "Cybersecurity Full Course", "channel": "Simplilearn", "url": "https://www.youtube.com/watch?v=PlHnamdwGmw", "duration": "11:35:00"},
            {"name": "Introduction to Cybersecurity", "channel": "NetworkChuck", "url": "https://www.youtube.com/watch?v=sdpxddDzXfE", "duration": "1:15:00"},
            {"name": "Cybersecurity for Beginners", "channel": "Cybersecurity for Everyone", "url": "https://www.youtube.com/playlist?list=PLtPJ9lKvJ4oiwLhL1-1k6CwN5-2a_YV6e", "duration": "Playlist"}
        ]
    },
    "TensorFlow": {
        "courses": [
            {"name": "TensorFlow Developer Certificate - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "level": "Intermediate"},
            {"name": "Complete Guide to TensorFlow for Deep Learning - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/complete-guide-to-tensorflow-for-deep-learning-with-python/", "level": "Intermediate"},
            {"name": "TensorFlow 2.0 Complete Course - Python Neural Networks", "platform": "Udemy", "url": "https://www.udemy.com/course/tensorflow-developer-certificate-machine-learning-zero-to-mastery/", "level": "Advanced"}
        ],
        "certifications": [
            {"name": "TensorFlow Developer Certificate", "issuer": "Google", "url": "https://www.tensorflow.org/certificate"},
            {"name": "Deep Learning Specialization", "issuer": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning"}
        ],
        "youtube": [
            {"name": "TensorFlow 2.0 Complete Course", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=tPYj3fFJGjk", "duration": "7:01:00"},
            {"name": "TensorFlow Tutorial for Beginners", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=6_2hzRopPbQ", "duration": "1:37:00"},
            {"name": "Deep Learning with TensorFlow", "channel": "Sentdex", "url": "https://www.youtube.com/playlist?list=PLQVvvaa0QuDfhTox0AjmQ6tvTgMBZBEXN", "duration": "Playlist"}
        ]
    },
    "Solidity": {
        "courses": [
            {"name": "Ethereum and Solidity: The Complete Developer's Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/ethereum-and-solidity-the-complete-developers-guide/", "level": "Intermediate"},
            {"name": "Blockchain A-Z: Learn How To Build Your First Blockchain", "platform": "Udemy", "url": "https://www.udemy.com/course/build-your-blockchain-az/", "level": "Beginner"},
            {"name": "Smart Contract Development with Solidity - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/smart-contract-development", "level": "Intermediate"}
        ],
        "certifications": [
            {"name": "Certified Blockchain Developer", "issuer": "Blockchain Council", "url": "https://www.blockchain-council.org/certifications/certified-blockchain-developer/"},
            {"name": "Ethereum Developer Certification", "issuer": "ConsenSys", "url": "https://consensys.net/academy/"}
        ],
        "youtube": [
            {"name": "Solidity Tutorial Course", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=ipwxYa-F1uY", "duration": "16:22:00"},
            {"name": "Learn Solidity in 1 Hour", "channel": "Dapp University", "url": "https://www.youtube.com/watch?v=EhPeHeoKF88", "duration": "1:00:00"},
            {"name": "Blockchain Development Tutorial", "channel": "Smart Contract Programmer", "url": "https://www.youtube.com/playlist?list=PLO5VPQH6OWdX-Rh7RonjZhOd9pb9zOnHW", "duration": "Playlist"}
        ]
    },
    "Unity": {
        "courses": [
            {"name": "Complete C# Unity Game Developer 3D - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/unitycourse2/", "level": "Beginner"},
            {"name": "Unity Game Development Mini-Degree - Zenva", "platform": "Zenva", "url": "https://academy.zenva.com/product/game-development-mini-degree/", "level": "Beginner to Advanced"},
            {"name": "Introduction to Game Development - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/introduction-game-development", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Unity Certified Programmer", "issuer": "Unity", "url": "https://unity.com/products/unity-certifications"},
            {"name": "Unity Certified User", "issuer": "Unity", "url": "https://unity.com/products/unity-certifications"}
        ],
        "youtube": [
            {"name": "Unity Tutorial for Beginners", "channel": "Brackeys", "url": "https://www.youtube.com/watch?v=pwZpJzpE2lQ", "duration": "1:06:00"},
            {"name": "Learn Unity - Beginner's Game Development Tutorial", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=gB1F9G0JXOo", "duration": "7:28:00"},
            {"name": "Unity 2D Game Development", "channel": "Blackthornprod", "url": "https://www.youtube.com/playlist?list=PLBIb_auVtBwDgHLRkfIiFkQSwS7q2rXjV", "duration": "Playlist"}
        ]
    },
    "C++": {
        "courses": [
            {"name": "Beginning C++ Programming - From Beginner to Beyond", "platform": "Udemy", "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/", "level": "Beginner"},
            {"name": "C++ Programming for Unreal Game Development - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/c-programming-unreal-game-development", "level": "Intermediate"},
            {"name": "Learn Advanced C++ Programming - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/learn-advanced-c-programming/", "level": "Advanced"}
        ],
        "certifications": [
            {"name": "C++ Certified Associate Programmer", "issuer": "C++ Institute", "url": "https://cppinstitute.org/cpa-certification"},
            {"name": "C++ Certified Professional Programmer", "issuer": "C++ Institute", "url": "https://cppinstitute.org/cpp-certification"}
        ],
        "youtube": [
            {"name": "C++ Tutorial for Beginners", "channel": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=vLnPwxZdW4Y", "duration": "4:01:00"},
            {"name": "C++ Programming Course", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=ZzaPdXTrSb8", "duration": "2:22:00"},
            {"name": "Advanced C++ Programming", "channel": "The Cherno", "url": "https://www.youtube.com/playlist?list=PLlrATfBNZ98dudnM48yfGUldqGD0S4FFb", "duration": "Playlist"}
        ]
    },
    "Agile Methodology": {
        "courses": [
            {"name": "Agile Crash Course: Agile Project Management - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/agile-crash-course/", "level": "Beginner"},
            {"name": "Agile Development Specialization - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/specializations/agile-development", "level": "Intermediate"},
            {"name": "Scrum Master Certification Training - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/scrummaster-certification/", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Professional Scrum Master I", "issuer": "Scrum.org", "url": "https://www.scrum.org/professional-scrum-master-i-certification"},
            {"name": "Certified ScrumMaster", "issuer": "Scrum Alliance", "url": "https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster"},
            {"name": "PMI Agile Certified Practitioner", "issuer": "PMI", "url": "https://www.pmi.org/certifications/agile-acp"}
        ],
        "youtube": [
            {"name": "Agile Project Management Full Course", "channel": "Simplilearn", "url": "https://www.youtube.com/watch?v=MIY1g4oH-0I", "duration": "2:37:37"},
            {"name": "What is Agile?", "channel": "IBM Technology", "url": "https://www.youtube.com/watch?v=Z9QbYZh1YXY", "duration": "8:03"},
            {"name": "Scrum in 20 Minutes", "channel": "Product Mastery Now", "url": "https://www.youtube.com/watch?v=vuBFzAdaHDY", "duration": "20:00"}
        ]
    },
    "Project Management": {
        "courses": [
            {"name": "Google Project Management Professional Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-project-management", "level": "Beginner"},
            {"name": "PMP Certification Exam Prep - Udemy", "platform": "Udemy", "url": "https://www.udemy.com/course/pmp-certification-exam-prep-course-pmbok-6th-edition/", "level": "Advanced"},
            {"name": "Project Management Principles and Practices - Coursera", "platform": "Coursera", "url": "https://www.coursera.org/learn/project-management-principles-practices", "level": "Beginner"}
        ],
        "certifications": [
            {"name": "Project Management Professional (PMP)", "issuer": "PMI", "url": "https://www.pmi.org/certifications/project-management-pmp"},
            {"name": "Certified Associate in Project Management (CAPM)", "issuer": "PMI", "url": "https://www.pmi.org/certifications/certified-associate-capm"},
            {"name": "PRINCE2 Foundation & Practitioner", "issuer": "AXELOS", "url": "https://www.axelos.com/certifications/prince2"}
        ],
        "youtube": [
            {"name": "Project Management Full Course", "channel": "Simplilearn", "url": "https://www.youtube.com/watch?v=uWPIsaYpY7U", "duration": "4:33:00"},
            {"name": "Project Management Tutorial", "channel": "ProjectManager", "url": "https://www.youtube.com/watch?v=BDsv8s6TzXU", "duration": "1:03:00"},
            {"name": "PMP Exam Preparation", "channel": "PMC Lounge", "url": "https://www.youtube.com/playlist?list=PL1txC5ws--zcx6l2Y1V6dX0yH0VZ8Z2lZ", "duration": "Playlist"}
        ]
    }
}

# Admin jobs database
admin_jobs_db = [
    {
        "id": 1,
        "designation": "Junior QA",
        "category": "qa",
        "salary": "500000",
        "sort_order": 0,
        "status": "enabled",
        "skills": ["SQL", "Testing", "Automation"],
        "description": "Junior Quality Assurance Engineer"
    }
]

# Helper function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# Helper function to extract text from DOCX
def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

# Routes
@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    user_email = session.get('user')
    if user_email and user_email in users_db:
        user = users_db[user_email]
        return jsonify({
            'authenticated': True,
            'user': {
                'email': user_email,
                'name': user['name'],
                'role': user['role']
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role')
        
        if not email or not password or not name or not role:
            return jsonify({'error': 'All fields are required'}), 400
        
        if email in users_db:
            return jsonify({'error': 'User already exists'}), 400
        
        users_db[email] = {
            'name': name,
            'password': generate_password_hash(password),
            'role': role
        }
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'email': email,
                'name': name,
                'role': role
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = users_db.get(email)
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        session['user'] = email
        return jsonify({
            'message': 'Login successful', 
            'user': {
                'email': email, 
                'name': user['name'], 
                'role': user['role']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-roles', methods=['GET'])
def get_job_roles():
    return jsonify(job_roles_db)

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif file.filename.lower().endswith(('.doc', '.docx')):
            text = extract_text_from_docx(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        return jsonify({
            'text': text,
            'message': 'Resume parsed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-skills', methods=['POST'])
def analyze_skills():
    try:
        data = request.json
        current_skills = data.get('current_skills', [])
        target_role = data.get('target_role')
        resume_text = data.get('resume_text', '')
        
        if not target_role or target_role not in job_roles_db:
            return jsonify({'error': 'Target role not found'}), 404
        
        required_skills = job_roles_db[target_role]['skills']
        
        # If resume text is provided, extract skills from it
        if resume_text:
            # Simple skill extraction (you can enhance this)
            extracted_skills = []
            for skill in required_skills:
                if skill.lower() in resume_text.lower():
                    extracted_skills.append(skill)
            current_skills = list(set(current_skills + extracted_skills))
        
        # Identify skill gaps
        skill_gaps = []
        current_skills_lower = [s.lower() for s in current_skills]
        
        for skill in required_skills:
            if skill.lower() not in current_skills_lower:
                skill_gaps.append(skill)
        
        # Identify existing skills
        existing_skills = []
        for skill in required_skills:
            if skill.lower() in current_skills_lower:
                existing_skills.append(skill)
        
        # Categorize gaps by priority
        critical_gaps = skill_gaps[:4] if len(skill_gaps) > 4 else skill_gaps
        important_gaps = skill_gaps[4:8] if len(skill_gaps) > 8 else skill_gaps[4:]
        nice_to_have = skill_gaps[8:] if len(skill_gaps) > 8 else []
        
        # Generate learning resources for all skill gaps
        learning_resources = {}
        for skill in critical_gaps + important_gaps:
            learning_resources[skill] = get_learning_resources(skill)
        
        # Calculate completion percentage
        total_skills = len(required_skills)
        matched_skills = len(existing_skills)
        completion_percentage = int((matched_skills / total_skills) * 100) if total_skills > 0 else 0
        
        response_data = {
            'current_skills': current_skills,
            'required_skills': required_skills,
            'existing_skills': existing_skills,
            'skill_gaps': {
                'critical': critical_gaps,
                'important': important_gaps,
                'nice_to_have': nice_to_have
            },
            'learning_resources': learning_resources,
            'completion_percentage': completion_percentage,
            'role_description': job_roles_db[target_role]['description']
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_learning_resources(skill):
    return learning_resources_db.get(skill, {
        "courses": [
            {"name": f"{skill} Fundamentals Course", "platform": "Coursera", "url": "https://www.coursera.org", "level": "Beginner"}
        ],
        "certifications": [
            {"name": f"{skill} Professional Certification", "issuer": "Professional Body", "url": "https://www.example.com"}
        ],
        "youtube": [
            {"name": f"{skill} Tutorial for Beginners", "channel": "Tech Channel", "url": "https://www.youtube.com", "duration": "2:00:00"}
        ]
    })

# Admin routes
@app.route('/api/admin/jobs', methods=['GET'])
def get_admin_jobs():
    return jsonify({'jobs': admin_jobs_db})

@app.route('/api/admin/jobs', methods=['POST'])
def create_job():
    try:
        data = request.json
        new_job = {
            "id": len(admin_jobs_db) + 1,
            "designation": data.get('designation'),
            "category": data.get('category'),
            "salary": data.get('salary'),
            "sort_order": data.get('sort_order', 0),
            "status": data.get('status', 'enabled'),
            "skills": data.get('skills', []),
            "description": data.get('description', '')
        }
        admin_jobs_db.append(new_job)
        return jsonify({'message': 'Job created successfully', 'job': new_job}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    try:
        data = request.json
        for job in admin_jobs_db:
            if job['id'] == job_id:
                job.update({
                    "designation": data.get('designation', job['designation']),
                    "category": data.get('category', job['category']),
                    "salary": data.get('salary', job['salary']),
                    "sort_order": data.get('sort_order', job['sort_order']),
                    "status": data.get('status', job['status']),
                    "skills": data.get('skills', job['skills']),
                    "description": data.get('description', job['description'])
                })
                return jsonify({'message': 'Job updated successfully', 'job': job})
        return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        global admin_jobs_db
        admin_jobs_db = [job for job in admin_jobs_db if job['id'] != job_id]
        return jsonify({'message': 'Job deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/external-resource', methods=['POST'])
def external_resource():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Return the URL for redirection
        return jsonify({'url': url, 'redirect': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------
# 💬 Chatbot API Section
# -----------------------------------------------
# Chatbot Q&A Database
chatbot_responses = {
    "skill_gap_analyzer": {
        "question": "What is a Skill Gap Analyzer?",
        "answer": "A Skill Gap Analyzer identifies the difference between the skills you currently have and the skills required for your target job. It helps you understand what to learn next to become job-ready.",
        "keywords": ["what is", "skill gap", "analyzer", "definition", "explain"]
    },
    "how_it_works": {
        "question": "How does this tool work?",
        "answer": "You simply upload your resume or enter your skills and job role. The analyzer compares them with job market requirements and shows you which skills you need to improve or learn.",
        "keywords": ["how", "work", "process", "function", "operation"]
    },
    "for_students": {
        "question": "Can I use this even if I'm a student?",
        "answer": "Absolutely! The Skill Gap Analyzer is designed for students, freshers, and professionals who want to identify areas for improvement before entering the job market.",
        "keywords": ["student", "fresher", "beginner", "new", "college"]
    },
    "supported_jobs": {
        "question": "What kind of jobs does it support?",
        "answer": "It supports a wide range of roles — from Data Analyst, Software Developer, and UI/UX Designer to Marketing, HR, and Business Analyst positions.",
        "keywords": ["jobs", "roles", "positions", "career", "supported"]
    },
    "gap_identification": {
        "question": "How are skill gaps identified?",
        "answer": "The system compares your current skills (from your resume or input) with key skills from verified job descriptions and industry standards using AI-based matching.",
        "keywords": ["identify", "detect", "find gaps", "matching", "comparison"]
    },
    "after_analysis": {
        "question": "What do I get after analysis?",
        "answer": "You'll receive a personalized report showing your skill strengths, missing skills, and recommended learning paths or online courses to close the gap.",
        "keywords": ["result", "report", "get", "receive", "analysis output"]
    },
    "resume_upload": {
        "question": "Can I upload my resume?",
        "answer": "Yes, you can upload your resume in PDF or DOCX format. The chatbot automatically extracts your skills and experience to perform a detailed analysis.",
        "keywords": ["upload", "resume", "cv", "document", "file"]
    },
    "accuracy": {
        "question": "How accurate is the skill matching?",
        "answer": "The system uses AI-based text extraction and comparison algorithms trained on real job data, ensuring up to 90% accuracy in identifying skill matches.",
        "keywords": ["accurate", "accuracy", "precision", "reliable", "trust"]
    },
    "cost": {
        "question": "Do I need to pay to use this analyzer?",
        "answer": "Currently, it's free to use for basic skill analysis. Premium features like personalized learning suggestions may be added in future versions.",
        "keywords": ["pay", "cost", "price", "free", "premium"]
    },
    "course_recommendations": {
        "question": "Can I get course recommendations to learn missing skills?",
        "answer": "Yes! Once your skill gaps are identified, the chatbot suggests free or paid online courses from trusted platforms like Coursera, Udemy, or LinkedIn Learning.",
        "keywords": ["courses", "learn", "recommendations", "suggestions", "training"]
    },
    "benefits": {
        "question": "What's the benefit of knowing my skill gap?",
        "answer": "Knowing your skill gap helps you focus your learning efforts, prepare better for interviews, and increase your chances of landing your dream job.",
        "keywords": ["benefit", "advantage", "why", "purpose", "help"]
    },
    "data_safety": {
        "question": "Is my data safe here?",
        "answer": "Yes, your data is processed securely and never shared. Uploaded resumes are used only for analysis and not stored permanently.",
        "keywords": ["safe", "security", "privacy", "data", "protect"]
    },
    "multiple_roles": {
        "question": "Can I compare my skills for multiple job roles?",
        "answer": "Yes! You can select multiple job roles to see how your current skillset matches across different positions and choose the best career path.",
        "keywords": ["multiple", "compare", "different", "roles", "positions"]
    },
    "industry_trends": {
        "question": "Does it show industry trends?",
        "answer": "The analyzer can highlight trending skills in your chosen domain, helping you stay updated with current job market demands.",
        "keywords": ["trends", "industry", "market", "trending", "demand"]
    },
    "download_report": {
        "question": "Can I download my skill gap report?",
        "answer": "Yes, you can download your detailed skill gap report as a PDF for future reference or to discuss with mentors or career counselors.",
        "keywords": ["download", "report", "pdf", "save", "export"]
    }
}

greeting_messages = [
    "Hi there! I'm Bob, your Skill Gap Analysis assistant. How can I help you today?",
    "Hello! I'm Bob, here to help you analyze your skills and find the right career path. What would you like to know?",
    "Hey! Bob here, ready to help you with skill analysis and career guidance. What's on your mind?"
]

default_responses = [
    "I'm not sure I understand. Could you rephrase your question?",
    "I specialize in skill gap analysis and career advice.",
    "I'm here to help with skill analysis, resume parsing, and career guidance."
]

@app.route('/api/chatbot/init', methods=['GET'])
def chatbot_init():
    return jsonify({
        'message': random.choice(greeting_messages),
        'default_questions': [q_data['question'] for q_data in chatbot_responses.values()]
    })

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    data = request.json
    user_message = data.get('message', '').lower().strip()

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if any(greet in user_message for greet in ['hi', 'hello', 'hey']):
        return jsonify({
            'response': random.choice(greeting_messages),
            'suggestions': get_suggestions()
        })

    response = find_best_response(user_message)
    if response:
        return jsonify({'response': response, 'suggestions': get_suggestions()})

    return jsonify({'response': random.choice(default_responses), 'suggestions': get_suggestions()})

def find_best_response(user_message):
    best_match = None
    highest_score = 0
    for q_data in chatbot_responses.values():
        score = sum(1 for kw in q_data['keywords'] if kw in user_message)
        if score > highest_score:
            highest_score = score
            best_match = q_data['answer']
    return best_match if highest_score >= 1 else None

def get_suggestions():
    return [
        "How does skill gap analysis work?",
        "Can I upload my resume?",
        "What jobs are supported?",
        "Show me course recommendations"
    ]

# ✅ PRODUCTION-READY MAIN BLOCK
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
 

  
 
# Get active job roles for frontend dropdown
@app.route('/api/active-job-roles', methods=['GET'])
def get_active_job_roles():
    try:
        # Get only enabled jobs from admin_jobs_db
        active_jobs = [job for job in admin_jobs_db if job.get('status') == 'enabled']
        
        # Convert to the format expected by frontend
        job_roles = {}
        for job in active_jobs:
            job_roles[job['designation']] = {
                'skills': job.get('skills', []),
                'description': job.get('description', '')
            }
        
        return jsonify(job_roles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500