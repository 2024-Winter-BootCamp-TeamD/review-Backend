<div align="center">
  
# ⚙️  **Refactory**  ⚙️
AI 기반 코드 리뷰 자동화 솔루션  

</div>

---

## 📖 목차  
- 서비스 소개  
- 주요 기능
- Demo
- Medium 링크  
- 시스템 아키텍처  
- ERD  
- 기술 스택  
- API
- How to use?
- 팀원 소개  

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
## 📈Demo
- **메인 페이지**
- **Github Login**
- **코드 리뷰**
- **데이터 시각화**
- **보고서 생성**
- **부분 코드 리뷰**

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
|-------------------|------------------------------------------------|  
| **Frontend**     | ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white) ![Styled Components](https://img.shields.io/badge/styled--components-DB7093?style=for-the-badge&logo=styled-components&logoColor=white)  |
| **Backend**         | ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white) ![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=ddf4a4) ![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white) |  
| **DevOps**           | ![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white) ![Deepseek](https://img.shields.io/badge/deepseek-143?style=for-the-badge&logo=deepseek&logoColor=white&color=blue)| 
| **Mornitoring**       | ![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white) ![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)  |  
| **기타**           | ![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white) ![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white) ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) ![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white) ![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white) ![Zoom](https://img.shields.io/badge/Zoom-2D8CFF?style=for-the-badge&logo=zoom&logoColor=white) ![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white) ![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green) |  

---

## 📗 API  
<div align="center">
  
![스크린샷 2025-01-29 오전 2 16 06](https://github.com/user-attachments/assets/f2195bf8-4823-4062-8a70-203f8e59338a)

</div>

---
## 🤔 How to use?
```bash
# clone our project
git clone -b develop --single-branch
```
```bash
# Create the .env file
```
```bash
# build docker
docker compose up -d --build
```
---
## 👨‍💻 팀원 소개  
<div align="center">

|            | **서지민**   | **김윤성**   | **장원진**   | **김규리**   | **김아인**   | **류정훈**   | **이융현**   |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
| **Profile** | |  |  || | | |
| **Role**   | **Team Leader**<br>Frontend<br>UI/UX<br>DevOps | Frontend<br>UI/UX | Frontend<br>UI/UX | Backend<br>DevOps | Backend<br>DevOps | Backend<br>DevOps | Backend<br>DevOps |
| **GitHub** | [@Lauiee](https://github.com/Lauiee) | [@Nekerworld](https://github.com/Nekerworld) | [@wonjinjang](https://github.com/wonjinjang) | [@gyuri224](https://github.com/gyuri224) | [@einhin](https://github.com/einhn) | [@RYUJEONGHUN](https://github.com/RYUJEONGHUN) | [@fostacion](https://github.com/fostacion) |

</div>

---
