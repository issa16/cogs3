# cogs3

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2e041aee6a4846089f8aedc228c56254)](https://app.codacy.com/app/tystakartografen/cogs3?utm_source=github.com&utm_medium=referral&utm_content=tystakartografen/cogs3&utm_campaign=badger)
[![Build Status](https://travis-ci.org/tystakartografen/cogs3.svg?branch=master)](https://travis-ci.org/tystakartografen/cogs3) [![codecov](https://codecov.io/gh/tystakartografen/cogs3/branch/master/graph/badge.svg)](https://codecov.io/gh/tystakartografen/cogs3) [![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/tystakartografen/cogs3/blob/master/LICENSE.md)

- [Demo](#demo)
- [Sequence Diagrams](#sequence-diagrams)
- [Getting started](#getting-started)

#### Demo

[Development server](https://scw.bangor.ac.uk/)

#### Sequence Diagrams
- [User Role Sequences](https://github.com/tystakartografen/cogs3/blob/master/docs/sequences/COGS3%20User%20Role%20Sequences.pdf)
- [Tech Lead Role Sequences](https://github.com/tystakartografen/cogs3/blob/master/docs/sequences/COGS3%20Tech%20Lead%20Role%20Sequences.pdf)
- [RSE Role Sequences](https://github.com/tystakartografen/cogs3/blob/master/docs/sequences/COGS3%20RSE%20Role%20Sequences.pdf)
- [Sysadmin Role Sequences](https://github.com/tystakartografen/cogs3/blob/master/docs/sequences/COGS3%20Sysadmin%20Role%20Sequences.pdf)

#### Getting started

1. Checkout the source code

	```sh
	mkdir -p ~/code && cd $_
	git clone git@github.com:tystakartografen/cogs3.git
	```

2. Create a virtual environment

	```sh
	mkdir -p ~/venvs/cogs3 && cd $_
	virtualenv -p /usr/local/bin/python3 .
	source bin/activate
	```

3. Install the requirements

	```sh
	cd ~/code/cogs3
	pip install -r requirements.txt
	```

4. Configure the environment variables ​

	```sh
	cd cogs3
	mv .template_env .env
	```

	Update .env

5. Create the database

	```sh
	python manage.py migrate
	```

6. Load institution data into the database, default institution data is available in fixtures

	```sh
	python manage.py loaddata institutions.yaml
	```
7. Create an admin user

	```sh
	python manage.py createsuperuser
	```

8. Run the unit tests

	```sh
	python manage.py test
	```

9. Generate coverage report

	```sh
	coverage run manage.py test
	coverage html
	```

10. Start the development server

	```sh
	python manage.py runserver
	```

