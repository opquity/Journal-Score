from django.urls import path
from .views import *

urlpatterns = [
    path('', webUploadPDFView, name ='uploadFileView'),
    path('plugin-pdf/', PluginUploadPDFView.as_view()),
    path('plugin/', PluginWebScoreView.as_view()),
    path('journal-category/', JournalCategoryView.as_view()),
    # path('',home),
]
