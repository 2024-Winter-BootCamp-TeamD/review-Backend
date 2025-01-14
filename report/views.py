import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import Report, ReportPrReview
from pullrequest.models import PRReview
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)


class ReportAPIView(APIView):
    def get(self, request):
        """
        보고서 목록 조회 (GET 요청)
        """
        try:
            # 페이지네이션 처리
            page = int(request.query_params.get('page', 1))  # 기본 페이지: 1
            size = int(request.query_params.get('size', 10))  # 기본 페이지 크기: 10
            reports = Report.objects.filter(is_deleted=False).order_by('-created_at')

            paginator = Paginator(reports, size)
            paginated_reports = paginator.get_page(page)

            # JSON 데이터 생성
            response_data = {
                "total_count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "reports": [
                    {
                        "report_id": report.report_id,
                        "title": report.title,
                        "content": report.content,
                        "pdf_url": report.pdf_url,
                        "review_num": report.review_num,
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

    def post(self, request):
        """
        보고서 생성 (POST 요청)
        """
        try:
            user_id = request.data.get('user_id')
            report_title = request.data.get('report_title')
            pr_ids = request.data.get('pr_ids', [])

            if not user_id or not report_title or not pr_ids:
                return Response({"error_message": "보고서 생성에 필요한 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

            if not (5 <= len(pr_ids) <= 10):
                return Response({"error_message": "pr_ids는 5개에서 10개 사이여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

            # PR 데이터 가져오기
            prs = PRReview.objects.filter(id__in=pr_ids, is_deleted=False)

            if len(prs) != len(pr_ids):
                return Response({"error_message": "유효하지 않은 PR ID가 포함되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 리뷰 코멘트 집계
            total_reviews = sum(int(pr.total_review or 0) for pr in prs)

            # 보고서 생성
            report_content = "이 보고서는 선택한 PR 리뷰 결과를 기반으로 작성되었습니다."
            report = Report.objects.create(
                user_id=user_id,
                title=report_title,
                content=report_content,
                pdf_url=f"http://example.com/report/{now().timestamp()}.pdf",
                review_num=total_reviews,
                created_at=now(),
                updated_at=now()
            )

            # ReportPrReview와 연결
            for pr in prs:
                ReportPrReview.objects.create(report=report, pr_review=pr)

            return Response({
                "report_id": report.report_id,
                "user_id": report.user_id,
                "title": report.title,
                "content": report.content,
                "pdf_url": report.pdf_url,
                "review_num": report.review_num,
                "created_at": report.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"보고서 생성 중 오류 발생: {e}")
            return Response({"error_message": f"보고서 생성 실패: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class ReportDetailAPIView(APIView):
    def get(self, request, report_id):
        """
        특정 보고서 조회 (GET 요청)
        """
        try:
            report = Report.objects.get(report_id=report_id)
            return Response({
                "report_id": report.report_id,
                "user_id": report.user_id,
                "title": report.title,
                "content": report.content,
                "pdf_url": report.pdf_url,
                "review_num": report.review_num,
                "created_at": report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": report.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }, status=status.HTTP_200_OK)
        except Report.DoesNotExist:
            return Response({"error_message": "보고서를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"특정 보고서 조회 중 오류 발생: {e}")
            return Response({"error_message": f"보고서 조회 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
