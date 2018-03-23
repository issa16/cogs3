# cogs3

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

6. Create the database

	```sh
	python manage.py migrate
	```

5. Create an admin user

	```sh
	python manage.py createsuperuser
	```

6. Run the unit tests

	```sh
	python manage.py test
	```

7. Generate coverage report

	```sh
	coverage run manage.py test
	coverage html
	```

8. Start the development server

	```sh
	python manage.py runserver
	```


#### TODO

- Unit tests
- Shibboleth integration (Privacy Preserving Identity Management)
- User registration form

