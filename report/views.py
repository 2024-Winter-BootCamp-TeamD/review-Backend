import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import Report, ReportPrReview
from pullrequest.models import PRReview
from django.core.paginator import Paginator
import os
from dotenv import load_dotenv
import requests

load_dotenv()
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")

class UserReportAPIView(APIView):
    def get(self, request, user_id):
        try:
            page = int(request.query_params.get('page', 1))  # 기본 페이지: 1
            size = int(request.query_params.get('size', 10))  # 기본 페이지 크기: 10

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

        prompt = f"""
        여기에다가 프롬프트를 작성해 주세요~
           """

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
            }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": prompt}],
            "stream": False,
        }

        response = requests.post(f"{DEEPSEEK_API_URL}", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"DeepSeek API 호출 실패: {response.status_code}, {response.text}")

    def post(self, request, user_id):
        try:
            report_title = request.data.get('report_title')
            pr_ids = request.data.get('pr_ids', [])

            if not report_title or not pr_ids:
                return Response({"error_message": "보고서 생성에 필요한 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

            if not (5 <= len(pr_ids) <= 10):
                return Response({"error_message": "pr_ids는 5개에서 10개 사이여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

            prs = PRReview.objects.filter(id__in=pr_ids, is_deleted=False)

            if len(prs) != len(pr_ids):
                return Response({"error_message": "유효하지 않은 PR ID가 포함되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 리뷰 코멘트 개수 집계
            total_reviews = sum([1 for pr in prs if pr.total_review])  # PR 리뷰 개수

            # 보고서 생성
            pr_reviews = [
                {
                    "title": pr.title,
                    "pr_url": pr.pr_url,
                    "aver_grade": pr.aver_grade,
                    "problem_type": pr.problem_type,
                    "review_mode": pr.review_mode,
                    "total_review": pr.total_review,
                }
                for pr in prs
            ]

            # 딥시크 API 호출
            deepseek_result = self.generate_report_with_deepseek(report_title, pr_reviews)
            summary = deepseek_result.get("summary", "요약 없음")
            improvements = deepseek_result.get("improvements", "개선점 없음")
            evaluation = deepseek_result.get("evaluation", "평가 없음")
            score = deepseek_result.get("score", "N/A")

            # 보고서 내용
            report_content = f"""
                    요약: {summary}
                    개선점: {improvements}
                    평가: {evaluation}
                    점수: {score}
                    """

            report = Report.objects.create(
                user_id=user_id,
                title=report_title,
                content=report_content,
                pdf_url=f"http://example.com/report/{now().timestamp()}.pdf",
                review_num=len(pr_reviews),
                created_at=now(),
                updated_at=now()
            )

            # PR과 보고서 연결
            for pr in prs:
                ReportPrReview.objects.create(report=report, pr_review=pr)

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
            # 삭제 대상 보고서 조회
            report = Report.objects.filter(report_id=report_id, is_deleted=False).first()

            if not report:
                # 대상 보고서가 없을 경우 404 응답 반환
                return Response({"error_message": "삭제 대상 보고서 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # 보고서 삭제 처리
            report.is_deleted = True
            report.save()

            # 성공 응답 반환
            return Response({"message": "보고서 삭제에 성공했습니다"}, status=status.HTTP_200_OK)

        except Exception as e:
            # 삭제 중 오류 발생 시 에러 로그 기록 및 400 응답 반환
            logger.error(f"{report_id} 보고서 삭제 중 오류 발생: {e}")
            return Response({"error_message": f"{report_id} 보고서 삭제 실패"}, status=status.HTTP_400_BAD_REQUEST)

class ReportDownloadAPIView(APIView):
    def get(self, request, report_id):
        try:
            report = Report.objects.filter(report_id=report_id, is_deleted=False).first()

            if report.is_deleted:
                return Response({"error_message": "삭제된 보고서입니다."}, status=status.HTTP_404_NOT_FOUND)

            if not report:
                return Response({"error": "Report not found or already deleted"}, status=status.HTTP_404_NOT_FOUND)

            response_data = {
                "pdf_url": report.pdf_url
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error fetching report download URL: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

