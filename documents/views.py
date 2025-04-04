from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.utils.timezone import now
from datetime import timedelta
from django.core.cache import cache

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
def view_file(request, doc_title):
     
    cache_key = f"accessed_doc_{doc_title}"  # Unique cache key for the document
    access_time = cache.get(cache_key)

    accessed_docs = request.session.get('accessed_docs', {})

    # If session exists and time expired, deny access
    # if str(doc_id) in accessed_docs:
    #     access_time = accessed_docs[str(doc_id)]
    #     if now() > access_time + timedelta(minutes=2):  # Expires after 2 minutes
    #         del accessed_docs[str(doc_id)]  
    #         request.session['accessed_docs'] = accessed_docs
    #         # return HttpResponse("<h3 style='color:red;'>URL expired. Please request access again.</h3>", status=403)
    #         return render(request, "documents/expired.html")
    #     else:
    #             del accessed_docs[str(doc_id)]  
    #             request.session['accessed_docs'] = accessed_docs
    #             # return HttpResponse("<h3 style='color:red;'>URL expired. Please request access again.</h3>", status=403)
    #             return render(request, "documents/expired.html")


    # else:
    #     accessed_docs[str(doc_id)] = now()
    #     request.session['accessed_docs'] = accessed_docs
        # request.session.modified = True  # Ensure session updates


    if access_time:
        # If access exists but has expired, deny access permanently
        if now() > access_time + timedelta(minutes=10):  
            return render(request, "documents/expired.html")
        else:
            return render(request, "documents/expired.html")

    else:
        # Store access time in cache (valid for 10 minutes)
        cache.set(cache_key, now(), timeout=600)  # 600 seconds timeout

    # return render(request, "documents/view_file.html", {"doc_id": doc_id})

    with connection.cursor() as cursor:
        cursor.execute("SELECT doc_file, doc_file_name , action_status1 FROM document_access WHERE doc_title = %s", [doc_title])
        row = cursor.fetchone()
    
  

        if row and row[0]:
            file_data = row[0]  # BLOB data
            file_name = row[1] if row[1] else f'document_{doc_title}.pdf'
            action_status1 = row[2]

            if action_status1 =='Approved':
                # Open directly in browser
                response = HttpResponse(file_data, content_type='application/pdf')
                response['Content-Disposition'] = 'inline'  # Opens in browser
                return response
            
            else : 
                return HttpResponse("This document is not yet approved!")
        # if row:
        #     file_name = row[0] if row[0] else f'document_{doc_id}.pdf'
        #     file_url = f"/media/documents/{file_name}"  # Assuming files are served from /media/documents/

        #     return render(request, "documents/view_file.html", {"file_url": file_url})
        else:
            # return HttpResponse("File not found", status=404)
            return HttpResponse("Please enter correct grade and try again!", status=404)
    

# # ✅ Download file
# def download_file(request, doc_id):
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT doc_file, doc_file_name FROM document_access WHERE DOC_id = %s", [doc_id])
#         row = cursor.fetchone()
    
#     if row and row[0]:
#         file_data = row[0]  # BLOB data
#         file_name = row[1] if row[1] else f'document_{doc_id}.pdf'
        
#         # Prompt file download
#         response = HttpResponse(file_data, content_type='application/octet-stream')
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response
#     else:
#         return HttpResponse("File not found", status=404)
    


# def clear_session(request):
#     request.session.flush()  # Clears session data on refresh
#     return HttpResponse("<h3 style='color:red;'>Session Refreshed! Please request access again.</h3>", status=403)

def clear_session(request):
    # """Clear session and redirect to document list"""
    request.session.flush()  # Clears session data
    return redirect('document_list')

def expired_view(request):
    return render(request, "documents/expired.html")

