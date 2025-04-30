# security-policy-manager-rest-api

Implements a REST API for the security policy manager module and to manage SSLAs remotely.

## Quick start

Install :

```sh
podman build -f ./Containerfile -t localhost/thales-sslamanager-rest
```

Run :

```sh
touch /tmp/ssla.db
podman run -d \
  --name sslamanagerrest \
  -p 8080:80 \
  -v /tmp/ssla.db:/data/ssla.db \
  localhost/thales-ssla-manager
```

Try it in your browser at `localhost:8080/docs`.  
You can use the examples in `examples/ssla/` to submit security policies.  

## OpenAPI specs

Read [openapi.json](openapi.json) for information about this REST API endpoints.

Generate it with : 

```sh
ssla-manager-rest --dump-openapi -c /dev/null
```

## Development

### Dependencies

You need the Security Policy Manager as a dependency for this project :

```sh
SSLA_MANAGER_VERSION="v0.1.0"
poetry config repositories.sslamanager <ssla_manager_repo_url>
poetry add git+<ssla_manager_repo url>#${SSLA_MANAGER_VERSION}
```

### Build

Build the wheel file :

```sh
./build.sh
```

To build the container image manually :

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
