from django.db import models
from django.urls import reverse

from users.models import MyUser


class Notice(models.Model):
    GUILDS = (
        ('TK', 'Танки'),
        ('HL', 'Хилеры'),
        ('DD', 'ДД'),
        ('TD', 'Торговцы'),
        ('GM', 'Гилдмастеры'),
        ('QG', 'Квестгиверы'),
        ('BS', 'Кузнецы'),
        ('LD', 'Кожевники'),
        ('PN', 'Зельевары'),
        ('MS', 'Мастера заклинаний'),
    )

    notice_author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    notice_title = models.CharField(max_length=255)
    notice_text = models.TextField(default='Текст объявления')
    category = models.CharField(max_length=2, choices=GUILDS)

    def __str__(self):
        return self.notice_title

    def get_absolute_url(self):
        return reverse('notice', kwargs={'pk': self.pk})


class Files(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    name = models.CharField(default='file-name', max_length=255)
    file = models.FileField(upload_to='', blank=True, null=True)
    file_type = models.TextField(default='jpg')

    def save(self, *args, **kwargs):
        img_ending = {'jpg', 'png', 'img'}
        self.name = self.file.name
        check_img = {self.name.split(".")[-1]}
        if check_img.intersection(img_ending):
            self.file_type = 'img'
        else:
            self.file_type = 'video'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Comments(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    comment = models.TextField(default='Комментарий')
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.comment


class OneTimeCode(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    code = models.CharField(default="", max_length=4)

    def __str__(self):
        return f'{self.user} - {self.code}'
