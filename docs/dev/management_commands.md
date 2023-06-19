# Management commands in Django

## Step 1: Create a Django App

If you haven't already, start by creating a Django app for your management commands. Open a terminal or command prompt, navigate to your project's root directory, and run the following command:

```sh
python manage.py startapp myapp
```

Replace **myapp** with the desired name for your app.

## Step 2: Create a Management Command File

Inside your newly created app directory **myapp**, create a directory called **management** (if it doesn't already exist). Within the management directory, create another directory called **commands**. This is where your management command files will reside.

Now, create a Python file inside the **commands** directory, with a name that reflects the purpose of your command. For example, let's call it **mycommand.py**. The file name will be the name of the management command.


## Step 3: Define the Command

Open **mycommand.py** in a text editor, and import the necessary modules:

```python
from django.core.management.base import BaseCommand
```

Next, create a subclass of **BaseCommand** to define your command:

```python
class Command(BaseCommand):
    help = 'Description of your command goes here.'

    def handle(self, *args, **options):
        # Logic for your command goes here
        self.stdout.write(self.style.SUCCESS('Command executed successfully.'))
```

Replace the '**Description of your command goes here.**' with a brief description of what your command does. The handle method is where you'll put your command's logic. For now, it simply outputs a success message.

## Step 4: Implement the Command Logic

Inside the handle method, you can add the code that performs the desired task for your management command. This could include database operations, data processing, file manipulation, or any other task you need to automate.

For example, let's say we want to create a command that prints all the usernames of registered users:

```python
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Prints the usernames of all registered users.'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            self.stdout.write(user.username)
```

## Step 5: Run the Command

Now that your management command is set up, you can run it from the command line. Open a terminal or command prompt, navigate to your project's root directory, and execute the following command:

```sh
python manage.py mycommand
```

Replace **mycommand** with the actual name of your command.



You should see the output of your command, which in our example would be the list of usernames.

That's it! You've created a custom management command in Django. You can now extend it with additional functionality or create more commands following the same pattern.

Remember to ensure that your Django app is included in the **INSTALLED_APPS** setting in your project's **settings.py** file, so that Django recognises your management commands.

# Examples

## Import Shibbolth user accounts from csv file

```python

# users/management/commands/import_shibboleth_users.py

import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import CustomUser, Profile

class Command(BaseCommand):
    help = 'Import Shibboleth user accounts from csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename')

    def handle(self, *args, **options):
        filename = options['csv_filename']
        try:
            with open(filename, newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            user, created = CustomUser.objects.get_or_create(
                                username=row['institutional_address'].lower(),
                                email=row['institutional_address'].lower(),
                                first_name=row['firstname'].title(),
                                last_name=row['surname'].title(),
                                is_shibboleth_login_required=True,
                            )
                            if created:
                                user.set_password(CustomUser.objects.make_random_password())
                                user.save()
                                message = 'Successfully created user account: {email}'.format(
                                    email=row['institutional_address']
                                )
                                self.stdout.write(self.style.SUCCESS(message))
                            else:
                                message = '{email} already exists.'.format(email=row['institutional_address'])
                                self.stdout.write(self.style.SUCCESS(message))

                            profile = user.profile
                            if not profile.hpcw_username:
                                profile.hpcw_username = row['hpcw_username'].lower()
                            if not profile.hpcw_email:
                                profile.hpcw_email = row['hpcw_email'].lower()
                            profile.raven_username = row['raven_username']
                            if row['raven_uid']:
                                profile.uid_number = int(row['raven_uid'])
                            profile.raven_email = row['raven_email'].lower()
                            profile.description = row['description']
                            profile.phone = row['phone']
                            profile.shibboleth_id = row['institutional_address'].lower()
                            profile.save()

                            message = 'Successfully updated user profile: {email}'.format(
                                email=row['institutional_address']
                            )
                            self.stdout.write(self.style.SUCCESS(message))
                    except Exception as e:
                        message = '{error}\n{row}'.format(error=e, row=row)
                        self.stdout.write(self.style.ERROR(message))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Unable to open ' + filename))

```

Here's a breakdown of the code:

1. The code defines a management command named Command, which extends the BaseCommand class.
2. The help attribute provides a brief description of the command's purpose.
3. The add_arguments method is overridden to specify a single required argument, which is the filename of the CSV file to import.
4. In the handle method, the provided CSV file is opened using the given filename.
5. The code reads the contents of the CSV file using csv.DictReader, which allows accessing rows as dictionaries.
6. A loop is set up to iterate over each row in the CSV file.
7. Inside the loop, the code attempts to create or retrieve a CustomUser instance using the data from the current row.
8. If a new user is created, a random password is generated, saved, and a success message is displayed.
9. If the user already exists, a message indicating that the user exists is displayed.
10. The associated Profile instance for the user is updated with data from the CSV file.
11. Success messages are displayed for each successful user account and profile update.
12. If an exception occurs during the execution of the code within the loop, an error message is displayed, including the exception details and the problematic row.
13. If the provided CSV file is not found, an error message is displayed.

To use this command, users can run the following command in the terminal, providing the path to the CSV file as an argument:

```sh
python manage.py import_shibboleth_users <csv_filename>
```


