<p align="center">
   <h3 align="center">cogs3</h3>
</p>
<p align="center">
   Project Management System
</p>

---
   [![Build Status](https://travis-ci.org/issa16/cogs3.svg?branch=master)](https://travis-ci.org/issa16/cogs3)
   [![codecov](https://codecov.io/gh/issa16/cogs3/branch/master/graph/badge.svg)](https://codecov.io/gh/issa16/cogs3)
   [![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/issa16/cogs3/blob/master/LICENSE.md)
---

- [Development](#development)
- [Deployment](#deployment)
- [Sequence Diagrams](#sequence-diagrams)

---

#### Development

---

1. Checkout the source code.

   ```sh
   mkdir -p ~/code && cd $_
   git clone git@github.com:issa16/cogs3.git
   ```

2. Create an env file.

   ```sh
   mv cogs3/.template_env cogs3/.env
   ```
   
3. Build and run.

   ```sh
   cd cogs3
   docker-compose up -d
   ```

4. Obtain an SSH connection to the *cogs3_web_1* container.

   ```sh
   docker ps
   docker exec -it <id_of_cogs3_web_1_container> bash
   ```

5. Run the database migrations.

   ```sh
   python3 manage.py migrate
   ```

6. Load data fixtures into the database.

   ```sh
   python3 manage.py loaddata institutions.json
   python3 manage.py loaddata systems.json
   ```

7. Create an admin user.

   ```sh
   python3 manage.py createsuperuser
   ```

8. Generate history tables.

   ```sh
   python3 manage.py populate_history --auto
   ```

9. Run the unit tests.

   ```sh
   python3 manage.py test -v 3
   ```

10. Generate coverage report.

      ```sh
      coverage run manage.py test
      coverage html
      ```

11. Enter ```http://localhost:5000/``` in a browser to see the application running.

---

#### Deployment

---

If you are running a production server with at least one institution and cluster that makes use of priority calculations, then set up the requisite Cron jobs to update priorities daily, as described in [the priority README](priority/README.md).

---

#### Sequence Diagrams

---

- [User Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20User%20Role%20Sequences.pdf)
- [Tech Lead Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20Tech%20Lead%20Role%20Sequences.pdf)
- [RSE Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20RSE%20Role%20Sequences.pdf)
- [Sysadmin Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20Sysadmin%20Role%20Sequences.pdf)
