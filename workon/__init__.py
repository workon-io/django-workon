import os
default_app_config = 'workon.conf.WorkonConfig'

if os.environ.get('DJANGO_SETTINGS_MODULE'):

	from workon.utils import *
	from workon.views import *
	from workon.fields import *

	# from workon.models.tracked import (
	# 	Tracked as TrackedModel
	# )