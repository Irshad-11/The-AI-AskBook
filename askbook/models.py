from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)

    bio = models.TextField(blank=True)
    works_at = models.CharField(max_length=255, blank=True)
    institute_at = models.CharField(max_length=255, blank=True)   
    location = models.CharField(max_length=255, blank=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    avatar_url = models.URLField(blank=True)

    profile_slug = models.SlugField(max_length=160, unique=True, blank=True)

    github_url = models.URLField(max_length=200, blank=True, null=True) 
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.profile_slug:
            self.profile_slug = slugify(self.username)
        super().save(*args, **kwargs)

    def profile_completion(self):
        fields = [
            self.avatar,
            self.bio,
            self.works_at,
            self.institute_at,
            self.location,
        ]
        filled = sum(bool(f) for f in fields)
        return int((filled / len(fields)) * 100)

    def __str__(self):
        return self.username



class Post(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    DIFFICULTY_CHOICES = [
        ("BEGINNER", "Beginner"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    summary = models.TextField()
    prompt_text = models.TextField()
    description_md = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)

    rejection_reason = models.TextField(blank=True)

    ai_model = models.CharField(max_length=100, blank=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    def get_user_reaction(self, user):
        """Returns the reaction type if the user has reacted, else None"""
        if user.is_authenticated:
            reaction = self.reactions.filter(user=user).first()
            return reaction.reaction_type if reaction else None
        return None

    def is_favourited_by(self, user):
        if user.is_authenticated:
            return self.favourited_by.filter(user=user).exists()
        return False

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title



class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PostTag(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_tags"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tag_posts"
    )

    class Meta:
        unique_together = ("post", "tag")

    def __str__(self):
        return f"{self.post.title} → {self.tag.name}"



class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favourites"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="favourited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.title}"


class PostReaction(models.Model):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"

    REACTION_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_reactions"
    )

    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    reaction_type = models.CharField(
        max_length=7,
        choices=REACTION_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "post")
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["reaction_type"]),
        ]

    def __str__(self):
        return f"{self.user} → {self.post} ({self.reaction_type})"
    

