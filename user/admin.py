from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'user_id', 'github_username', 'email', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'email', 'github_username')

    def user_id(self, obj):
        return obj.user.id
    user_id.short_description = 'User ID'

# Admin에 등록
admin.site.register(UserProfile, UserProfileAdmin)
