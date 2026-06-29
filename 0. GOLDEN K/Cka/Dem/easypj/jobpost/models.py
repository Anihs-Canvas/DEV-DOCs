
# I have created 5 models and their objects
# In this chat, i will be asking you questions, and you will be using the models and the objects below to give me examples
# This is the code



# Import necessary modules
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


# Create your models here.
class Skills(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.company}"

class Location(models.Model):
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    zip = models.CharField(max_length=200)

    def __str__(self):
        return f" {self.country}"


class JobPost(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
    ]
        
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    expiry = models.DateField(null=True)
    salary = models.IntegerField()
    slug = models.SlugField(null=True, max_length=40, unique=True)
    type = models.CharField(max_length=200, null=False, choices=JOB_TYPE_CHOICES, default= 'Full Time')
    
    #Uniques columns
    location = models.OneToOneField(Location, on_delete=models.CASCADE , null=True, related_name='jobpost', related_query_name="jobpost")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name='jobpost', related_query_name="jobpost")
    skills = models.ManyToManyField(Skills, related_name='jobpost', related_query_name="jobpost")

    def save(self, *args, **kwargs):
        # Auto-generate a unique slug from title when missing
        if not self.slug and self.title:
            base_slug = slugify(self.title)[:40]
            candidate = base_slug
            i = 1
            while JobPost.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                suffix = f"-{i}"
                candidate = f"{base_slug[:max(0, 40 - len(suffix))]}{suffix}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title





def seed_demo_data():
    """Create demo data safely (call from a shell or management command).

    Returns a dict with lists of created objects for quick access.
    """
    # Skills
    skills = [
        Skills.objects.create(name='Python'),
        Skills.objects.create(name='JavaScript'),
        Skills.objects.create(name='React'),
        Skills.objects.create(name='Django'),
        Skills.objects.create(name='SQL'),
    ]

    # Users (use create_user to hash passwords)
    users = [
        User.objects.create_user(username='user1', email='user1@example.com', first_name='John', last_name='Doe', password='newpassword123'),
        User.objects.create_user(username='user2', email='user2@example.com', first_name='Jane', last_name='Smith', password='newpassword223'),
        User.objects.create_user(username='user3', email='user3@example.com', first_name='Michael', last_name='Johnson', password='newpassword323'),
        User.objects.create_user(username='user4', email='user4@example.com', first_name='Emily', last_name='Brown', password='newpassword423'),
        User.objects.create_user(username='user5', email='user5@example.com', first_name='David', last_name='Wilson', password='newpassword523'),
    ]

    # Authors
    authors = [
        Author.objects.create(user=users[0], company='ABC Corp', designation='Software Engineer'),
        Author.objects.create(user=users[1], company='XYZ Inc', designation='Web Developer'),
        Author.objects.create(user=users[2], company='123 Industries', designation='Full Stack Developer'),
        Author.objects.create(user=users[3], company='Tech Solutions', designation='Data Scientist'),
        Author.objects.create(user=users[4], company='Tech Innovations', designation='UI/UX Designer'),
    ]

    # Locations
    locations = [
        Location.objects.create(street='123 Main St', city='New York', state='NY', country='USA', zip='10001'),
        Location.objects.create(street='456 Elm St', city='Los Angeles', state='CA', country='USA', zip='90001'),
        Location.objects.create(street='789 Oak St', city='Chicago', state='IL', country='USA', zip='60001'),
        Location.objects.create(street='101 Pine St', city='San Francisco', state='CA', country='USA', zip='94101'),
        Location.objects.create(street='202 Maple St', city='Seattle', state='WA', country='98101'),
    ]

    # Job posts (expiry uses timezone-aware date)
    job_posts = [
        JobPost.objects.create(
            title='Python Developer',
            description='Looking for a skilled Python developer',
            expiry=timezone.now().date(),
            salary=80000,
            location=locations[0],
            author=authors[0],
        ),
        JobPost.objects.create(
            title='Frontend Developer',
            description='Hiring a frontend developer proficient in JavaScript and React',
            expiry=timezone.now().date(),
            salary=75000,
            location=locations[1],
            author=authors[1],
        ),
        JobPost.objects.create(
            title='Full Stack Developer',
            description='Join our team as a full stack developer',
            expiry=timezone.now().date(),
            salary=85000,
            location=locations[2],
            author=authors[2],
        ),
        JobPost.objects.create(
            title='Data Scientist',
            description='Exciting opportunity for a data scientist',
            expiry=timezone.now().date(),
            salary=90000,
            location=locations[3],
            author=authors[3],
        ),
        JobPost.objects.create(
            title='UI/UX Designer',
            description='Looking for a creative UI/UX designer',
            expiry=timezone.now().date(),
            salary=80000,
            location=locations[4],
            author=authors[4],
        ),
    ]

    # Many-to-many skills
    job_posts[0].skills.add(skills[0], skills[3])               # Python Developer -> Python, Django
    job_posts[1].skills.add(skills[1], skills[2])               # Frontend -> JavaScript, React
    job_posts[2].skills.add(skills[0], skills[1], skills[2], skills[3])
    job_posts[3].skills.add(skills[0], skills[4])               # Data Scientist -> Python, SQL
    # UI/UX Designer has no skills specified for variety

    return {
        'skills': skills,
        'users': users,
        'authors': authors,
        'locations': locations,
        'job_posts': job_posts,
    }





