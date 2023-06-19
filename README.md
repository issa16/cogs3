<p align="center">
   <h3 align="center">cogs3</h3>
</p>
<p align="center">
   Project Management System
</p>

- [Development](#development)
- [Sequence Diagrams](#sequence-diagrams)

## Development

1. Checkout the source code.

   ```sh
   mkdir -p ~/code && cd $_
   git clone git@github.com:issa16/cogs3.git
   ```

2. Create an env file.

   ```sh
   cd cogs3
   mv cogs3/.template_env cogs3/.env
   ```
   
3. Build and run.

   ```sh
   docker-compose up -d
   ```
   
   Note: If docker-compose hangs when creating the *cogs3_web_1* container, you may need to add the *cogs3* directory to the list of file sharing resources.

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
   ./load_fixtures
   ```

7. Create an admin user.

   ```sh
   python3 manage.py createsuperuser
   ```

8. Run the unit tests.

   ```sh
   python3 manage.py test -v 3
   ```

9. Generate coverage report.

      ```sh
      coverage run manage.py test
      coverage html
      ```

10. Enter ```http://localhost:5000/``` in a browser to see the application running.


## Sequence Diagrams

- [User Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20User%20Role%20Sequences.pdf)
- [Tech Lead Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20Tech%20Lead%20Role%20Sequences.pdf)
- [RSE Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20RSE%20Role%20Sequences.pdf)
- [Sysadmin Role Sequences](https://github.com/issa16/cogs3/blob/master/docs/sequences/COGS3%20Sysadmin%20Role%20Sequences.pdf)
