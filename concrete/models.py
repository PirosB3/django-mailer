from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)


class Comment(models.Model):
    body = models.CharField(max_length=100)
    post = models.ForeignKey(Post)
