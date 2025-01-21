import logging
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import Report, ReportPrReview
from pullrequest.models import PRReview
from django.core.paginator import Paginator
from dotenv import load_dotenv
import requests
from io import BytesIO
from django.http import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
import os

# 폰트 경로 설정
FONT_PATH_REGULAR = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf')
FONT_PATH_BOLD = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothicBold.ttf')

# 폰트 파일 존재 여부 확인
if not os.path.exists(FONT_PATH_REGULAR):
    raise FileNotFoundError(f"Regular 폰트 파일을 찾을 수 없습니다: {FONT_PATH_REGULAR}")
if not os.path.exists(FONT_PATH_BOLD):
    raise FileNotFoundError(f"Bold 폰트 파일을 찾을 수 없습니다: {FONT_PATH_BOLD}")

# 폰트 등록
pdfmetrics.registerFont(TTFont('NanumGothic', FONT_PATH_REGULAR))  # Regular 폰트 등록
pdfmetrics.registerFont(TTFont('NanumGothic-Bold', FONT_PATH_BOLD))  # Bold 폰트 등록

# 스타일 설정
styles = getSampleStyleSheet()
styles['Normal'].fontName = 'NanumGothic'
styles['Heading1'].fontName = 'NanumGothic-Bold'
styles['Heading2'].fontName = 'NanumGothic-Bold'
styles['BodyText'].fontName = 'NanumGothic'

load_dotenv()
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")

class UserReportAPIView(APIView):
    def get(self, request, user_id):
        try:
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 10))

            reports = Report.objects.filter(user_id=user_id, is_deleted=False).order_by('-created_at')
            paginator = Paginator(reports, size)
            paginated_reports = paginator.get_page(page)

            response_data = {
                "total_count": paginator.count,
                "reports": [
                    {
                        "report_id": report.report_id,
                        "title": report.title,
                        "content": report.content,
                        "pdf_url": report.pdf_url,
                        "review_num": report.review_num,
                        "is_deleted": report.is_deleted,
                        "created_at": report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "updated_at": report.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    for report in paginated_reports
                ]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"보고서 목록 조회 중 오류 발생: {e}")
            return Response({"error_message": "보고서 목록 조회 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def generate_report_with_deepseek(title, pr_reviews):
        """
        DeepSeek API를 이용하여 보고서 내용을 생성하는 함수
        :param title: 보고서 제목
        :param pr_reviews: PR 리뷰 데이터 리스트
        :return: 구조화된 딕셔너리 형태의 보고서 내용
        """
        # PR 리뷰 데이터를 테이블 형식으로 변환
        pr_table_rows = [
            {"id": pr['id'], "title": pr['title'], "aver_grade": pr['aver_grade'], "problem_type": pr['problem_type'], "review_mode": pr['review_mode'], "created_at": pr['created_at']}
            for pr in pr_reviews
        ]

        # PR 데이터 요약
        total_prs = len(pr_reviews)
        clean_mode_count = sum(1 for pr in pr_reviews if pr['review_mode'] == 'clean')
        optimize_mode_count = sum(1 for pr in pr_reviews if pr['review_mode'] == 'optimize')
        study_mode_count = sum(1 for pr in pr_reviews if pr['review_mode'] == 'study')
        newbie_mode_count = sum(1 for pr in pr_reviews if pr['review_mode'] == 'newbie')
        basic_mode_count = sum(1 for pr in pr_reviews if pr['review_mode'] == 'basic')

        # DeepSeek API 프롬프트 생성
        prompt = f"""
        # 리뷰 종합 보고서 생성 요청

        아래 양식에 맞추어 보고서를 생성해주세요.

        ---

        **2-1. 리뷰 결과 통계**

        - **분석된 PR 수**: {total_prs}
        - **Clean 모드**: {clean_mode_count}개의 리뷰
        - **Optimize 모드**: {optimize_mode_count}개의 리뷰
        - **Study 모드**: {study_mode_count}개의 리뷰
        - **newbie 모드**: {newbie_mode_count}개의 리뷰
        - **basic 모드**: {basic_mode_count}개의 리뷰

        ---

        **2-2. 주요 취약점 및 개선 우선순위**

        **취약한 유형 통계 및 개선 방향**:
        - 각 PR 리뷰에서 지적된 취약점을 분석하고, 취약점의 분포를 표시하세요.
        - 가능한 경우, 다음과 같은 세부 사항을 포함하세요:
          - **취약점 유형 문제점**
          - **개선 방향**
          - **안좋은 예시와 좋은 예시**

        ---

        **2-3. 개인화된 피드백 및 권장사항**

        **사용자 맞춤 개선 방향**:
        - 가장 낮은 점수를 받은 평가 기준을 기반으로, 사용자 맞춤 피드백을 작성하세요.
        - 취약점을 잘 보완할 수 있는 보편적 개선안을 세세하게 출력해주세요.

        ---

        **2-4. 종합 결론**

        - **총평**:
          - 프로젝트의 전체적 성향 및 평균 등급을 출력하고 ~~부분에서 개선 여지가 가장 크다 라는 식의 독려하는 말투로 취약점 개선에 힘을 실어주세요.
            - **강점**: 프로젝트 또는 코드의 긍정적인 점을 3개 이상 작성하세요.
            - **약점**: 코드에서 개선이 필요한 점을 3개 이상 작성하세요.
            - **향후 권장 사항**:
          - ~~모드를 사용하며 사용자가 키워야 할 역량에 대해 알려주세요..

        ---

        **첨부 자료**

        - 추천 학습 자료
        - 관련 예시 코드
        """

        # DeepSeek API 요청
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": prompt}],
            "stream": False,
        }

        try:
            response = requests.post(f"{DEEPSEEK_API_URL}", json=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()
            logger.debug(f"DeepSeek API 응답: {response_data}")

            # API 응답에서 데이터 추출
            content = response_data["choices"][0]["message"]["content"]

            # 구조화된 딕셔너리 생성
            structured_content = {
                "title": title,
                "author": "DeepSeek API",
                "created_date": now().strftime('%Y-%m-%d'),
                "summary": {
                    "total_prs": total_prs,
                    "clean_mode_count": clean_mode_count,
                    "optimize_mode_count": optimize_mode_count,
                    "study_mode_count": study_mode_count,
                    "newbie_mode_count": newbie_mode_count,
                    "basic_mode_count": basic_mode_count,

                },
                "review_table": pr_table_rows,
                "analysis": content,  # 분석 내용
            }
            return structured_content

        except Exception as e:
            logger.error(f"API 호출 실패: {e}")
            return {"error": "API 호출 실패", "details": str(e)}

    def generate_styled_pdf(self, report_title, report_data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'NanumGothic'
        styles['Heading1'].fontName = 'NanumGothic'
        styles['Heading2'].fontName = 'NanumGothic'
        styles['BodyText'].fontName = 'NanumGothic'

        elements = []

        # 제목 섹션
        elements.append(Paragraph(f"<strong>{report_data['title']}</strong>", styles['Heading1']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<strong>작성자:</strong> {report_data['author']}", styles['Normal']))
        elements.append(Paragraph(f"<strong>작성일자:</strong> {report_data['created_date']}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # 리뷰 데이터 요약
        elements.append(Paragraph("1. 리뷰 데이터 요약", styles['Heading2']))
        elements.append(Spacer(1, 12))

        # 테이블 데이터 변환
        table_data = [["PR ID", "제목", "평균 등급", "작성일자"]] + [
            [
                item["id"],
                Paragraph(item["title"], styles['Normal']),  # 제목을 Paragraph로 처리
                item["aver_grade"],
                item["created_at"].split(" ")[0]
            ]
            for item in report_data["review_table"]
        ]

        # Table 생성 및 스타일 적용
        table = Table(table_data, colWidths=[50, 300, 70, 100])  # 제목 칸 확장
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),  # NanumGothic 폰트 적용
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # 분석 내용
        elements.append(Paragraph("2. 분석 내용", styles['Heading2']))
        elements.append(Spacer(1, 12))

        # 분석 내용을 문단으로 구성
        analysis_lines = report_data["analysis"].split("\n")
        for line in analysis_lines:
            if line.strip():
                if line.startswith("-"):
                    elements.append(Paragraph(f"<strong>{line.strip()}</strong>", styles['Normal']))
                else:
                    elements.append(Paragraph(line.strip(), styles['BodyText']))
            elements.append(Spacer(1, 6))
        elements.append(Spacer(1, 24))

        # 결론

        # PDF 생성
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def post(self, request, user_id):
        try:
            report_title = request.data.get('report_title')
            pr_ids = request.data.get('pr_ids', [])

            # 데이터 유효성 검사
            if not report_title:
                return Response({"error_message": "보고서 제목이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
            if not pr_ids:
                return Response({"error_message": "PR ID 리스트가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
            if not (5 <= len(pr_ids) <= 10):
                return Response({"error_message": "pr_ids는 5개에서 10개 사이여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

            # PR 데이터 조회
            prs = PRReview.objects.filter(id__in=pr_ids, is_deleted=False)
            if len(prs) != len(pr_ids):
                invalid_ids = list(set(pr_ids) - set(pr.id for pr in prs))
                return Response({"error_message": f"유효하지 않은 PR ID가 포함되어 있습니다: {invalid_ids}"},
                                status=status.HTTP_400_BAD_REQUEST)

            # PR 리뷰 데이터 정리
            pr_reviews = [
                {
                    "id": pr.id,
                    "title": pr.title,
                    "pr_url": pr.pr_url,
                    "aver_grade": pr.aver_grade,
                    "problem_type": pr.problem_type,
                    "review_mode": pr.review_mode,
                    "total_review": pr.total_review,
                    "created_at": pr.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for pr in prs
            ]

            # DeepSeek API 호출
            report_content = self.generate_report_with_deepseek(report_title, pr_reviews)

            # PDF 생성 및 저장
            relative_pdf_path = f"report/reports/{now().strftime('%Y%m%d%H%M%S')}_report.pdf"
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            absolute_pdf_path = os.path.join(BASE_DIR, relative_pdf_path)

            os.makedirs(os.path.dirname(absolute_pdf_path), exist_ok=True)
            with open(absolute_pdf_path, 'wb') as f:
                f.write(self.generate_styled_pdf(report_title, report_content).getvalue())

            logger.debug(f"PDF 저장 경로: {absolute_pdf_path}")

            # 보고서 데이터베이스 저장
            report = Report.objects.create(
                user_id=user_id,
                title=report_title,
                content=report_content,
                pdf_url=relative_pdf_path,  # 상대 경로만 저장
                review_num=len(pr_reviews),
                created_at=now(),
                updated_at=now()
            )

            logger.debug(f"Report 생성 완료: ID={report.report_id}, pdf_url={report.pdf_url}")

            # PR과 보고서 연결
            for pr in prs:
                ReportPrReview.objects.create(report=report, pr_review=pr)

            # 성공 응답 반환
            return Response({
                "report_id": report.report_id,
                "user_id": report.user_id,
                "title": report.title,
                "content": report.content,
                "pdf_url": report.pdf_url,
                "review_num": len(pr_reviews),
                "created_at": report.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"보고서 생성 중 오류 발생: {e}")
            return Response({"error_message": f"보고서 생성 실패: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def generate_pdf_url(report_id):
        return reverse('report-download', args=[report_id])

class ReportDetailAPIView(APIView):
    def get(self, request, report_id):
        try:
            report = Report.objects.get(report_id=report_id)

            if report.is_deleted:
                return Response({"error_message": "삭제된 보고서입니다."}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "report_id": report.report_id,
                "user_id": report.user_id,
                "title": report.title,
                "content": report.content,
                "pdf_url": report.pdf_url,
                "review_num": report.review_num,
                "is_deleted": report.is_deleted,
                "created_at": report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": report.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }, status=status.HTTP_200_OK)
        except Report.DoesNotExist:
            return Response({"error_message": "보고서를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"특정 보고서 조회 중 오류 발생: {e}")
            return Response({"error_message": f"보고서 조회 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportDeleteAPIView(APIView):
    def delete(self, request, report_id):
        try:
            report = Report.objects.filter(report_id=report_id, is_deleted=False).first()

            if not report:
                return Response({"error_message": "삭제 대상 보고서 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            report.is_deleted = True
            report.save()

            return Response({"message": "보고서 삭제에 성공했습니다"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"{report_id} 보고서 삭제 중 오류 발생: {e}")
            return Response({"error_message": f"{report_id} 보고서 삭제 실패"}, status=status.HTTP_400_BAD_REQUEST)


class ReportDownloadAPIView(APIView):
    def get(self, request, report_id):
        try:
            # 데이터베이스에서 보고서 조회
            report = Report.objects.filter(report_id=report_id, is_deleted=False).first()

            if not report:
                return Response({"error_message": "Report not found or already deleted"}, status=status.HTTP_404_NOT_FOUND)

            # PDF 파일 경로 계산
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_path = os.path.join(BASE_DIR, report.pdf_url)

            # 파일 존재 여부 확인
            if not os.path.exists(pdf_path):
                logger.error(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
                return Response({"error_message": "PDF 파일을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            logger.debug(f"PDF 다운로드: {pdf_path}")

            # 파일 응답 반환
            return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=os.path.basename(pdf_path))

        except Exception as e:
            logger.error(f"PDF 다운로드 중 오류 발생: {e}")
            return Response({"error_message": "PDF 다운로드 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportModeAPIView(APIView):
    def get(self, request, report_id):
        try:
            report = Report.objects.get(report_id=report_id)

            pr_reviews = ReportPrReview.objects.filter(report=report)
            modes = pr_reviews.values_list('pr_review__review_mode', flat=True).distinct()

            unique_modes = list(set(modes))

            return Response({"modes": unique_modes}, status=status.HTTP_200_OK)

        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error fetching report modes: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)