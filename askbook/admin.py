from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Post, Tag, PostTag, Favourite

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
    )

    search_fields = ("username", "email")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile Info", {
            "fields": (
                "bio",
                "works_at",
                "institute_at",
                "location",
                "avatar",
                "avatar_url",
                "profile_slug",
                "is_verified",
                "github_url",
                "linkedin_url",
            )
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_by",
        "status",
        "is_public",
        "is_featured",
        "views_count",
        "created_at",
    )

    list_filter = (
        "status",
        "is_public",
        "is_featured",
        "difficulty_level",
        "created_at",
    )

    search_fields = ("title", "summary", "prompt_text")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("created_by",)
    ordering = ("-created_at",)

    readonly_fields = ("views_count", "likes_count", "dislikes_count")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ("post", "tag")
    search_fields = ("post__title", "tag__name")
    raw_id_fields = ("post", "tag")


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username", "post__title")
    raw_id_fields = ("user", "post")
    ordering = ("-created_at",)
