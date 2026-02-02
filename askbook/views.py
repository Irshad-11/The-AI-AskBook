from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm, LoginForm
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import User , Tag, PostTag , PostReaction
from .forms import PostForm , UserProfileForm
from django.db import transaction
from django.db.models import Sum, Count
from django.urls import reverse
from django.views.decorators.http import require_POST

from django.utils import timezone
from datetime import timedelta

from django.db.models import Count, Q, F, ExpressionWrapper, FloatField

from .models import Post, Favourite




from django.core.exceptions import PermissionDenied

def test_403(request):
    raise PermissionDenied("You shall not pass!")



def landing(request):
    # Total approved public posts
    total_posts = Post.objects.filter(status="APPROVED", is_public=True).count()

    # Weekly growth (percentage)
    one_week_ago = timezone.now() - timedelta(days=7)
    posts_this_week = Post.objects.filter(
        status="APPROVED", is_public=True, created_at__gte=one_week_ago
    ).count()
    posts_last_week = Post.objects.filter(
        status="APPROVED", is_public=True,
        created_at__lt=one_week_ago,
        created_at__gte=one_week_ago - timedelta(days=7)
    ).count()

    if posts_last_week > 0:
        weekly_growth = round(((posts_this_week - posts_last_week) / posts_last_week) * 100, 1)
    else:
        weekly_growth = 100 if posts_this_week > 0 else 0  # avoid division by zero

    # Active curators = total users who have at least 1 post
    active_curators = User.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0).count()

    # Total unique topics (tags)
    total_topics = Tag.objects.annotate(post_count=Count('tag_posts')).filter(post_count__gt=0).count()

    # Featured posts (Trending Collections) – latest first
    featured_posts = Post.objects.filter(
        status="APPROVED",
        is_public=True,
        is_featured=True
    ).select_related('created_by').order_by('-created_at')[:3]  # show 3 latest featured

    context = {
        'total_posts': total_posts,
        'weekly_growth': weekly_growth,
        'active_curators': active_curators,
        'total_topics': total_topics,
        'featured_posts': featured_posts,
    }

    return render(request, 'landing.html', context)



def feed(request):

    # 1. Get filter parameters

    query = request.GET.get('q', '')

    difficulty = request.GET.get('difficulty', '')

    sort = request.GET.get('sort', '')  # featured, favourites, likes

    # 2. Base Queryset: only approved public posts

    posts = Post.objects.filter(status="APPROVED", is_public=True)

    # 3. Apply Search

    if query:

        posts = posts.filter(

            Q(title__icontains=query) | 

            Q(summary__icontains=query) |

            Q(post_tags__tag__name__icontains=query)

        ).distinct()

    # 4. Apply Difficulty Filter (optional — keep if you still want it)

    if difficulty:

        posts = posts.filter(difficulty_level=difficulty)

    # 5. Apply Sorting / Filtering based on ?sort=

    if sort == "featured":

        posts = posts.filter(is_featured=True).order_by("-created_at")

    

    elif sort == "favourites":

        posts = posts.annotate(

            fav_count=Count('favourited_by')   # ← FIXED: use 'favourited_by'

        ).order_by("-fav_count", "-created_at")

    

    elif sort == "likes":

        posts = posts.order_by("-likes_count", "-created_at")

    

    else:

        # Default: newest first

        posts = posts.order_by("-created_at")

    # 6. Optimized Reaction/Favourite Logic (only for authenticated users)

    if request.user.is_authenticated:

        # Get reactions and favourites only once

        reactions = PostReaction.objects.filter(user=request.user).values_list('post_id', 'reaction_type')

        reaction_dict = dict(reactions)

        

        fav_ids = set(Favourite.objects.filter(user=request.user).values_list('post_id', flat=True))

        # Attach attributes only to the posts we're displaying

        for post in posts:

            post.user_reaction = reaction_dict.get(post.id)

            post.is_favourited_by_user = post.id in fav_ids

    context = {

        'posts': posts,

        'query': query,

        'difficulty': difficulty,

        'sort': sort,  # optional: can be used to highlight active filter in sidebar

    }

    return render(request, "feed.html", context)


def public_profile(request, profile_slug):
    profile_user = get_object_or_404(User, profile_slug=profile_slug)

    public_posts = Post.objects.filter(
        created_by=profile_user,
        status="APPROVED",
        is_public=True,
    ).order_by("-created_at")

    context = {
        "profile_user": profile_user,
        "public_posts": public_posts,
    }
    return render(request, "public_profile.html", context)



def auth(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # ---------- LOGIN ----------
        if action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                
                if user.is_staff:
                    return redirect("admin_dashboard")
            
                return redirect("user_dashboard")

            return render(request, "auth.html", {
                "login_error": "Invalid credentials",
                "active_tab": "login",
            })

        # ---------- SIGNUP ----------
        if action == "signup":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                return render(request, "auth.html", {
                    "signup_error": "Passwords do not match",
                    "active_tab": "signup",
                })

            if User.objects.filter(username=username).exists():
                return render(request, "auth.html", {
                    "signup_error": "Username already taken",
                    "active_tab": "signup",
                })

            if User.objects.filter(email=email).exists():
                return render(request, "auth.html", {
                    "signup_error": "Email already registered",
                    "active_tab": "signup",
                })

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True,
            )

            login(request, user)
            return redirect("user_dashboard")

    return render(request, "auth.html")


@login_required
def user_dashboard(request):
    user = request.user

    if user.is_staff:
        return redirect("admin_dashboard")

    # ─── User's own posts (base for stats + manage posts) ──────────────────────
    user_posts = Post.objects.filter(created_by=user).select_related("created_by")

    # ─── Stats ─────────────────────────────────────────────────────────────────
    stats = {
        "total_posts": user_posts.count(),
        "approved_posts": user_posts.filter(status="APPROVED").count(),
        "pending_posts": user_posts.filter(status="PENDING").count(),
        "rejected_posts": user_posts.filter(status="REJECTED").count(),
        "total_views": user_posts.aggregate(total=Sum("views_count"))["total"] or 0,
        "total_likes": user_posts.aggregate(total=Sum("likes_count"))["total"] or 0,
        "total_dislikes": user_posts.aggregate(total=Sum("dislikes_count"))["total"] or 0,
        "total_favourites_received": Favourite.objects.filter(post__created_by=user).count(),
    }

    # ─── Recent posts (dashboard overview) ─────────────────────────────────────
    recent_posts = user_posts.order_by("-created_at")[:5]

    # ─── Manage Posts filtered list + reaction/favourite annotations ───────────
    posts = None
    active_tab = "all"

    # Only process when on manage posts page
    if request.path.startswith("/dashboard/posts"):
        tab = request.GET.get("tab", "all").lower()

        if tab == "approved":
            posts = user_posts.filter(status="APPROVED")
            active_tab = "approved"
        elif tab == "pending":
            posts = user_posts.filter(status="PENDING")
            active_tab = "pending"
        elif tab == "rejected":
            posts = user_posts.filter(status="REJECTED")
            active_tab = "rejected"
        elif tab == "favourites":
            fav_ids = Favourite.objects.filter(user=user).values_list("post_id", flat=True)
            posts = Post.objects.filter(id__in=fav_ids).select_related("created_by")
            active_tab = "favourites"
        else:
            posts = user_posts.order_by("-created_at")
            active_tab = "all"

        # ─── This is the key part — same as your working feed view ─────────────
        if request.user.is_authenticated and posts is not None:
            # Get reactions and favourites only for the displayed posts
            post_ids = posts.values_list("id", flat=True)

            reactions = PostReaction.objects.filter(
                user=request.user,
                post__id__in=post_ids
            ).values_list("post_id", "reaction_type")

            fav_ids = set(
                Favourite.objects.filter(
                    user=request.user,
                    post__id__in=post_ids
                ).values_list("post_id", flat=True)
            )

            reaction_dict = dict(reactions)

            # Attach attributes — exactly like in feed view
            for post in posts:
                post.user_reaction = reaction_dict.get(post.id)
                post.is_favourited_by_user = post.id in fav_ids

    # ─── Context ───────────────────────────────────────────────────────────────
    context = {
        "stats": stats,
        "recent_posts": recent_posts,
        "posts": posts,           # ← template uses this in manage posts section
        "active_tab": active_tab, # ← optional, can help highlight tabs
    }

    return render(request, "user_dashboard.html", context)


@login_required
def user_posts(request):
    user = request.user

    tab = request.GET.get("tab", "all")
    search = request.GET.get("q")

    # ---------------- base queryset ----------------
    posts = Post.objects.filter(created_by=user)

    # ---------------- tab filtering ----------------
    if tab == "approved":
        posts = posts.filter(status="APPROVED")

    elif tab == "pending":
        posts = posts.filter(status="PENDING")

    elif tab == "rejected":
        posts = posts.filter(status="REJECTED")

    elif tab == "favourites":
        # posts this user has favourited
        posts = Post.objects.filter(
            favourited_by__user=user
        ).distinct()

    # ---------------- search ----------------
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(summary__icontains=search)
        )

    # ---------------- counts ----------------
    total_posts = Post.objects.filter(created_by=user).count()
    approved_posts = Post.objects.filter(created_by=user, status="APPROVED").count()
    pending_posts = Post.objects.filter(created_by=user, status="PENDING").count()
    rejected_posts = Post.objects.filter(created_by=user, status="REJECTED").count()

    favourites_count = Favourite.objects.filter(user=user).count()

    context = {
        "posts": posts,
        "active_tab": tab,
        "search": search,

        "total_posts": total_posts,
        "approved_posts": approved_posts,
        "pending_posts": pending_posts,
        "rejected_posts": rejected_posts,
        "favourites_posts": favourites_count,
    }

    return render(request, "user_dashboard.html", context)



# Helper function for mutual exclusion logic
def handle_reaction(user, post, reaction_type):
    with transaction.atomic():
        existing = PostReaction.objects.filter(user=user, post=post).first()
        
        if existing:
            if existing.reaction_type == reaction_type:
                # Toggle OFF if clicking the same icon
                existing.delete()
                if reaction_type == "LIKE": post.likes_count -= 1
                else: post.dislikes_count -= 1
            else:
                # Switch Reaction (e.g. Dislike -> Like)
                if reaction_type == "LIKE":
                    post.likes_count += 1
                    post.dislikes_count -= 1
                else:
                    post.dislikes_count += 1
                    post.likes_count -= 1
                existing.reaction_type = reaction_type
                existing.save()
        else:
            # New Reaction
            PostReaction.objects.create(user=user, post=post, reaction_type=reaction_type)
            if reaction_type == "LIKE": post.likes_count += 1
            else: post.dislikes_count += 1
        
        # Ensure counts never go below zero
        post.likes_count = max(0, post.likes_count)
        post.dislikes_count = max(0, post.dislikes_count)
        post.save()

@login_required
@require_POST
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    handle_reaction(request.user, post, "LIKE")
    return redirect(request.META.get("HTTP_REFERER", "feed"))

@login_required
@require_POST
def post_dislike(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    handle_reaction(request.user, post, "DISLIKE")
    return redirect(request.META.get("HTTP_REFERER", "feed"))

@login_required
@require_POST
def post_favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    fav, created = Favourite.objects.get_or_create(user=request.user, post=post)
    if not created:
        fav.delete()
    return redirect(request.META.get("HTTP_REFERER", "feed"))

@login_required
@require_POST
def make_featured(request, post_id):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    post = get_object_or_404(Post, id=post_id)
    post.is_featured = not post.is_featured
    post.save()
    return redirect(request.META.get("HTTP_REFERER", "feed"))

def post_detail(request, pk, slug):
    post = get_object_or_404(Post, pk=pk, status="APPROVED")

    # SEO redirect if slug changed
    if post.slug != slug:
        return redirect("post_detail", pk=post.pk, slug=post.slug)

    # Attach user-specific reaction & favourite status
    if request.user.is_authenticated:
        # Reaction
        reaction = PostReaction.objects.filter(user=request.user, post=post).first()
        post.user_reaction = reaction.reaction_type if reaction else None

        # Favourite
        post.is_favourited_by_user = Favourite.objects.filter(user=request.user, post=post).exists()

    # Related posts (unchanged)
    post_tags_ids = post.post_tags.values_list('tag_id', flat=True)
    related_posts = Post.objects.filter(status="APPROVED", post_tags__tag_id__in=post_tags_ids)\
                                .exclude(pk=post.pk)\
                                .annotate(same_tags=Count('post_tags'))\
                                .order_by("-same_tags", "-created_at")[:4]

    author_posts = Post.objects.filter(created_by=post.created_by, status="APPROVED")\
                               .exclude(pk=post.pk)[:3]

    context = {
        "post": post,
        "related_posts": related_posts,
        "author_posts": author_posts,
    }

    return render(request, "post_detail.html", context)

@login_required
def user_profile(request):
    user = request.user

    # ---- stats ----
    total_posts = Post.objects.filter(created_by=user).count()

    # ---- update profile ----
    if request.method == "POST":
        user.bio = request.POST.get("bio", "")
        user.works_at = request.POST.get("works_at", "")
        user.institute_at = request.POST.get("institute_at", "")
        user.location = request.POST.get("location", "")

        # avatar upload
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]

        user.save()

        return redirect("user_profile")

    context = {
        "profile_user": user,
        "total_posts": total_posts,
    }

    return render(request, "user_dashboard.html", context)



@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.slug = slugify(post.title)

            if request.user.is_verified:
                post.status = "APPROVED"
            else:
                post.status = "PENDING"

            post.save()

            # ---- tags ----
            tags_raw = form.cleaned_data["tags"]

            for raw_name in tags_raw.split():
                clean_name = raw_name.strip().lower()
                slug = slugify(clean_name)

                tag, created = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={"name": clean_name}
                )

                PostTag.objects.get_or_create(post=post, tag=tag)

            return redirect("user_posts")
    else:
        form = PostForm()

    return render(request, "post_form.html", {
        "form": form,
        "mode": "create",
    })




@login_required
def post_edit(request, pk, slug):
    post = get_object_or_404(Post, pk=pk, created_by=request.user)
    if post.created_by != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    initial_tags = " ".join(
        pt.tag.name for pt in post.post_tags.all()
    )

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title)  # 🔥 rewrite slug
            post.status = "PENDING"
            post.save()

            post.post_tags.all().delete()

            tags_raw = form.cleaned_data.get("tags", "")
            for raw in tags_raw.split():
                name = raw.lower()
                slug = slugify(name)

                tag, _ = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={"name": name}
                )
                PostTag.objects.create(post=post, tag=tag)

            return redirect("user_posts")
    else:
        form = PostForm(instance=post, initial={"tags": initial_tags})

    return render(request, "post_form.html", {
        "form": form,
        "mode": "edit",
        "post": post,
    })


@login_required
def post_delete(request, pk, slug): # Added pk here
    # Use pk for the lookup, it's more reliable
    post = get_object_or_404(Post, pk=pk)

    if post.created_by != request.user:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        post.delete()
        # Make sure the name matches your urls.py (user_posts)
        return redirect("user_posts") 

    return redirect("post_detail", pk=pk, slug=slug)

@login_required
def user_settings(request):
    user = request.user

    if request.method == "POST":
        action = request.POST.get("action")

        # ---------- DELETE PROFILE ----------
        if action == "delete_profile":
            logout(request)     # end session
            user.delete()       # delete user permanently
            return redirect("landing")

    return render(request, "user_dashboard.html", {
        "settings_page": True
    })

@login_required
def user_profile_edit(request, profile_slug):
    profile_user = get_object_or_404(User, profile_slug=profile_slug)

    # 🔒 SECURITY: only owner can edit
    if request.user != profile_user:
        return HttpResponseForbidden("You cannot edit this profile")

    if request.method == "POST":
        profile_user.bio = request.POST.get("bio", "")
        profile_user.works_at = request.POST.get("works_at", "")
        profile_user.institute_at = request.POST.get("institute_at", "")
        profile_user.location = request.POST.get("location", "")
        profile_user.github_url = request.POST.get("github_url", "")
        profile_user.linkedin_url = request.POST.get("linkedin_url", "")

        if "avatar" in request.FILES:
            profile_user.avatar = request.FILES["avatar"]

        profile_user.save()
        return redirect("public_profile", profile_slug=profile_user.profile_slug)

    return render(request, "profile_form.html", {
        "profile_user": profile_user
    })



def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    current_tab = request.GET.get('tab', 'dashboard')
    
    # 1. SIDEBAR ALERTS (Global)
    pending_count = Post.objects.filter(status='PENDING').count()

    context = {
        'current_tab': current_tab,
        'pending_count': pending_count,
    }

    if current_tab == 'dashboard':
        total_posts = Post.objects.count()
        # Stats
        context.update({
            'total_users': User.objects.count(),
            'total_posts': total_posts,
            'approved_posts': Post.objects.filter(status='APPROVED').count(),
            'pending_posts': pending_count,
            'rejected_posts': Post.objects.filter(status='REJECTED').count(),
            'featured_posts': Post.objects.filter(is_featured=True).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
        })

        # Top Users by Approved Posts
        context['top_approved_users'] = User.objects.annotate(
            count=Count('posts', filter=Q(posts__status='APPROVED'))
        ).order_by('-count')[:5]

        # Top Users by Featured Posts
        context['top_featured_users'] = User.objects.annotate(
            count=Count('posts', filter=Q(posts__is_featured=True))
        ).order_by('-count')[:5]

    elif current_tab == 'posts':
        context.update({
            'pending_list': Post.objects.filter(status='PENDING'),
            'approved_list': Post.objects.filter(status='APPROVED'),
            'rejected_list': Post.objects.filter(status='REJECTED'),
        })

    elif current_tab == 'users':
        # Annotate users with counts and calculate percentages
        users = User.objects.annotate(
            total_p=Count('posts'),
            app_p=Count('posts', filter=Q(posts__status='APPROVED')),
            rej_p=Count('posts', filter=Q(posts__status='REJECTED')),
        )
        
        # Simple Python sorting for complex percentages
        user_list = list(users)
        sort_by = request.GET.get('sort', 'name')
        if sort_by == 'approval':
            user_list.sort(key=lambda u: (u.app_p / u.total_p) if u.total_p > 0 else 0, reverse=True)
        
        context['users'] = user_list

    return render(request, "admin_dashboard.html", context)

@login_required
@user_passes_test(is_admin)
def toggle_verify(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    target_user.is_verified = not target_user.is_verified
    target_user.save()

    base_url = reverse('admin_dashboard') 
    return redirect(f"{base_url}?tab=users")


@login_required
@user_passes_test(is_admin)
def update_post_status(request, post_id, new_status):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST' and new_status.upper() == 'REJECTED':
        reason = request.POST.get('rejection_reason', 'No reason provided.')
        post.status = 'REJECTED'
        post.rejection_reason = reason
        post.save()
    elif new_status.upper() == 'APPROVED':
        post.status = 'APPROVED'
        post.rejection_reason = "" # Clear reason if re-approved
        post.save()

    base_url = reverse('admin_dashboard')
    return redirect(f"{base_url}?tab=posts")


def logout_view(request):
    logout(request)
    return redirect("landing")


@login_required
def user_settings(request):
    user = request.user

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete_profile":
            logout(request)     # end session
            user.delete()       # delete user permanently
            return redirect("landing")

    return render(request, "user_dashboard.html", {
        "settings_page": True   # optional flag if needed
    })