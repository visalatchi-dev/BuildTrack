from django.contrib import admin
from .models import Project, Worker, DailyLog, Issue

admin.site.register(Project)
admin.site.register(Worker)
admin.site.register(DailyLog)
admin.site.register(Issue)