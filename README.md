# cogs3

### Demo

[Development demo](http://147.143.49.105/accounts/login/)

Email aaron.owen@bangor.ac.uk for demo account access.

### Flow

1. A technical user logs in and completes a project application form. 
2. A SCW admin reviews the project application, if the application is successful the project is approved and assigned a project code.
3. The technical user distributes the project code to selected users.
4. The users log in and request membership to the project using the project code.
5. The technical user approves the users project membership requests.


### Development

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


### TODO

- Unit tests
- Shibboleth integration (Privacy Preserving Identity Management)
- User registration form

