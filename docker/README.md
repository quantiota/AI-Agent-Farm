# Docker

You will find all the Docker services set up in this folder.

## Services

### VSCode

:link: [docker image](https://hub.docker.com/r/codercom/code-server)
:link: [github repository](https://github.com/coder/code-server)

Acces VSCode through [localhost:8080](http://localhost:8080).

### QuestDB

:link: [docker image](https://hub.docker.com/r/questdb/questdb)
:link: [github repository](https://github.com/questdb/questdb)

Acces QuestDB GUI through [localhost:9000](http://localhost:9000).
Access the database using [localhost:8812](localhost:8812).

:lock:
The user/password are the default one: `admin:quest` ([see the documentation](https://questdb.io/docs/reference/configuration/#postgres-wire-protocol)) and the database name is `qdb`.

### Grafana

:link: [docker image](https://hub.docker.com/r/grafana/grafana)
:link: [github repository](https://github.com/grafana/grafana)

Acces Grafana through [localhost:3000](http://localhost:3000).

:lock:
The user/password are the default one: `admin:admin`.
You can add set the password adding the environment variable `GF_SECURITY_ADMIN_PASSWORD`.

## Usage

You can up the stack using the command:

```bash
docker-compose up
```

A `.volumes` folder will be created to store the data of the different services.