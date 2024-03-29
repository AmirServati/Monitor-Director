"""
URL configuration for MonitorClient project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.status, name="status"),
    path('switch/<int:id>/', views.switch, name="switch"),
    path('autoplay/', views.autoplay, name="autoplay"),
    path('autodelete/', views.autodelete, name="autodelete"),
    path('autopow/', views.autopow, name="autopow"),
]
