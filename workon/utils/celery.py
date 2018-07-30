# import celery.app
# from celery import Celery
# from celery.schedules import crontab
# import celery.app



# def periodic_tasks(period=crontab('*'), args=(), expires=None):

#     def original(func):
#         return func

#     self.add_periodic_task(
#         period, original.s(*args), expires=expires
#     )
#     print(original)

#     return original

# setattr(celery.app, 'periodic_tasks', periodic_tasks)
