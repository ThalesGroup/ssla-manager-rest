# SSLA Manager REST API

Implements a REST API for the [SSLA manager module](https://github.com/ThalesGroup/ssla-manager) and to manage SSLAs remotely.

## Quick start

Install :

```sh
podman build -f ./Containerfile -t localhost/thales-sslamanager-rest .
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

Check :

```sh
curl localhost:8081/api/v1/health
> ok
```

Try it in your browser at `localhost:8081/docs`.  
You can use the examples in `examples/ssla/` to submit security policies.  

## OpenAPI specs

Read [openapi.json](openapi.json) for information about this REST API endpoints.

Generate it with : 

```sh
sslamanagerrest --dump-openapi -c /dev/null
```

## Development

### Build

You need `uv` for this 

Build the wheel file :

```sh
uv build
```

To build the container image :

```sh
podman build -f ./Containerfile -t localhost/thales-sslamanager-rest .
```

### Dev run

```sh
uv run sslamanagerrest -c config.yaml
```

Test with :

```sh
curl -L localhost:8080/api/v1/health
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
