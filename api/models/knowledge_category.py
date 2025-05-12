# models/knowledge_category.py
from django.db import models

class KnowledgeCategory(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    iconUrl = models.CharField(max_length=255, blank=True, null=True)
    createdBy = models.CharField(max_length=50)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    articleCount = models.IntegerField(default=0)
    parentId = models.CharField(max_length=50, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'api_knowledgecategory'