from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

DAYS_OF_WEEK = [
    ('SU', 'Sunday'),
    ('MO', 'Monday'),
    ('TU', 'Tuesday'),
    ('WE', 'Wednesday'),
    ('TH', 'Thursday'),
    ('FR', 'Friday'),
    ('SA', 'Saturday'),
]

@receiver(post_migrate)
def create_menus(sender, **kwargs):
    Menu=apps.get_model('base','Menu')
    
    i=0
    for day, _ in DAYS_OF_WEEK:
        Menu.objects.get_or_create(day_of_week=day,sequence=i)
        i+=1