# from django.urls import path
# from . import views

from django.urls import path
from . import views

urlpatterns = [
	path('jobs/', views.jobpost_list, name='jobpost_list'),
	path('jobs/<int:job_id>/', views.jobpost_detail, name='jobpost_detail'),
	path('skills/', views.skills_list, name='skills_list'),
]
