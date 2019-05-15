# Welcome to Muesli Machine!

...

This project is being worked on hard - in every free minute. Unfortunately there are not many of them.

Also on the readme should be worked hard...

...
### How to set it up ###
1. Clone repository
2. Go to new local repository folder, e.g. with `cd mueslimachine/`
3. Change MySQL root password in `.env` file! (This file is hidden in some file browsers.)\
Here you can also change:
    - web app port
    - database port
    - database name
4. Let create containers via Docker Compose: `docker-compose up`
    - Container **Muesli_Machine_App** for Python Plesk web app
    - Container **Muesli_Machine_MySQL** for MySQL database
      - Muesli_Machine_MySQL container creates a `db/ folder for MySQL files
5. Open `http://localhost/` (or with the port that you have specified).