from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import JobPost, Author, Skills, Location

# Create your views here.
# Simple view to list all job posts
def jobpost_list(request):
	jobs = JobPost.objects.all()
	data = [
		{
			'title': job.title,
			'description': job.description,
			'salary': job.salary,
			'author': str(job.author) if job.author else None,
			'location': str(job.location) if job.location else None,
			'skills': [skill.name for skill in job.skills.all()],
		}
		for job in jobs
	]
	return JsonResponse({'jobs': data})

# Simple view to show details of a single job post
def jobpost_detail(request, job_id):
	try:
		job = JobPost.objects.get(id=job_id)
		data = {
			'title': job.title,
			'description': job.description,
			'salary': job.salary,
			'author': str(job.author) if job.author else None,
			'location': str(job.location) if job.location else None,
			'skills': [skill.name for skill in job.skills.all()],
		}
		return JsonResponse(data)
	except JobPost.DoesNotExist:
		return JsonResponse({'error': 'JobPost not found'}, status=404)

# Simple view to list all skills
def skills_list(request):
	skills = Skills.objects.all()
	data = [skill.name for skill in skills]
	return JsonResponse({'skills': data})
