from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

""" 
This class inherits from UserCreationForm to override the __init__ method
in order to not show the 'usable_password' field in the final form
"""
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the "usable_password" field if it exists
        if 'usable_password' in self.fields:
            self.fields.pop('usable_password')

"""
This model is destined to elaborate the tasks table 
"""
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    completiondate = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 

    # Method used to show the title and owner of a task
    def __str__(self):
        return self.title + ' - by ' + self.user.username
