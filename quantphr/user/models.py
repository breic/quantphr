from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# CODE to extend the User model with custom fields
#  see https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
# this includes info for how to make the admin pages show the UserProfile information on the User page
# e.g., http://digitaldreamer.net/blog/2010/12/8/custom-user-profile-and-extend-user-admin-django/
# also http://www.igorsobreira.com/blog/2010/12/11/extending-user-model-in-django/ , http://stackoverflow.com/questions/44109/extending-the-user-model-with-custom-fields-in-django
#  for interoperability with other apps, it seems best not to subclass User.  
# Here's how to add UserProfiles to existing Users (after ./manage.py sqlall and ./manage.py syncdb --all): import quantphr.user.models; for user in User.objects.all(): profile = quantphr.user.UserProfile(); profile.user = user; profile.save().  Then can use user.get_profile().institution to get at this data.
class UserProfile(models.Model):
	user = models.OneToOneField('auth.User')
		# extra fields: 
	institution = models.CharField(max_length=100, default='', null=True, blank=True)
	#avatar = models.ImageField(upload_to='uploads/avatars', default='', blank=True)
    #biography = models.TextField(default='', blank=True)
	def __unicode__(self):
		return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    """Create the UserProfile when a new User is saved"""
    if created:
        profile = UserProfile()
        profile.user = instance
        profile.save()
post_save.connect(create_user_profile, sender=User)	