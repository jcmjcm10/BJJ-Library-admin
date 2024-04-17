from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=128, null=False, blank=True)
    url = models.CharField(max_length=128, null=False, blank=True)
    youtubeID = models.CharField(max_length=16, null=False, blank=True)

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

class VideoTag(models.Model):
    video = models.ForeignKey(Video, null=False, blank=True, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=False, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return 'Video: ' + self.video.title + ' Tag: ' + self.tag.name
