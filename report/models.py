from django.db import models
from django.utils.timezone import now
from pullrequest.models import PRReview  # PRReview를 참조
from user.models import User


class Report(models.Model):
    report_id = models.AutoField(primary_key=True)  # report_id를 기본 키로 설정
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 작성자 정보
    title = models.CharField(max_length=100)  # 보고서 제목
    content = models.TextField()  # 보고서 내용
    pdf_url = models.CharField(max_length=255)  # PDF URL
    review_num = models.IntegerField(default=0)  # 리뷰 총합
    is_deleted = models.BooleanField(default=False)  # 삭제 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시각
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시각

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'report_report'  # 테이블 이름 명시


class ReportPrReview(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="pr_reviews")  # 보고서와 연관
    pr_review = models.ForeignKey(PRReview, on_delete=models.CASCADE, related_name="report_reviews")  # PR 리뷰와 연관
    created_at = models.DateTimeField(default=now)  # 생성 시각

    class Meta:
        unique_together = ('report', 'pr_review')  # 동일한 보고서와 PR 리뷰의 중복 방지
        db_table = 'report_prreview'  # 테이블 이름 명시

    def __str__(self):
        return f"Report {self.report.report_id} - PR {self.pr_review.id}"

