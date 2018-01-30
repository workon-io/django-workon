deploy_minor:
	python autocommit.py minor
	make push_tags
	make pypi

deploy_medium:
	python autocommit.py medium
	make push_tags
	make pypi

deploy_major:
	python autocommit.py major
	make push_tags
	make pypi

deploy:
	make deploy_minor

push_tags:
	git push origin master
	git push --tags

pypi:
	python setup.py sdist upload -r pypi || echo 'Workon is up-to-date'