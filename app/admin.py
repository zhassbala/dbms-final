from django.contrib import admin
from .models import exports

for model in exports:
    admin.site.register(model)

# Register your models here.
