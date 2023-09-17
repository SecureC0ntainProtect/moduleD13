import os
from random import randint

from django.dispatch import receiver
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import pre_delete, post_save
from django.conf.global_settings import EMAIL_HOST_USER

from .models import Notice, Files, OneTimeCode, MyUser, Comments


@receiver(pre_delete, sender=Notice)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    obj_files = Files.objects.filter(notice=instance)
    for file in obj_files:
        if os.path.isfile(file.File.path):
            os.remove(file.File.path)


@receiver(post_save, sender=MyUser)
def confirm_code_registration(sender, instance, created, **kwargs):
    if created:
        code_obj = OneTimeCode.objects.create(user=instance)
        while True:
            rand_code = randint(1000, 9999)
            if not OneTimeCode.objects.filter(code=rand_code).exists():
                code_obj.Code = rand_code
                code_obj.save()
                break

        html_content = render_to_string(
            'account/register_code_email.html',
            {
                'register_code': rand_code,
                'user': instance.username,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Код поддтверждения',
            from_email=EMAIL_HOST_USER,
            to=[instance.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    return redirect('/notice/')


@receiver(post_save, sender=Comments)
def email_response_to_user(sender, instance, created, **kwargs):
    if created:
        html_content = render_to_string(
            'notice/comment_added.html',
            {
                'post_id': instance.Notice_id,
                'post_title': instance.Notice.notice_title,
                'user': instance.Notice.notice_author,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Комментарий к объявлению',
            body="",
            from_email=EMAIL_HOST_USER,
            to=[instance.Notice.notice_author.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    else:
        if instance.Comment_accepted:
            html_content = render_to_string(
                'notice/comment_accepted.html',
                {
                    'post_id': instance.Notice_id,
                    'post_title': instance.Notice.notice_title,
                    'user': instance.User.username,
                }
            )

            msg = EmailMultiAlternatives(
                subject=f'Комментарий к объявлению',
                from_email=EMAIL_HOST_USER,
                to=[instance.User.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
