from django.db import models
from users.models import User

class Video(models.Model):
    title = models.CharField(max_length=128, null=False, blank=False)
    url = models.CharField(max_length=128, null=False, blank=False)
    youtubeID = models.CharField(max_length=16, null=False, blank=False)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    visibility = models.CharField(max_length=16, null=False, blank=False, default='private')

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

class VideoTag(models.Model):
    video = models.ForeignKey(Video, null=False, blank=False, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=False, blank=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return 'Video: ' + self.video.title + ' Tag: ' + self.tag.name


class VideoList(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    videos = models.ManyToManyField(Video, through='VideoListItem')
    owner = models.ForeignKey(User, default=None, null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
class VideoListItem(models.Model):
    videoList = models.ForeignKey(VideoList, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.video.title

    def show_tags(self):    
        tags = 'Aqui se mostraran los tags, esta en progreso'
        return tags
    