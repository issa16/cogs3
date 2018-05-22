# ![cogs3](cogs3.svg) cogs3

[![Build Status](https://travis-ci.org/tystakartografen/cogs3.svg?branch=master)](https://travis-ci.org/tystakartografen/cogs3) [![codecov](https://codecov.io/gh/tystakartografen/cogs3/branch/master/graph/badge.svg)](https://codecov.io/gh/tystakartografen/cogs3) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c98d95ae20094f32aea3f40dd83f55e0)](https://www.codacy.com/app/tystakartografen/cogs3?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tystakartografen/cogs3&amp;utm_campaign=Badge_Grade) [![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/tystakartografen/cogs3/blob/master/LICENSE.md)

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

1. Checkout the source code.

  ```sh
  mkdir -p ~/code && cd $_
  git clone git@github.com:tystakartografen/cogs3.git
  ```

2. Create a virtual environment.

  ```sh
  mkdir -p ~/venvs/cogs3 && cd $_
  virtualenv -p /usr/local/bin/python3 .
  source bin/activate
  ```

  Replace `/usr/local/bin/python3` with the path to a Python 3 executable.
  On macOS this should be installed from Homebrew.

3. Install the requirements.

  ```sh
  cd ~/code/cogs3
  pip install -r requirements.txt
  ```

4. Configure the environment variables.

  ```sh
  cd cogs3
  mv .template_env .env
  ```

5. Edit `.env` to include, at a minimum, an arbitrary `SECRET_KEY`.
   Email, RQ, OpenLDAP, and Shibboleth can be configured if desired, but
   are not required for development and testing not touching those features.

6. Create the database.

  ```sh
  cd ..
  python manage.py migrate
  ```

7. Load data fixtures into the database.

  ```sh
  python manage.py loaddata institutions.yaml
  python manage.py loaddata systems.yaml
  ```

8. Create an admin user.

  ```sh
  python manage.py createsuperuser
  ```

9. Install geckodriver.

  macOS
  ```sh
  brew install geckodriver
  ```

  Linux

  ```sh
  wget https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-linux64.tar.gz
  tar -xzf geckodriver-v0.20.1-linux64.tar.gz
  chmod +x geckodriver
  sudo mv geckodriver /usr/local/bin
  rm geckodriver-v0.20.1-linux64.tar.gz
  ```

10. Run the unit tests.

  ```sh
  python manage.py test -v 3
  ```

11. Generate coverage report.

  ```sh
  coverage run manage.py test
  coverage html
  ```

12. Install redis.

  ```sh
  brew install redis
  ```

  Replace `brew` with your package manager. On Debian and Ubuntu, the package
  is named `redis-server`; i.e.

  ```sh
  sudo apt install redis-server
  ```

13. Start the redis server.

  ```sh
  redis-server &
  ```

14. Test redis server is running.

   ```sh
   redis-cli ping
   >>> PONG
   ```

15. Start the development server.

  ```sh
  python manage.py runserver
  ```


