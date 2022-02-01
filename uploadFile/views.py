from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .fileOperation.pdfOperation import PDFFile
from .fileOperation.htmlOperation import HTMLFile
from .models import *
from .serializers import *

import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser


"""
********** Upload Category Admin ***********
"""


"""
*********** PDF Journal Score **************
"""


def webUploadPDFView(request):
    context = {}
    categories = JournalCategory.objects.all().values_list('name',flat=True)
    if categories:
        context['categories'] = categories
        #return render(request, 'uploadFile/index.html',context)

    if request.method == "POST":
        category = request.POST.get('category', False)
        file = request.FILES['file']
        if file.content_type == 'application/pdf':
            # fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT,'pdf'), base_url=os.path.join(settings.MEDIA_URL+'pdf'))
            # name = fs.save(uploaded_file.name,uploaded_file)
            # file_url = fs.url(name)
            # context['url'] = uploaded_file.name
            # context['category'] = category
            web_pdf = PluginUploadPDF()
            web_pdf.file = file
            web_pdf.category = category
            web_pdf.save()
            file_name = str(web_pdf.file).split('/')[-1]
            pdf = PDFFile(os.path.join(settings.MEDIA_ROOT,'pdf',file_name),category)
            context['url'] = file_name
            context['category'] = category
            context['score'] = str(pdf.main())
        return render(request, 'uploadFile/index.html',context) 
    return render(request, 'uploadFile/index.html', context)


class PluginUploadPDFView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        ser = PluginUploadPDFSerilaizer(data=request.data)
        try:
            ser.is_valid(raise_exception=True)
        except Exception as e:
            resp = {
                'errorMesssage': 'Please upload a pdf file',
                'resultCode': '0',
                'resultDescription': ser.errors
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        else:
            ser.save()
            file_name = ser.data['file'].split('/')[-1]
            category = ser.data['category']
            pdf = PDFFile(os.path.join(settings.MEDIA_ROOT,'pdf',file_name),category)
            score = str(pdf.main())
            resp = {
                'results':f'{score}',
                'resultCode':'1',
                'resultDescription':'Plugin PDF content score'
                }
            return Response(resp,status=status.HTTP_200_OK)


"""
*********** Plugin's Journal Category **************
"""


class JournalCategoryView(APIView):

    def get(self, request):
        categories = JournalCategory.objects.all()
        if categories:
            categories_ser = JournalCategorySerializer(categories, many=True)
            resp = {
                    'results': categories_ser.data,
                    'resultCode': '1',
                    'resultDescription': 'Journal categories'
                    }
            return Response(resp,status=status.HTTP_200_OK)
        resp = {
                'errorMessage': 'Journal categories missing',
                'resultCode': '0',
                'resultDescription': 'Journal categories missing'
                }
        return Response(resp,status=status.HTTP_200_OK)


"""
*********** Plugin Web Score **************
"""


class PluginWebScoreView(APIView):
    def post(self, request):
        plugin_data = request.data
        link = plugin_data.get('payload')
        category = plugin_data.get('strUser')
        if (link and category) is not None:
            plugin = HTMLFile(link,category)
            score = str(plugin.main())
            resp = {
                'results':f'{score}',
                'resultCode':'1',
                'resultDescription':'Web HTML content score'
                }
            return Response(resp,status=status.HTTP_200_OK)
        resp = {
            'errorMessage':'Technical error in fetching the data',
            'resultCode':'0',
            'resultDescription':'payload missing'}
        return Response(resp,status=status.HTTP_200_OK)


# from django.shortcuts import render

# def home(request):
#     return render(request, 'uploadFile/index.html')
