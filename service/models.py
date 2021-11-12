from django.db import models


class Review(models.Model):
    score = models.FloatField()
    contents = models.TextField()


class Waiting(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    leader = models.OneToOneField('Guest',
                                  on_delete=models.CASCADE,
                                  related_name='leader')
    member = models.ManyToManyField('Guest',
                                    related_name='member')


class Acceptation(models.Model):
    admission_date = models.DateTimeField(auto_now=True)
    waiting = models.ForeignKey(Waiting, on_delete=models.CASCADE)