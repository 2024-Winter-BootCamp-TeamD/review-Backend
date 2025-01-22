from django.core.cache import cache

# 캐시에 데이터 저장
def set_cache(key, value, timeout=50):
    cache.set(key, value, timeout)

# 캐시에서 데이터 리턴
def get_cache(key):
    return cache.get(key)

def delete_cache(key):
    cache.delete(key)


# PRReview 데이터를 캐시에 저장
def cache_pr_review(pr_review):
    key = pr_review.id
    value = {
        "id": pr_review.id,
        "user": pr_review.user.id,
        "title": pr_review.title,
        "pr_url": pr_review.pr_url,
        "review_mode": pr_review.review_mode,
    }
    set_cache(key, value, timeout=50)
    return key

# JSON 데이터를 캐시에 저장
def cache_pr_data(pr_number, data):
    key = f"pr_data_{pr_number}"
    set_cache(key, data, timeout=60)
    return key