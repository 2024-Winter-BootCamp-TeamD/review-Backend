import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from pullrequest.models import PRReview
from repository.models import Repository
from user.models import User
from apiserver.tasks import async_process_pr_review, async_process_pr_code_only_review



# 리팩토링 요소 정리
## 비동기 처리 구현
## 비동기 처리 구현 이후 웹훅에는 수신 응답 빠르게 반환해야 함
@csrf_exempt
def github_webhook(request):
    if request.method == "POST":
        # JSON 데이터를 파싱
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        # PR 이벤트 처리
        try:
            action = data.get('action')  # PR 오픈 / PR 리오픈 / PR 클로즈
            pr = data.get('pull_request')
            if action in ['opened', 'reopened'] and pr:
                sender = data.get('sender', {})
                sender_username = sender.get('login')

                repository_github_id = data.get('repository', {}).get('id')
                if not repository_github_id:
                    return JsonResponse({"message": "Missing repository ID"}, status=400)

                repository = Repository.objects.get(repository_github_id=repository_github_id)
                repo_name = data['repository']['full_name']
                print("repo_name:", repo_name)

                hook_owner = User.objects.get(id=repository.user_id_id)
                review_mode = "clean mode" #hook_owner.review_mode
                print(action)
                print(f"Sender's Username: {sender_username}")
                print(f"Hook Owner: {hook_owner.github_username}")
                print(f"review mode: {review_mode}")

                pr_number = pr['number']
                print("pr_number:", pr_number)

                access_token = hook_owner.access_token
                print("Access Token:", access_token)

                commit_id = data['pull_request']['head']['sha']

                if sender_username == hook_owner.github_username:
                    pr_review = PRReview(
                        user=hook_owner,
                        title=pr['title'],
                        pr_url=pr['url'],
                        aver_grade="Pending",
                        review_mode=review_mode,
                        total_review="Pending"
                    )
                    pr_review.full_clean()
                    pr_review.save()
                    async_process_pr_review.delay(pr_review.id, access_token, repo_name, pr_number, commit_id)
                else:
                    async_process_pr_code_only_review.delay(access_token, repo_name, pr_number, commit_id)

                # 성공적인 응답 반환
                return JsonResponse({
                    "message": "Webhook processed successfully",
                    "action": action,
                    "sender_username": sender_username,
                    "repository_name": repo_name,
                    "pr_number": pr_number,
                }, status=200)

        except Repository.DoesNotExist:
            return JsonResponse({"message": "Repository not found"}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"message": "Hook owner not found"}, status=404)

        except KeyError as e:
            return JsonResponse({"message": f"Missing key: {str(e)}"}, status=400)

    # POST 요청이 아닌 경우
    return HttpResponseBadRequest("Invalid request method")




'''
def get_pr_files(access_token, repo_name, pr_number):
    """
    PR의 모든 파일 정보를 가져오는 함수
    """
    GITHUB_TOKEN = access_token
    GITHUB_API_URL = "https://api.github.com"

    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/files"
    print("get_url:", url)
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve PR files: {response.status_code}, {response.text}")


def download_file_content(file_url):
    """
    파일의 실제 내용을 다운로드하는 함수
    """
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to download file content: {response.status_code}, {response.text}")


def post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, comment):
    """
    PR 파일에 댓글을 추가하는 함수
    """
    if "리뷰할 내용이 없습니다" in comment:
        print(f"Skipping comment for {file_path}: 리뷰할 내용이 없습니다.")
        return

    GITHUB_API_URL = "https://api.github.com"
    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment,
        "path": file_path,
        "position": 1,
        "commit_id": commit_id
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Comment successfully posted on {file_path}.")
    else:
        print(f"Failed to post comment: {response.status_code}, {response.json()}")


def process_pr_code_review(pr_review, access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    """
    try:
        pr_files = get_pr_files(access_token, repo_name, pr_number)
        gather_reviews = ""
        total_score = 0
        file_count = 0

        for file_info in pr_files:
            file_path = file_info["filename"]
            file_extension = os.path.splitext(file_path)[1]

            if file_extension in SUPPORTED_EXTENSIONS:
                file_content = download_file_content(file_info["raw_url"])
                review_result = file_code_review(file_content, pr_review.id)
                gather_reviews += review_result

                # 점수 추출 및 누적
                score_match = re.search(r'"score":\s*(\d+)', review_result)
                if score_match:
                    total_score += int(score_match.group(1))
                file_count += 1

                post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_result)

        if file_count > 0:
            average_score = total_score / file_count
            average_grade = get_grade(average_score)
        else:
            average_grade = "Unknown"

        pr_review_result = get_pr_review(gather_reviews, average_grade)
        post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result)

    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")


def process_pr_code_only_review(access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    이때 익스텐션 사용자의 pr이 아닌경우 db에 저장하지 않음
    """
    # 등급 평균 추출 준비
    file_num = 0
    total_score = 0
    gather_reviews = ""
    try:
        # PR의 모든 파일 가져오기
        pr_files = async_get_pr_files.delay(access_token, repo_name, pr_number)

        for file_info in pr_files:
            file_path = file_info["filename"]

            file_extension = os.path.splitext(file_path)[1]

            # 지원하는 확장자인 경우에만 처리
            if file_extension in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")

                file_num += 1

                # 파일 내용 가져오기
                file_content = async_download_file_content.delay(file_info["raw_url"])

                # 코드 리뷰 수행
                review_result = file_code_review(file_content)
                print("review_result:", review_result)

                review_text, score = get_score_review_text(file_path, review_result)
                total_score += score
                gather_reviews += review_text

                # 리뷰 결과를 PR에 댓글로 추가
                async_post_comment_to_pr.delay(commit_id, access_token, repo_name, pr_number, file_path, review_text)
            else:
                print(f"Skipping unsupported file: {file_path}")

        if file_num > 0:
            aver_score = total_score / file_num
            aver_grade = get_grade(aver_score)
            print("aver_grade:", aver_grade)
            print("gather_reviews:", gather_reviews)

            # 받은 모든 리뷰를 토대로 PR리뷰 받기
            pr_review_result = get_pr_review(gather_reviews, aver_grade)

            if aver_grade != 'A' and aver_grade != 'S':
                problem_type = get_problem_type(pr_review_result)

            # pr에 총평 댓글로 남겨주는 함수 실행
            post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result)
    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")
'''