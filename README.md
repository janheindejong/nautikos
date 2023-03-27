# Nautikos 

*A lightweight CI/CD tool for updating image tags in Kubernetes manifests.* 

[![PyPI version](https://badge.fury.io/py/nautikos.svg)](https://badge.fury.io/py/nautikos)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python versions](https://img.shields.io/pypi/pyversions/nautikos)]()

## Rationale

A GitOps CI/CD process usually uses a deployment or ops repo containing Kubernetes manifests for multiple services and environments. Tools like *Argo-CD* or *Flux* then track these repo's, and apply any changes to the cluster. When a new image of an application is created, you want the corresponding tags to be updated in the manifests. Doing this manually is error prone. Having to write logic in every repo or pipeline to perform this is tedious. 

This is where Nautikos comes in. 

## Installation 

```bash
pip install nautikos
```

## Basic usage 

Nautikos is configured through a YAML-file (`./nautikos.yaml`), that specifies where the manifests for the different images and environments can be found: 

```yaml
environments: 
- name: prod 
  manifests: 
  - path: prod/app1/deployment.yaml  # Path relative to configuration file
    type: kubernetes  # Type can be 'kubernetes' or 'kustomize'
    labels: 
    - app1
    - refs/head/main
  - path: prod/app2/kustomize.yaml
    type: kustomize
    labels:  # Optional specification of labels for more granular control
    - app2
    - refs/head/master
- name: dev
  manifests: 
  - path: dev/app1/deployment.yaml
    type: kubernetes
    labels: 
    - app1
    - refs/head/dev
  - path: dev/app3/feature-A/deployment.yaml
    type: kubernetes
    labels: 
    - app1
    - refs/head/feature-A
```

Next, you can run Nautikos to update the image tags of specific images in different environments.

```bash
nautikos my-repo 1.2.3  # Updates all occurences of `my-repo` to `1.2.3` in all manifests
nautikos --env prod my-repo 2.3.4  # Updates all occurences of `my-repo` to `2.3.4` in `prod/app1/deployment.yaml` and `prod/app2/deployment`
nautikos --env dev --labels app1 my-repo 4.5.6  # Updates all occurences of `my-repo` to `4.5.6` in `dev/app1/deployment.yaml`
nautikos --labels 'app1,refs/head/main' my-repo 5.6.7  # Updates all occurences of `my-repo` to `5.6.7` in `prod/app1/deployment.yaml`
```

## Supported tools

The tool works with standard **Kubernetes** manifests and **Kustomize** - **Helm** might be added later. Each have their own format for defining image tags. 

```yaml
# Kubernetes manifests
spec:
  template:
    spec:
      containers:
      - image: some-repository:tag

# Kustomize
images: 
- name: some-repository
  newTag: tag 
```

## Advanced usage

Nautikos takes several options: 

* `--dry-run`: prints the modified files to stdout, but doesn't edit in place 
* `--config config-file.yaml`: path to config YAML, default is `./nautikos.yaml`

## Alternatives 

There are basically three alternatives to do the same thing: 

* **Update manifests manually** - of course this works, but this is not really proper CD
* **Write your own bash scripts in a pipeline using a tool like `sed` or `yq`** - This works, but having to write this logic for every project is tedious. 
* **Use a tool like [Argo-CD Image updater](https://argocd-image-updater.readthedocs.io/en/stable/)** - very nice, but a bit heavy-weight, not very actively developed, and doesn't seem to support Azure Container Registry. 

## Notes 

Multiple YAML docs in one file is not yet supported. 

## Dependencies 

* **`typer`** - for creating a CLI 
* **`ruamel.yaml`** - for handling YAML files while maintaining ordering and comments
