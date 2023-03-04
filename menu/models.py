from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Menu(models.Model):
    name = models.CharField(max_length=125)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    namespace = models.CharField(max_length=125, blank=True, null=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu', blank=True, null=True)

    def __str__(self):
        return f'{self.title} {self.url if self.url else self.namespace}'

    def get_url(self):
        if self.namespace:
            return reverse(self.namespace)
        return self.url

    def save(self, **kwargs):
        if not self.url and not self.namespace:
            raise ValidationError(
                'At least one of the two fields MenuItem (url, namespace) must be filled in'
            )
        if self.namespace:
            reverse(self.namespace)
        super().save(**kwargs)
