from django.db import models

class DocumentAccess(models.Model):
    level_name = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255)
    doc_file_name = models.CharField(max_length=255)
    doc_title = models.CharField(max_length=255)

    def __str__(self):
        return self.doc_title
