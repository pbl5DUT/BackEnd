# models/knowledge_article.py
from django.db import models
from api.models.knowledge_category import KnowledgeCategory

class KnowledgeArticle(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    categoryId = models.CharField(max_length=50)
    createdBy = models.CharField(max_length=50)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    viewCount = models.IntegerField(default=0)
    likeCount = models.IntegerField(default=0)
    isFeatured = models.BooleanField(default=False)
    isPublished = models.BooleanField(default=True)
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_knowledgearticle'