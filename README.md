# SSLA Manager REST API

Implements a REST API for the [SSLA manager module](https://github.com/ThalesGroup/ssla-manager) and to manage SSLAs remotely.

## Quick start

Install :

```sh
podman build -f ./Containerfile -t localhost/thales-sslamanager-rest
```

Run :

```sh
touch /tmp/ssla.db
podman run -d \
  --name ssla-manager \
  -p 8081:80 \
  -v /tmp/ssla.db:/data/ssla.db \
  localhost/thales-sslamanager-rest
```

Try it in your browser at `localhost:8080/docs`.  
You can use the examples in `examples/ssla/` to submit security policies.  

## OpenAPI specs

Read [openapi.json](openapi.json) for information about this REST API endpoints.

Generate it with : 

```sh
sslamanagerrest --dump-openapi -c /dev/null
```

## Development

### Dependencies

You need the SSLA Manager as a dependency for this project :

```sh
SSLA_MANAGER_VERSION="v0.1.0"
poetry config repositories.sslamanager https://github.com/ThalesGroup/ssla-manager
poetry add git+https://github.com/ThalesGroup/ssla-manager#${SSLA_MANAGER_VERSION}
```

### Build

Build the wheel file :

```sh
./build.sh
```

To build the container image :

```sh
podman build -f ./Containerfile -t localhost/thales-sslamanager-rest
```

### Install

Install `sslamanagerrest` in your python environment :

```sh
./install.sh
```

Verify :

```sh
# manual with poetry
sslamanagerrest --help
```

### Dev run

```sh
poetry run python -m sslamanagerrest -c config.yaml
```

Test with :

```sh
curl -L localhost:8080/api/v1/health
```
