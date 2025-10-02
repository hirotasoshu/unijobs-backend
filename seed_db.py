import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId, VacancyId
from src.domain.value_object.workformat import WorkFormat
from src.infra.adapters.database.models import (
    Base,
    EmployerModel,
    VacancyModel,
    LocalizedString,
)

# Локализованные данные для работодателей
mock_employers = [
    {
        "id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
        "name": LocalizedString(
            en="Ural Federal University", ru="УрФУ", fr="Université fédérale de l'Oural"
        ),
        "avatar_url": "https://urfu.ru/fileadmin/user_upload/common_files/brand/svg/Logotip_UrFU_Znak.svg",
        "description": LocalizedString(
            en="""Ural Federal University is the largest university in the Urals, a leading scientific and educational center in the region and one of the largest universities in the Russian Federation.
In 2023, the university ranked 3rd in the Ranking of the Largest Universities in Russia and 12th in Russia in terms of the number of foreign students.""",
            ru="""Уральский федеральный университет является крупнейшим вузом Урала, ведущим научно-образовательным центром региона и одним из крупнейших вузов Российской Федерации.
В 2023 году университет занял 3 место в Рейтинге крупнейших университетов России и 12 место в России по количеству иностранных студентов.""",
            fr="""L'Université fédérale de l'Oural est la plus grande université de l'Oural, le principal centre scientifique et éducatif de la région et l'une des plus grandes universités de la Fédération de Russie.""",
        ),
    },
    {
        "id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
        "name": LocalizedString(
            en="HSE St. Petersburg", ru="ВШЭ СПБ", fr="HSE Saint-Pétersbourg"
        ),
        "avatar_url": "https://papik.pro/grafic/uploads/posts/2023-04/1681593331_papik-pro-p-niu-vshe-logotip-vektor-6.jpg",
        "description": LocalizedString(
            en="""National Research University Higher School of Economics is an autonomous institution, a federal state higher educational institution.""",
            ru="""Национальный исследовательский университет «Высшая школа экономики» — автономное учреждение, федеральное государственное высшее учебное заведение.""",
            fr="""L'Université nationale de recherche «École supérieure d'économie» est un établissement autonome, un établissement fédéral d'enseignement supérieur.""",
        ),
    },
]

# Локализованные данные для вакансий
mock_vacancies = [
    {
        "id": VacancyId(UUID("01960c29-a1b3-11e5-bb77-1234567890f1")),
        "title": LocalizedString(
            en="Python Developer", ru="Python разработчик", fr="Développeur Python"
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 80000,
        "salary_to": 120000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development of web applications and APIs using Python and Django framework.",
            ru="Разработка веб-приложений и API с использованием Python и фреймворка Django.",
            fr="Développement d'applications web et d'API utilisant Python et le framework Django.",
        ),
        "key_skills": ["Python", "Django", "REST API", "PostgreSQL", "Docker"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-b2c4-11e5-bb77-1234567890f2")),
        "title": LocalizedString(
            en="Data Analyst", ru="Аналитик данных", fr="Analyste de données"
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 70000,
        "salary_to": 100000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Data analysis and visualization, creating reports and dashboards.",
            ru="Анализ данных и визуализация, создание отчетов и дашбордов.",
            fr="Analyse et visualisation des données, création de rapports et tableaux de bord.",
        ),
        "key_skills": ["SQL", "Python", "Tableau", "Excel", "Statistics"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-c3d5-11e5-bb77-1234567890f3")),
        "title": LocalizedString(
            en="DevOps Engineer", ru="DevOps инженер", fr="Ingénieur DevOps"
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 100000,
        "salary_to": 150000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Infrastructure management, CI/CD pipelines, and cloud services administration.",
            ru="Управление инфраструктурой, настройка CI/CD пайплайнов и администрирование облачных сервисов.",
            fr="Gestion de l'infrastructure, configuration des pipelines CI/CD et administration des services cloud.",
        ),
        "key_skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-d4e6-11e5-bb77-1234567890f4")),
        "title": LocalizedString(
            en="Frontend Developer",
            ru="Frontend разработчик",
            fr="Développeur Frontend",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 90000,
        "salary_to": 130000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development of user interfaces using modern JavaScript frameworks.",
            ru="Разработка пользовательских интерфейсов с использованием современных JavaScript фреймворков.",
            fr="Développement d'interfaces utilisateur avec des frameworks JavaScript modernes.",
        ),
        "key_skills": ["JavaScript", "React", "TypeScript", "HTML/CSS", "Webpack"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-e5f7-11e5-bb77-1234567890f5")),
        "title": LocalizedString(
            en="Database Administrator",
            ru="Администратор баз данных",
            fr="Administrateur de base de données",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 85000,
        "salary_to": 110000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Database management, optimization, and performance monitoring.",
            ru="Управление базами данных, оптимизация и мониторинг производительности.",
            fr="Gestion des bases de données, optimisation et surveillance des performances.",
        ),
        "key_skills": ["PostgreSQL", "MySQL", "MongoDB", "SQL", "Performance Tuning"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-f708-11e5-bb77-1234567890f6")),
        "title": LocalizedString(
            en="Machine Learning Engineer",
            ru="Инженер машинного обучения",
            fr="Ingénieur en apprentissage automatique",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 120000,
        "salary_to": 180000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development and implementation of machine learning models and algorithms.",
            ru="Разработка и внедрение моделей и алгоритмов машинного обучения.",
            fr="Développement et mise en œuvre de modèles et algorithmes d'apprentissage automatique.",
        ),
        "key_skills": [
            "Python",
            "TensorFlow",
            "PyTorch",
            "scikit-learn",
            "Deep Learning",
        ],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-0819-11e5-bb77-1234567890f7")),
        "title": LocalizedString(
            en="System Administrator",
            ru="Системный администратор",
            fr="Administrateur système",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 60000,
        "salary_to": 90000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Server administration, network management, and technical support.",
            ru="Администрирование серверов, управление сетями и техническая поддержка.",
            fr="Administration de serveurs, gestion de réseau et support technique.",
        ),
        "key_skills": [
            "Linux",
            "Windows Server",
            "Networking",
            "Bash",
            "Virtualization",
        ],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-192a-11e5-bb77-1234567890f8")),
        "title": LocalizedString(
            en="Mobile App Developer",
            ru="Разработчик мобильных приложений",
            fr="Développeur d'applications mobiles",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 95000,
        "salary_to": 140000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development of cross-platform mobile applications.",
            ru="Разработка кроссплатформенных мобильных приложений.",
            fr="Développement d'applications mobiles multiplateformes.",
        ),
        "key_skills": ["React Native", "Flutter", "JavaScript", "iOS", "Android"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-2a3b-11e5-bb77-1234567890f9")),
        "title": LocalizedString(
            en="QA Automation Engineer",
            ru="Инженер по автоматизации тестирования",
            fr="Ingénieur en automatisation des tests",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 75000,
        "salary_to": 110000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development of automated test scripts and test frameworks.",
            ru="Разработка автоматизированных тестовых скриптов и фреймворков тестирования.",
            fr="Développement de scripts de test automatisés et de frameworks de test.",
        ),
        "key_skills": ["Selenium", "Python", "Jenkins", "TestNG", "API Testing"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-3b4c-11e5-bb77-1234567890fa")),
        "title": LocalizedString(
            en="Cloud Solutions Architect",
            ru="Архитектор облачных решений",
            fr="Architecte de solutions cloud",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 130000,
        "salary_to": 200000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Design and implementation of cloud infrastructure solutions.",
            ru="Проектирование и внедрение решений облачной инфраструктуры.",
            fr="Conception et mise en œuvre de solutions d'infrastructure cloud.",
        ),
        "key_skills": ["AWS", "Azure", "Terraform", "Kubernetes", "Microservices"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-20de-71a1-a4e7-509120b6527f")),
        "title": LocalizedString(
            en="Teaching Assistant",
            ru="Ассистент преподавателя",
            fr="Assistant d'enseignement",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 20000,
        "salary_to": 30000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.PART_TIME,
        "description": LocalizedString(
            en="Vacancy description for teaching assistant in Yekaterinburg.",
            ru="Описание вакансии для ассистент преподавателя в Екатеринбург.",
            fr="Description du poste pour assistant d'enseignement à Iekaterinbourg.",
        ),
        "key_skills": ["Python", "Microsoft office", "Excel"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-8f45-771d-a8d6-2a9b1ca9a86d")),
        "title": LocalizedString(
            en="Administrative Assistant",
            ru="Административный помощник",
            fr="Assistant administratif",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 25000,
        "salary_to": 35000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Vacancy description for administrative assistant in Saint Petersburg.",
            ru="Описание вакансии для административный помощник в Санкт-Петербург.",
            fr="Description du poste pour assistant administratif à Saint-Pétersbourg.",
        ),
        "key_skills": ["Communication", "Microsoft office", "excel"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-c88c-7104-969f-566213debd7f")),
        "title": LocalizedString(
            en="IT Department Intern",
            ru="Стажёр в ИТ-отдел",
            fr="Stagiaire en département IT",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 15000,
        "salary_to": 20000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.INTERNSHIP,
        "description": LocalizedString(
            en="Vacancy description for IT department intern in Yekaterinburg.",
            ru="Описание вакансии для стажёр в ИТ-отдел в Екатеринбург.",
            fr="Description du poste pour stagiaire en département IT à Iekaterinbourg.",
        ),
        "key_skills": ["Windows", "Linux", "Microsoft office"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-dfd4-7433-9a41-d86f152cb50f")),
        "title": LocalizedString(
            en="Research Intern", ru="Исследователь-стажёр", fr="Stagiaire chercheur"
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 10000,
        "salary_to": 15000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.INTERNSHIP,
        "description": LocalizedString(
            en="Vacancy description for research intern in Saint Petersburg.",
            ru="Описание вакансии для исследователь-стажёр в Санкт-Петербург.",
            fr="Description du poste pour stagiaire chercheur à Saint-Pétersbourg.",
        ),
        "key_skills": ["Python", "R", "Matlab"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-1a2b-11e5-bb77-1234567890c4")),
        "title": LocalizedString(
            en="Educational Programs Coordinator",
            ru="Куратор учебных программ",
            fr="Coordinateur des programmes éducatifs",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 30000,
        "salary_to": 40000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Vacancy description for educational programs coordinator in Yekaterinburg.",
            ru="Описание вакансии для куратор учебных программ в Екатеринбург.",
            fr="Description du poste pour coordinateur des programmes éducatifs à Iekaterinbourg.",
        ),
        "key_skills": ["Office", "Windows", "Excel"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-2b3c-11e5-bb77-1234567890c5")),
        "title": LocalizedString(
            en="Student Projects Manager",
            ru="Менеджер по студенческим проектам",
            fr="Manager des projets étudiants",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 32000,
        "salary_to": 42000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Vacancy description for student projects manager in Saint Petersburg.",
            ru="Описание вакансии для менеджер по студенческим проектам в Санкт-Петербург.",
            fr="Description du poste pour manager des projets étudiants à Saint-Pétersbourg.",
        ),
        "key_skills": ["Event-management", "Microsoft office", "Excel"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-4c5d-11e5-bb77-1234567890fb")),
        "title": LocalizedString(
            en="Full Stack Developer",
            ru="Full Stack разработчик",
            fr="Développeur Full Stack",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 95000,
        "salary_to": 140000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development of end-to-end web applications from frontend to backend.",
            ru="Разработка полнофункциональных веб-приложений от фронтенда до бэкенда.",
            fr="Développement d'applications web complètes du frontend au backend.",
        ),
        "key_skills": ["JavaScript", "Node.js", "React", "PostgreSQL", "Express.js"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-5d6e-11e5-bb77-1234567890fc")),
        "title": LocalizedString(
            en="Cyber Security Specialist",
            ru="Специалист по кибербезопасности",
            fr="Spécialiste en cybersécurité",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 110000,
        "salary_to": 160000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Network security monitoring, vulnerability assessment and penetration testing.",
            ru="Мониторинг сетевой безопасности, оценка уязвимостей и тестирование на проникновение.",
            fr="Surveillance de la sécurité réseau, évaluation des vulnérabilités et tests de pénétration.",
        ),
        "key_skills": [
            "SIEM",
            "Penetration Testing",
            "Firewalls",
            "Kali Linux",
            "OWASP",
        ],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-6e7f-11e5-bb77-1234567890fd")),
        "title": LocalizedString(
            en="Data Engineer", ru="Инженер данных", fr="Ingénieur de données"
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 100000,
        "salary_to": 150000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Design and maintenance of data pipelines and ETL processes.",
            ru="Проектирование и сопровождение данных пайплайнов и ETL процессов.",
            fr="Conception et maintenance des pipelines de données et processus ETL.",
        ),
        "key_skills": ["Apache Spark", "Python", "SQL", "Airflow", "Hadoop"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-7f90-11e5-bb77-1234567890fe")),
        "title": LocalizedString(
            en="UI/UX Designer", ru="UI/UX дизайнер", fr="Designer UI/UX"
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 80000,
        "salary_to": 120000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Creating user-centered designs and interactive prototypes.",
            ru="Создание пользовательских интерфейсов и интерактивных прототипов.",
            fr="Création de conceptions centrées sur l'utilisateur et de prototypes interactifs.",
        ),
        "key_skills": ["Figma", "Adobe XD", "Sketch", "Prototyping", "User Research"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-90a1-11e5-bb77-1234567890ff")),
        "title": LocalizedString(
            en="Java Backend Developer",
            ru="Java Backend разработчик",
            fr="Développeur Backend Java",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 90000,
        "salary_to": 130000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Development of high-performance backend services using Java technologies.",
            ru="Разработка высокопроизводительных бэкенд-сервисов с использованием Java технологий.",
            fr="Développement de services backend hautes performances utilisant les technologies Java.",
        ),
        "key_skills": ["Java", "Spring Boot", "Hibernate", "Maven", "REST API"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-a1b2-11e5-bb77-123456789100")),
        "title": LocalizedString(
            en="Business Intelligence Analyst",
            ru="Аналитик бизнес-аналитики",
            fr="Analyste en business intelligence",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 85000,
        "salary_to": 125000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Creating dashboards and reports for business decision making.",
            ru="Создание дашбордов и отчетов для принятия бизнес-решений.",
            fr="Création de tableaux de bord et de rapports pour la prise de décision commerciale.",
        ),
        "key_skills": ["Power BI", "Tableau", "SQL", "Excel", "Data Visualization"],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-b2c3-11e5-bb77-123456789101")),
        "title": LocalizedString(
            en="Network Engineer", ru="Сетевой инженер", fr="Ingénieur réseau"
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 70000,
        "salary_to": 100000,
        "work_format": WorkFormat.ONSITE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Design, implementation and maintenance of network infrastructure.",
            ru="Проектирование, внедрение и обслуживание сетевой инфраструктуры.",
            fr="Conception, mise en œuvre et maintenance de l'infrastructure réseau.",
        ),
        "key_skills": ["Cisco", "TCP/IP", "VPN", "Routing", "Switching"],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-c3d4-11e5-bb77-123456789102")),
        "title": LocalizedString(
            en="Technical Writer", ru="Технический писатель", fr="Rédacteur technique"
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 60000,
        "salary_to": 90000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Creating technical documentation and user manuals for software products.",
            ru="Создание технической документации и руководств пользователя для программных продуктов.",
            fr="Création de documentation technique et de manuels utilisateur pour les produits logiciels.",
        ),
        "key_skills": [
            "Technical Writing",
            "Markdown",
            "Git",
            "API Documentation",
            "Confluence",
        ],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
    {
        "id": VacancyId(UUID("01960c29-d4e5-11e5-bb77-123456789103")),
        "title": LocalizedString(
            en="Site Reliability Engineer",
            ru="Инженер надежности сайтов",
            fr="Ingénieur de fiabilité des sites",
        ),
        "location": LocalizedString(
            en="Yekaterinburg", ru="Екатеринбург", fr="Iekaterinbourg"
        ),
        "salary_from": 110000,
        "salary_to": 170000,
        "work_format": WorkFormat.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Ensuring system reliability, performance and monitoring.",
            ru="Обеспечение надежности, производительности и мониторинга систем.",
            fr="Assurer la fiabilité, les performances et la surveillance des systèmes.",
        ),
        "key_skills": [
            "Prometheus",
            "Grafana",
            "Linux",
            "Python",
            "Incident Management",
        ],
        "employer_id": EmployerId(UUID("01960c2a-5ad1-7651-80bf-54760bd9d55a")),
    },
    {
        "id": VacancyId(UUID("01960c29-e5f6-11e5-bb77-123456789104")),
        "title": LocalizedString(
            en="Microsoft 365 Administrator",
            ru="Администратор Microsoft 365",
            fr="Administrateur Microsoft 365",
        ),
        "location": LocalizedString(
            en="Saint Petersburg", ru="Санкт-Петербург", fr="Saint-Pétersbourg"
        ),
        "salary_from": 65000,
        "salary_to": 95000,
        "work_format": WorkFormat.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "description": LocalizedString(
            en="Management and administration of Microsoft 365 services and applications.",
            ru="Управление и администрирование сервисов и приложений Microsoft 365.",
            fr="Gestion et administration des services et applications Microsoft 365.",
        ),
        "key_skills": [
            "Microsoft 365",
            "PowerShell",
            "SharePoint",
            "Exchange Online",
            "Azure AD",
        ],
        "employer_id": EmployerId(UUID("01960c2a-9938-74ff-8fe1-027402ef0b9b")),
    },
]


async def seed():
    engine = create_async_engine(
        "sqlite+aiosqlite:////home/hirotasoshu/code/unijobs-backend/test.db",
        echo=True,
    )
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Employers
        for e in mock_employers:
            session.add(
                EmployerModel(
                    id=e["id"],
                    name=e["name"],
                    avatar_url=e["avatar_url"],
                    description=e["description"],
                )
            )

        # Vacancies
        for v in mock_vacancies:
            session.add(
                VacancyModel(
                    id=v["id"],
                    title=v["title"],
                    location=v["location"],
                    salary_from=v["salary_from"],
                    salary_to=v["salary_to"],
                    work_format=v["work_format"],
                    employment_type=v["employment_type"],
                    description=v["description"],
                    key_skills=",".join(v["key_skills"]),
                    employer_id=v["employer_id"],
                )
            )

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
