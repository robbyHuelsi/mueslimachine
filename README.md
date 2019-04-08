# mueslimachine

...

project work in progress - also readme...

...
### How to setup ###
1. Clone repository
2. Go to new local repository folder, e.g. with `cd mueslimachine/`
2. Change MySQL root password in `.env` file! Here you can also change web app, database port and database name.
3. Let create containers via Docker Compose: `docker-compose up`
    * Container **mmApp** for Python Plesk web app
    * Container **mmMySQL** for MySQL database
      - mmMySQL container creates a `db/ folder for MySQL files