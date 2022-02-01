from django.db import models
from django.utils import timezone
from os.path import splitext

class JournalCategory(models.Model):
    name = models.CharField(max_length=400)
    jif = models.FloatField()
    class Meta:
        db_table = 'JournalCategory'
        verbose_name_plural = "Journal categories"

def plugin_pdf_upload_to(instance, filename):
    now = timezone.now()
    base, extension = splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"pdf/{base}{now:%Y%m%d%H%M%S}{milliseconds}{extension}"


class PluginUploadPDF(models.Model):
    file = models.FileField(upload_to=plugin_pdf_upload_to,
                            blank=False,
                            null=False)
    category = models.CharField(max_length=400)

class MailCredential(models.Model):
    sender_mail = models.CharField(max_length=100)
    sender_pwd = models.CharField(max_length=100)
    receiver_mail = models.CharField(max_length=100)
