deploy_minor:
	python autocommit.py minor
	make push_tags
	make pypi_upload

deploy_medium:
	python autocommit.py medium
	make push_tags
	make pypi_upload

deploy_major:
	python autocommit.py major
	make push_tags
	make pypi_upload

deploy:
	make deploy_minor

push_tags:
	git push origin master --force
	git push --tags

pypi:
	#python setup.py sdist upload -r pypi || echo 'Workon is up-to-date'
	echo 'Ignoring'

pypi_upload:
	python setup.py sdist upload -r pypi || echo 'docker-emperor is up-to-date'

develop:
	# sudo pip install .
	python setup.py develop --user
	which de