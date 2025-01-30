<div align="center">
  
# ⚙️  **Refactory**  ⚙️
AI 기반 코드 리뷰 자동화 솔루션  

</div>

---

## 📖 목차  
- [서비스 소개](#-서비스-소개)  
- [주요 기능](#-주요-기능)  
- [Demo](#-demo)  
- [Medium 링크](#-medium)  
- [시스템 아키텍처](#-시스템-아키텍처)  
- [ERD](#-erd)  
- [기술 스택](#-기술-스택)  
- [API](#-api)  
- [How to use?](#-how-to-use)  
- [팀원 소개](#-팀원-소개)  

---

## 🏭 서비스 소개  
Refactory는 AI를 활용하여 자동화된 코드 리뷰를 제공함으로써 코드의 품질을 높이고 유지보수를 간편하게 합니다.  

---

## 🐈 주요 기능  
- **GitHub 연동**:  
  - GitHub PR 자동 분석 및 리뷰 제공  
  - 리뷰 모드 자동 선택  

- **리뷰 모드**:  
  - **Clean mode**: 클린 코드 원칙을 중심으로 리뷰  
  - **Optimize mode**: 성능과 효율성을 중심으로 리뷰  
  - **Basic mode**: 초보 개발자를 위한 기본 개선 사항 및 리뷰
  - **Newbie mode**: 쉬운 언어로 작성된 간단한 리뷰
  - **Study mode**: 학습자 성장을 돕기 위한 심층 분석 및 리뷰

- **PR 리뷰 생성**:  
  AI가 작성한 모드 별 리뷰와 개선 사항 제공
  코드 품질과 성능을 점수화하여 제공

- **리뷰 내역 시각화 제공**:  
  결과를 토대로 시각화 그래프 제공

- **보고서 작성**:
  리뷰 받은 PR들을 바탕으로 보고서 작성 및 pdf 파일 제공

- **부분 코드 리뷰**:
  드래그를 통한 실시간 부분 코드 리뷰 기능 제공

---
## 📈 Demo
- **메인 기능 페이지**
<div align="center">
  
| 대시보드 | 히스토리 |
|:--------:|:--------:|
| <img src="https://github.com/user-attachments/assets/55986d52-2b9f-4fa6-af52-45d815411d07" width="400" height="250"> | <img src="https://github.com/user-attachments/assets/ba4011f9-c317-47f1-9f5b-ecaa3c7a47f5" width="400" height="250"> |
| **레포지토리** | **리포트** |
| <img src="https://github.com/user-attachments/assets/7a8a7476-12d4-40f0-80e6-78a7989ec430" width="400" height="250"> | <img src="https://github.com/user-attachments/assets/d710a46d-3b19-4e1a-b948-89c4a59da813" width="400" height="250"> |



</div>
  
- **Github Login**
<div align="center">

![깃허브 로그인](https://github.com/user-attachments/assets/b946c5c0-9146-4340-a0ca-296dcbdd7629)

</div>

- **코드 리뷰**
<div align="center">

| 머지 차단 clean mode | 머지 가능 optimize mode |
|:--------:|:--------:|
| <img src="https://github.com/user-attachments/assets/ed7369dc-9436-4a0c-ba71-34bf92488e55" width="400" height="200"> | <img src="https://github.com/user-attachments/assets/3b3cc250-37e0-4308-9ec7-e89b389a798a" width="400" height="200"> |

</div>

- **데이터 시각화**
<div align="center">

| 이슈 타입 그래프 | 히스토리 그래프 |
|:--------:|:--------:|
| <img src="https://github.com/user-attachments/assets/9d978b6c-943f-4ac3-bacc-0f6ea901399a" width="300" height="200"> | <img src="https://github.com/user-attachments/assets/29f89405-9b92-4eef-a102-7cd6163f622f" width="300" height="200"> |

| 평균 등급 그래프 |
|:--------:|
| <img src="https://github.com/user-attachments/assets/95dab837-3fcd-49e5-a991-ca844a986609" width="500"> |

</div>

- **보고서 생성**
<div align="center">

| 보고서 생성 | 보고서 내용 |
|:--------:|:--------:|
| <img src="https://github.com/user-attachments/assets/ca294bb3-d370-466c-923e-89d653edd48d" width="400" height="200"> | <img src="https://github.com/user-attachments/assets/cbf28554-fb34-4ab1-929f-a01815fe34e4" width="400" height="200"> |

</div>
  
- **부분 코드 리뷰**
  
<div align="center">

![부분 코드 리뷰 (2)](https://github.com/user-attachments/assets/f2aca9e7-b7c7-4165-99e3-104969cb6d3d)

</div>

---
## 🐳 Medium  


---

## 🛠 시스템 아키텍처  
<div align="center">

<img width="1105" alt="arcitecture" src="https://github.com/user-attachments/assets/8ee9a536-c623-4db0-affc-f5100a1744d6" />

</div>

---

## 🔑 ERD  
<div align="center">

![image](https://github.com/user-attachments/assets/08bb8ccc-3c6b-46b0-aafb-e0fea64485f0)

</div>

---

## 💻 기술 스택  
| 카테고리          | 기술 스택                                       |  
|:-------------------:|:------------------------------------------------:|  
| **Frontend**     | ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![Styled Components](https://img.shields.io/badge/styled--components-DB7093?style=for-the-badge&logo=styled-components&logoColor=white)  |
| **Backend**         | ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white) ![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=ddf4a4) ![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white) |  
| **DevOps**           | ![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white) ![Deepseek](https://i.imgur.com/ejWPMAl.png)| 
| **Mornitoring**       | ![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white) ![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white) ![cAdvisor](https://i.imgur.com/vO6QYSK.png) ![Node Exporter](https://img.shields.io/badge/Node%20Exporter-orange?style=for-the-badge&logo=prometheus&logoColor=white) |  
| **Additional**           | ![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white) ![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white) ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) ![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white) ![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white) ![Zoom](https://img.shields.io/badge/Zoom-2D8CFF?style=for-the-badge&logo=zoom&logoColor=white) ![Visual Studio Code](https://i.imgur.com/YeY3dpQ.png) ![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green) |  

---

## 📗 API  
<div align="center">
  
![스크린샷 2025-01-29 오전 2 16 06](https://github.com/user-attachments/assets/f2195bf8-4823-4062-8a70-203f8e59338a)

</div>

---
## 🤔 How to use?

**Backend**
```bash
# clone our project
git clone https://github.com/2024-Winter-BootCamp-TeamD/review-Backend.git
```

```bash
# Create the .env file in main directory

#mysql 설정
MYSQL_DATABASE=<YOUR_MYSQL_DATABASE>
MYSQL_USER=<YOUR_MYSQL_USER>
MYSQL_ROOT_USER=<YOUR_MYSQL_ROOT_USER>
MYSQL_PASSWORD=<YOUR_MYSQL_PASSWORD>
MYSQL_ROOT_PASSWORD=<YOUR_MYSQL_ROOT_PASSWORD>

RABBITMQ_DEFAULT_USER='<YOUR_RABBITMQ_USER>'
RABBITMQ_DEFAULT_PASS='<YOUR_RABBITMQ_PASSWORD>'

# github oauth 설정
GITHUB_CLIENT_ID = '<YOUR_GITHUB_CLIENT_ID>'
GITHUB_CLIENT_SECRET = '<YOUR_GITHUB_CLIENT_SECRET>'
GITHUB_REDIRECT_URI = ' '  # 예: http://localhost:8000/oauth/callback/

# 로컬 환경에서 웹훅 수신 테스트를 위해 ngork을 이용한 프록시 서버 사용
GITHUB_WEBHOOK_URL = ' '  # 로컬에서 테스트 중인 웹훅 수신 URL

DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>
DEEPSEEK_API_URL=' ' # DeepSeek API 요청을 보낼 기본 URL

# S3 Configuration
AWS_ACCESS_KEY_ID= '<YOUR_AWS_ACCESS_KEY>'
AWS_SECRET_ACCESS_KEY= '<YOUR_AWS_SECRET_KEY>'
AWS_STORAGE_BUCKET_NAME= # S3에서 사용할 버킷의 이름 (파일 업로드 및 저장에 사용)
AWS_S3_REGION_NAME= # S3 버킷이 위치한 AWS 리전

DEPLOY_GITHUB_CLIENT_ID = '<YOUR_GITHUB_CLIENT_ID>'
DEPLOY_GITHUB_CLIENT_SECRET = '<YOUR_GITHUB_CLIENT_SECRET>'
DEPLOY_GITHUB_REDIRECT_URI = ' ' # GitHub 로그인 후 사용자를 리디렉션할 URI (OAuth 인증 과정에서 GitHub가 이 URL로 응답을 보냄)

```

```bash
# build docker
docker compose up -d --build
```

**Frontend**
```bash
# clone our project
git clone https://github.com/2024-Winter-BootCamp-TeamD/review-Frontend.git
```

```bash
npm i
npm run build
```

---
## 👨‍💻 팀원 소개  
<div align="center">

|            | **서지민**   | **김윤성**   | **장원진**   | **김규리**   | **김아인**   | **류정훈**   | **이융현**   |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
| **Profile** | <img src="https://github.com/user-attachments/assets/43627a8f-4049-4ce5-8c75-5d483b1461d9" width="100" height="100"> | <img src="https://github.com/user-attachments/assets/8a558c12-e4db-49b8-998e-71ce761f81fe" width="100" height="100"> | <img src="https://github.com/user-attachments/assets/3fe09797-881d-49ea-a443-f8ee66d1cab9" width="100" height="100"> | <img src="https://github.com/user-attachments/assets/c0e876e9-dbf5-46e4-b96d-0e5c716dcca5" width="100" height="100"> | <img src="https://github.com/user-attachments/assets/cfcf01e5-9c54-4091-8f26-62854ff83c89" width="100" height="100"> | <img src="https://github.com/user-attachments/assets/0053ff1c-3d52-4104-ba0e-9a25fc19703a" width="100" height="100"> | <img src="https://github.com/user-attachments/assets/5599d89d-a23d-4ca5-9a83-8a2ba0850698" width="100" height="100"> |
| **Role**   | **Team Leader**<br>Frontend<br>UI/UX<br>DevOps | Frontend<br>UI/UX | Frontend<br>UI/UX | Backend | Backend | Backend | Backend |
| **GitHub** | [@Lauiee    ](https://github.com/Lauiee) | [@Nekerworld ](https://github.com/Nekerworld) | [@wonjinjang ](https://github.com/wonjinjang) | [@gyuri224   ](https://github.com/gyuri224) | [@einhn](https://github.com/einhn) | [@RYUJEONGHUN](https://github.com/RYUJEONGHUN) | [@fostacion  ](https://github.com/fostacion) |

</div>

---
