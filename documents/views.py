from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse , JsonResponse
from django.utils.timezone import now
from datetime import timedelta
from django.core.cache import cache
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from .utils import create_one_time_token

#  List documents
def document_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DOC_id, level_name, department_name, doc_file_name, doc_title FROM document_access")
        rows = cursor.fetchall()
    
    documents = [
        {
            'doc_id': row[0],
            'level_name': row[1],
            'department_name': row[2],
            'doc_file_name': row[3],
            'doc_title': row[4],
        }
        for row in rows
    ]
    
    return render(request, 'documents/document_list.html', {'documents': documents})


def fetch_pdf(request, doc_title):
    with connection.cursor() as cursor:
        cursor.execute("SELECT doc_file FROM document_access WHERE doc_title = %s", [doc_title])
        row = cursor.fetchone()
    
    if row and row[0]:
        file_data = row[0]  # BLOB data
        # file_name = row[1] if row[1] else f'document_{doc_id}.pdf'
        
        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = 'inline'  # Open in browser
        return response
    else:
        return HttpResponse("File not found", status=404)



#  View file directly in browser

SECRET_KEY = 'mes-dolvi-rolling-protocol'

def view_file(request, doc_title):
    token = request.GET.get('token')  # or request.headers.get('Authorization')

    if not token:
        # return HttpResponse("Token missing", status=401)
        token = create_one_time_token(doc_title)
        return redirect(f"{request.path}?token={token}")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        jti = payload.get('jti')

        if not jti:
            return HttpResponse("Invalid token", status=401)

     
        if cache.get(f'used_jti_{jti}'):
            return render(request, "documents/expired.html")

       
        cache.set(f'used_jti_{jti}', True, timeout=600)  # Store for 10 minutes

    except ExpiredSignatureError:
        return render(request, "documents/expired.html")
    except InvalidTokenError:
        return HttpResponse("Invalid token", status=401)

   
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT doc_file, doc_file_name, action_status1 FROM document_access WHERE doc_title = %s",
            [doc_title]
        )
        row = cursor.fetchone()

        if row and row[0]:
            file_data = row[0]
            file_name = row[1] if row[1] else f'document_{doc_title}.pdf'
            action_status1 = row[2]

            if action_status1 == 'Prepared':
                response = HttpResponse(file_data, content_type='application/pdf')
                response['Content-Disposition'] = 'inline'
                return response
            else:
                return HttpResponse("This document is not yet approved!")
        else:
            return HttpResponse("Please enter correct grade and try again!", status=404)


def clear_session(request):
    # """Clear session and redirect to document list"""
    request.session.flush()  # Clears session data
    return redirect('document_list')

def expired_view(request):
    return render(request, "documents/expired.html")

