# Nautikos 

Nautikos is a CLI tool for updating image tags in Kubernetes manifests, as part of a GitOps CI/CD process. 

## Rationale

In a GitOps CI/CD process, a deployment repo contains Kubernetes manifests for multiple services and environments, that are tracked by a tool like *Argo-CD* or *Flux*. When a new image of an application is created, you want the tags for that image to be updated in the manifests. Doing this manually is error prone. Having to write logic in every repo or pipeline to perform this is tedious. 

This is where Nautikos comes in. 

## Installation 

```bash
pip install nautikos
```

## Basic usage 

Nautikos is configured through a YAML-file (`./nautikos.yaml`), that specifies where the manifests for the different images and environments can be found: 

```yaml
environments: 
# An environment is basically a collection of manifests that you want to 
# update simultaneously. 
- name: prod 
  manifests: 
  - path: path/to/prod-env-1-file.yaml
    type: kubernetes  # Type can be 'kubernetes', 'kustomize' or 'helm'
  - path: path/to/prod-env-2-file.yaml 
    type: kustomize
    repositories:  # Optional specification of repositories to be modified for more granular control
      - repository-b
      - repository-c
- name: dev
  manifests: 
  - path: path/to/dev-env-file.yaml
    type: helm
```

Next, you can run Nautikos to update the image tags of specific images in different environments.

```bash
nautikos --env prod repository-a 1.2.3  # Updates all occurences of the image `repository-a` to `1.2.3` in `prod-env-1-file.yaml`
nautikos --env prod repository-b 1.2.3  # Updates all occurences of the image `repository-b` to `1.2.3` in `prod-env-1-file.yaml` and `prod-env-1-file.yaml`
nautikos --env dev repository-c dev-1.2.3  # Updates all occurences of the image `repository-c` to `dev-1.2.3` in `dev-env-file.yaml`
```

## Supported tools

The tool works with standard **Kubernetes** manifests, **Kustomize**, and **Helm**. Each have their own format for defining image tags. 

```yaml
# Kubernetes manifests
image: "some-repository:tag"

# Kustomize
images: 
- name: some-repository
  newTag: tag 

# Helm 
image: 
- repository: some-repository 
  tag: tag 
```

## Advanced usage

Nautikos takes several options: 

* `--dry-run`: prints the lines that would be modified, but doesn't edit in place 
* `--config config-file.yaml`: path to config YAML, default is `./nautikos.yaml`

## Alternatives 

There are basically three alternatives to do the same thing: 

* **Update manifests manually** - of course this works, but this is not really proper CD
* **Write your own bash scripts in a pipeline using a tool like `sed`** - This works, but having to write this logic for every project is tedious. 
* **Use a tool like [Argo-CD Image updater](https://argocd-image-updater.readthedocs.io/en/stable/)** - very nice, but a bit heavy-weight, not very actively developed, and doesn't seem to support Azure Container Registry. 

## Dependencies 

* **`typer`** - for creating a CLI 
* **`ruamel.yaml`** - for handling YAML files while maintaining ordering and comments
