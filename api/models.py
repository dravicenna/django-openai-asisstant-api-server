# Create your models here.
import telebot.types as types
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Manager, QuerySet
from openai.types.beta.threads.thread_message import ThreadMessage

from hotel_bot.utils import extract_message


class CreateTracker(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class CreateUpdateTracker(CreateTracker):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(CreateTracker.Meta):
        abstract = True


class GetOrNoneManager(models.Manager):
    """returns none if object doesn't exist else model instance"""

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


def extract_user_data_from_update(message: types.Message):
    user = message.json['from']
    return dict(
        user_id=user['id'],
        **{
            k: user[k]
            for k in ['username', 'first_name', 'last_name', 'language_code']
            if k in user and user[k] is not None
        },
    )


class Thread(CreateUpdateTracker):
    messages: QuerySet
    user: QuerySet
    thread_id = models.CharField(max_length=100)


class Message(CreateUpdateTracker):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    text_input = models.TextField(null=True, blank=True)
    text_output = models.TextField(null=True, blank=True)
    annotations = models.TextField(null=True, blank=True)
    assistant_id = models.CharField(max_length=100, null=True, blank=True)
    run_id = models.CharField(max_length=100, null=True, blank=True)
    platform = models.CharField(max_length=100, default='webapp')

    # About what a conversation was
    topic = models.CharField(max_length=100, null=True, blank=True, default='None')

    @classmethod
    def save_conversation(cls, messages: list[ThreadMessage], assistant_id: str, thread_id: str, platform: str):
        if len(messages) > 2:
            thread = Thread.objects.get(thread_id=thread_id)
            input = messages[1]
            output = messages[0]
            text_input = extract_message(input)
            text_output = extract_message(output)
            if text_input != text_output:
                obj = {
                    'text_input': text_input,
                    'text_output': text_output,
                    'assistant_id': output.assistant_id or assistant_id,
                    'run_id': output.run_id or '',
                    'platform': platform,
                }
                cls.objects.create(thread=thread, **obj)


class Run(CreateUpdateTracker):
    run_id = models.CharField(max_length=100, primary_key=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='runs')
    assistant_id = models.CharField(max_length=32)
    created_at = models.DateTimeField()
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_error_code = models.CharField(max_length=50, null=True, blank=True)
    last_error_message = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    prompt_tokens = models.PositiveIntegerField()
    completion_tokens = models.PositiveIntegerField()
    total_tokens = models.PositiveIntegerField()


class TelegramUser(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    thread = models.OneToOneField(Thread, on_delete=models.CASCADE, null=True, blank=True, related_name='user')
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", null=True, blank=True)
    deep_link = models.CharField(max_length=64, null=True, blank=True)
    is_blocked_bot = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, message: types.Message):
        """python-telegram-bot's Update, Context --> User instance"""
        data = extract_user_data_from_update(message)
        u, created = cls.objects.update_or_create(user_id=data['user_id'], defaults=data)

        if created:
            u.save()

        return u, created

    @classmethod
    def get_user(cls, message: types.Message):
        u, _ = cls.get_user_and_created(message)
        return u

    def record_action(self, action: str):
        """Record user action"""
        return UserAction.objects.create(user=self, action=action)


class UserAction(CreateTracker):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    objects = GetOrNoneManager()

    def __str__(self):
        return f'{self.user} ask {self.action} at {self.created_at.strftime("(%H:%M, %d %B %Y)")}'


# class KnowledgeFile(CreateUpdateTracker):
#     file_id = models.CharField(max_length=100, primary_key=True)
#     filename = models.CharField(max_length=100)
#     purpose = models.CharField(max_length=100, default='assistants')


# class AssistantTool(CreateUpdateTracker):
#     description = models.CharField(max_length=255)
#     name = models.CharField(max_length=50)
#     parameters = models.JSONField()


# class Assistant(CreateUpdateTracker):
#     assistant_id = models.CharField(max_length=100, primary_key=True)
#     name = models.CharField(max_length=100, null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#     model = models.CharField(max_length=100)
#     instructions = models.TextField(null=True, blank=True)
#     is_code_interpreter = models.BooleanField(default=False)
#     is_retrieve = models.BooleanField(default=False)
#     files = models.ManyToManyField(KnowledgeFile, related_name='assistants')
#     tools = models.ManyToManyField(AssistantTool, related_name='assistants')
#     objects = GetOrNoneManager()
