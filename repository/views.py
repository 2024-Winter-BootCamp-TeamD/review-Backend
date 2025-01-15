from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

import user
from .models import Repository, User

from .serializers import RepositorySerializer
from .webhooks.controlWebhook import createWebhook, deactivateWebhook ,activateWebhook


@api_view(['GET'])
def get_repositories(request):
    """
    /repositories?user_id=123  형태로 호출:
    - user_id가 없으면 400 반환
    - 있으면 해당 user_id에 해당하는 Repository 목록 반환
    """
    user_id = request.query_params.get('user_id', None)

    if not user_id:
        return Response(
            {"레포지토리 조회 실패"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # user_id가 정수인지 확인
    try:
        user_id = int(user_id)
    except ValueError:
        return Response(
            {"error_message": "user_id는 정수여야 합니다"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 해당 user_id를 가진 Repository들 조회
    repositories = Repository.objects.filter(user_id=user_id)
    serializer = RepositorySerializer(repositories, many=True)

    response_data = {"repositories": serializer.data}

    return Response(response_data, status=status.HTTP_200_OK)




class ApplyRepositoryView(APIView):
    def post(self, request):
        data = request.data
        repositories = data.get("repositories")
        is_apply = data.get("is_apply")

        if not isinstance(is_apply, bool):
            return Response({"error": "is_apply는 boolean이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

            # repository_id와 repositories 배열 간 충돌 처리

        # 2) 데이터베이스 업데이트
        qs = Repository.objects.filter(id__in=repositories)
        updated_count = qs.update(is_apply=is_apply)


        if is_apply==False: #is_apply가 false일때
            false_results = []
            false_failed_repos=[]
            for repo in qs:
                repo_user = User.objects.get(id=repo.user_id.id)
                result = deactivateWebhook(
                    organization=repo.organization,
                    repo_name=repo.name,
                    access_token=repo_user.access_token,
                    hook_id=repo.hook_id,
                    repo_id=repo.id
                )
                if result["status"] == "success":
                    false_results.append({"id": repo.id, "message": result["message"]})
                else:
                    false_failed_repos.append({"id": repo.id, "error": result["message"]})
                    continue
            return Response(
                {
                    "webhook": {
                        "success": false_results,
                        "failed": false_failed_repos,
                    },
                }
            )




        if is_apply==True:
            results = []  # 성공 결과 저장
            failed_repos = []  # 실패한 repo 저장


            for repo in qs:
                repo_user = User.objects.get(id=repo.user_id.id)
                # 웹훅 생성 호출
                print(repo_user.access_token)
                result = createWebhook(
                    organization=repo.organization,
                    repo_name=repo.name,
                    access_token=repo_user.access_token,
                    repo_id=repo.id,
                    repo=repo,
                )
                if result["status"] == "success" and result.get("message", "").startswith("Already Existing"):
                    results.append({"id": repo.id, "message": result["message"]})
                    continue

                if result["status"] == "success":
                    results.append({"id": repo.id, "message": result["message"]})
                    # 웹훅 ID 저장
                    repo.hook_id = result["data"]["id"]
                    repo.save()
                else:
                    failed_repos.append({"id": repo.id, "error": result["message"]})
                    continue

            return Response(
                {
                    "webhook": {
                        "success": results,
                        "failed": failed_repos,
                    },

                }
            )


@api_view(['GET'])
def get_acitve(request):
    user_id = request.query_params.get('user_id')

    # 1) user_id가 없는 경우 처리
    if not user_id:
        return Response(
            {"error_message": "사용자 ID를 입력하세요."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 2) 해당 사용자의 is_apply=True인 레포지토리 조회
        repositories = Repository.objects.filter(user_id=user_id, is_apply=True)

        # 3) 레포지토리가 없는 경우 처리
        if not repositories.exists():
            return Response(
                {"repositories": []},
                status=status.HTTP_200_OK
            )

        # 4) 레포지토리 데이터를 JSON 형식으로 변환
        repositories_data = [
            {
                "id": repo.id,
                "user_id": repo.user_id.id,
                "organization": repo.organization,
                "name": repo.name,
                "repo_image": repo.repository_image,
                "is_apply": repo.is_apply
            }
            for repo in repositories
        ]

        return Response({"repositories": repositories_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error_message": f"기능 적용 레포지토리 조회 실패: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )




@api_view(['GET'])
def get_inacitve(request):
    user_id = request.query_params.get('user_id')

    # 1) user_id가 없는 경우 처리
    if not user_id:
        return Response(
            {"error_message": "사용자 ID를 입력하세요."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 2) 해당 사용자의 is_apply=False인 레포지토리 조회
        repositories = Repository.objects.filter(user_id=user_id, is_apply=False)

        # 3) 레포지토리가 없는 경우 처리
        if not repositories.exists():
            return Response(
                {"repositories": []},
                status=status.HTTP_200_OK
            )

        # 4) 레포지토리 데이터를 JSON 형식으로 변환
        repositories_data = [
            {
                "id": repo.id,
                "user_id": repo.user_id.id,
                "organization": repo.organization,
                "name": repo.name,
                "repo_image": repo.repository_image,
                "is_apply": repo.is_apply
            }
            for repo in repositories
        ]

        return Response({"repositories": repositories_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error_message": f"기능 적용 레포지토리 조회 실패: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_search(request):
        user_id = request.query_params.get('user_id')
        search_query = request.query_params.get('search_query', "")
        is_apply_str = request.query_params.get('is_apply', "").lower()  # "true"

        # 1) user_id 검증
        if not user_id:
            return Response({"error_message": "user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2) 기본 쿼리: 사용자 ID로 필터링
            qs = Repository.objects.filter(user_id=user_id)

            # 3) 검색어(search_query)로 이름 부분 검색
            if search_query:
                qs = qs.filter(name__icontains=search_query)

            # 4) is_apply=true/false 처리
            if is_apply_str == "true":
                qs = qs.filter(is_apply=True)

            repositories_data = [
            {
                "id": repo.id,
                "user_id": repo.user_id.id,
                "organization": repo.organization,
                "name": repo.name,
                "repo_image": repo.repository_image,
                "is_apply": repo.is_apply
            }
                for repo in qs
                ]
            return Response({"repositories": repositories_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error_message": f"기능 적용 레포지토리 조회 실패: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)