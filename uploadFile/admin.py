from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(JournalCategory)
admin.site.register(PluginUploadPDF)
admin.site.register(MailCredential)
