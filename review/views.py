import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from pullrequest.models import PRReview
from repository.models import Repository
from review.tasks import process_pr_code_review, process_pr_code_only_review
from user.models import User


@csrf_exempt
def github_webhook(request):
    if not request.method == "POST":
        # POST 요청이 아닌 경우
        return HttpResponseBadRequest("Invalid request method")

    try:  # JSON 파싱
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    # PR 이벤트 처리
    action = data.get('action')  # PR 오픈 / PR 리오픈 / PR 클로즈
    pr = data.get('pull_request')
    print(action)
    # action과 pr이 유효하지 않은 경우 종료
    if not (action in ['opened', 'reopened'] and pr):
        return JsonResponse({"message": "Closed pull request"}, status=400)

    sender = data.get('sender', {})
    sender_username = sender.get('login')

    repository_github_id = data.get('repository', {}).get('id')
    if not repository_github_id:
        return JsonResponse({"message": "Missing repository ID"}, status=400)

    try:
        repository = Repository.objects.get(repository_github_id=repository_github_id)
        repo_name = data['repository']['full_name']
        commit_id = data['pull_request']['head']['sha']
        pr_number = pr['number']
        print("repo_name:", repo_name)

        hook_owner = User.objects.get(id=repository.user_id_id)
        access_token = hook_owner.access_token
        review_mode = hook_owner.review_mode
        print(f"Sender's Username, Hook Owner: {sender_username}, {hook_owner.github_username}")
        print(f"review mode: {review_mode}")

        # JSON 데이터 캐싱





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
            process_pr_code_review.delay(pr_review.id, access_token, repo_name, pr_number, commit_id)

        else:
            process_pr_code_only_review.delay(review_mode, access_token, repo_name, pr_number, commit_id)

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
