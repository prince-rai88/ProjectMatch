from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from matcher.models import Profile

class Command(BaseCommand):
    help = 'Seed database with demo profiles'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        users_data = [
            {'username': 'alice', 'email': 'alice@example.com', 'skills': 'Python, Django', 'interests': 'Web Dev', 'availability': 'weekends', 'experience_level': 'intermediate', 'looking_for': 'A cool open source project'},
            {'username': 'bob', 'email': 'bob@example.com', 'skills': 'React, JS', 'interests': 'Frontend', 'availability': 'evenings', 'experience_level': 'advanced', 'looking_for': 'Backend developer to team up'},
        ]
        
        for data in users_data:
            user, created = User.objects.get_or_create(username=data['username'], email=data['email'])
            if created:
                user.set_password('password123')
                user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'skills': data['skills'],
                    'interests': data['interests'],
                    'availability': data['availability'],
                    'experience_level': data['experience_level'],
                    'looking_for': data['looking_for'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded demo profiles.'))
