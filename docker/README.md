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

Acces QuestDB through [localhost:9000](http://localhost:9000).

### Grafana

:link: [docker image](https://hub.docker.com/r/grafana/grafana)
:link: [github repository](https://github.com/grafana/grafana)

Acces Grafana through [localhost:3000](http://localhost:3000).

## Usage

You can up the stack using the command:

```bash
docker-compose up
```

A `.volumes` folder will be created to store the data of the different services.