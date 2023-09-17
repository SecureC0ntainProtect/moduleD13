from django.contrib import admin
from .models import Files, Comments, OneTimeCode


admin.site.register(Comments)
admin.site.register(Files)
admin.site.register(OneTimeCode)
