from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    # Protected pages
    path("index/", login_required(views.index), name="index"),
    path('about/', login_required(views.about), name='about-us'),
    path('services/', login_required(views.services), name='services'),
    path('results/', login_required(views.results), name='results'),
    path('category/', login_required(views.category), name='category'),
    path('voting/', login_required(views.voting), name='voting'),
    path("vote/", login_required(views.vote), name="vote"),
    path('contact/', login_required(views.contact), name='contact-us'),
   
    
    # Login 
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),

    # Logout
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # Register
    path("register/", views.register, name="register"),  

]