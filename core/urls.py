
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("accounts/signup/", views.signup, name="signup"),

    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "accounts/delete/",
        views.delete_account,
        name="delete_account",
    ),

    path("", views.dashboard, name="dashboard"),
    path("leave/", views.leave_request_list, name="leave_requests"),
    path("leave/new/", views.leave_request_create, name="leave_create"),
    path(
        "leave/<int:pk>/decision/<str:decision>/",
        views.decide_leave,
        name="leave_decision",
    ),
    
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/new/", views.task_create, name="task_create"),
    
    path("handovers/", views.handover_list, name="handover_list"),
    path("handovers/new/", views.handover_create, name="handover_create"),
    path(
        "handovers/<int:pk>/<str:decision>/",
        views.decide_handover,
        name="handover_decision",
    ),
    
    path("team/", views.team_overview, name="team_overview"),
    
    path(
        "handovers/ai-draft/",
        views.handover_ai_draft,
        name="handover_ai_draft",
    ),

    
    path(
        "leave/<int:pk>/ai-risk/",
        views.ai_risk_explainer,
        name="ai_risk_explainer",
    ),
    path(
        "ask-teamflow/",
        views.ask_teamflow,
        name="ask_teamflow",
    ),
    
    

    

]
