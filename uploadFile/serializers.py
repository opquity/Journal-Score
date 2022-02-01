from rest_framework import serializers
from .models import *


class JournalCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalCategory
        fields = ['name']


class PluginUploadPDFSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = PluginUploadPDF
        fields = '__all__'
