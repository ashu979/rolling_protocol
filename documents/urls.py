from django.urls import path
from django.shortcuts import render
from .views import document_list, view_file , clear_session,fetch_pdf,expired_view




urlpatterns = [
    path('', document_list, name='document_list'),
    path('view/<str:doc_title>/', view_file, name='view_file'),
    # path('download/<int:doc_id>/', download_file, name='download_file'),
    path("pdf/<int:doc_id>/", fetch_pdf, name="fetch_pdf"),
    path('clear-session/', clear_session, name='clear_session'),
    path("expired/", expired_view, name="expired_page"),
]
