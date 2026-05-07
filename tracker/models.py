from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    STATUS=[('ongoing','Ongoing'),('delayed','Delayed'),('ontrack','On Track')]
    name=models.CharField(max_length=100)
    status=models.CharField(max_length=20,choices=STATUS)
    deadline=models.CharField(max_length=50)
    completion=models.IntegerField(default=0)
    workers_count=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return self.name
class Worker(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    name=models.CharField(max_length=100)
    role=models.CharField(max_length=100)
    project=models.ForeignKey(Project,on_delete=models.SET_NULL,null=True)
    is_present=models.BooleanField(default=False)
    def __str__(self):
        return self.name
class DailyLog(models.Model):
    STATUS=[('done','Done'),('partial','Partial'),('issue','Issue')]
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    activity=models.CharField(max_length=200)
    status=models.CharField(max_length=20,choices=STATUS)
    logged_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.activity
class Issue(models.Model):
    PRIORITY=[('high','High'),('medium','Medium'),('low','Low')]
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    description=models.TextField()
    priority=models.CharField(max_length=20,choices=PRIORITY)
    assigned_to=models.CharField(max_length=100,blank=True)
    reported_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.description[:50]
