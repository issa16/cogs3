# cogs3

- [Demo](#demo)
- [Sequence Diagrams](#sequence-diagrams)
- [Getting started](#getting-started)

#### Demo

[Development server](http://147.143.49.105/accounts/login/)

#### Sequence Diagrams
- [Tech Lead Role Sequences](#tech-lead-role-sequences)
- [User Role Sequences](#user-role-sequences)

##### Tech Lead Role Sequences
![Tech Lead Role Sequences](docs/sequences/COGS3_Tech_Lead_Role_Sequences.png?raw=true "Tech Lead Role Sequences")

#### User Role Sequences
![User Role Sequences](docs/sequences/COGS3_User_Role_Sequences.png?raw=true "User Role Sequences")

#### Getting started

1. Checkout the source code

	```sh
	mkdir -p ~/code && cd $_
	git clone git@github.com:tystakartografen/cogs3.git
	```

2. Create a virtual environment

	```sh
	mkdir -p ~/vens/cogs3 && cd $_
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

