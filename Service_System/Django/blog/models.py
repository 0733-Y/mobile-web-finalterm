from django.conf import settings
from django.db import models
from django.utils import timezone


class Space(models.Model):
    """학습 공간 (도서관 열람실, 스터디룸 등)."""
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(help_text='좌석 수')
    has_outlet = models.BooleanField(default=False, help_text='콘센트 유무')

    def __str__(self):
        return self.name


class Post(models.Model):
    """Edge가 업로드하는 스냅샷 (Image Blog 글)."""
    LEVEL_FREE = '여유'
    LEVEL_NORMAL = '보통'
    LEVEL_CROWDED = '혼잡'
    LEVEL_CHOICES = [
        (LEVEL_FREE, '여유'),
        (LEVEL_NORMAL, '보통'),
        (LEVEL_CROWDED, '혼잡'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    # --- SpaceCheck 추가 필드 ---
    space = models.ForeignKey(Space, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='posts')
    person_count = models.PositiveIntegerField(default=0)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True)

    class Meta:
        ordering = ['-published_date', '-created_date']

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
