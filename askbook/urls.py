from django.urls import path , include
from . import views


urlpatterns = [
    path('', views.landing , name='landing'),
    path('feed/', views.feed , name='feed'),
    path('auth/', views.auth , name='auth'),
    path('dashboard/', views.user_dashboard , name='user_dashboard'),
    path('dashboard/posts', views.user_posts , name='user_posts'),
    path('dashboard/profile', views.user_profile , name='user_profile'),
    path("dashboard/settings", views.user_settings, name="user_settings"),

    path("posts/<int:post_id>/like/", views.post_like, name="post_like"),
    path("posts/<int:post_id>/dislike/", views.post_dislike, name="post_dislike"),
    path("posts/<int:post_id>/favourite/", views.post_favourite, name="post_favourite"),
    path("posts/<int:post_id>/make-featured/", views.make_featured, name="make_featured"),


    path( "u/<slug:profile_slug>/", views.public_profile, name="public_profile" ),
    path("u/<slug:profile_slug>/edit/", views.user_profile_edit, name="user_profile_edit"),

    path('test-403/', views.test_403, name='test_403'),

    path("dashboard/posts/create/", views.post_create, name="post_create"),
    path("dashboard/posts/<int:pk>/<slug:slug>/edit/", views.post_edit, name="post_edit"),

    path("posts/<int:pk>/<slug:slug>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/<slug:slug>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:pk>/<slug:slug>/delete/", views.post_delete, name="post_delete"),

    path('admin-portal/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/toggle-verify/<int:user_id>/', views.toggle_verify, name='toggle_verify'),
    path('admin-portal/update-post-status/<int:post_id>/<str:new_status>/', views.update_post_status, name='update_post_status'),


    path("logout/", views.logout_view, name="logout"),
    
    
]