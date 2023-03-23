# Nautikos 

Nautikos is a CLI tool for updating image tags in Kubernetes manifests, as part of a GitOps CI/CD process. 

## Rationale 

In a GitOps process, a deployment repo typically contains Kubernetes manifests for multiple services and environments. When you create a new image for your application, you want the correct manifests to be updated with the new tag. Doing this manually is error prone. Having to write logic in every repo or pipeline to perform this is tedious. 

This is where Nautikos comes in. 

## Installation 

```bash
pip install nautikos
```

## Basic usage 

Nautikos is configured through a YAML-file (`nautikos.yaml`), that specifies where the manifests for the different images and environments can be found: 

```yaml
environments: 
- name: prod 
  manifests: 
  - path: path/to/prod-env-1-file.yaml
    type: kubernetes
    repositories: 
      - repository-A
      - repository-B
  - path: path/to/prod-env-2-file.yaml 
    type: kustomize
    repositories: 
      - repository-A
- name: dev
  manifests: 
  - path: path/to/dev-env-file.yaml
    type: helm
    repositories: 
      - repository-A
```

Next, you can run Nautikos to update the image tag: 

```bash 
nautikos --env prod some-repository 1.2.3 
```

This will update the tags for the image `some-repository` to `1.2.3` in the files `prod-env-1-file.yaml` and `prod-env-2-file.yaml`.

The tool should be able to work with standard k8s manifests, Kustomize, and Helm charts. Each have their own format for defining image tags. 

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

## Notes

YAML objects are ordered alphabetically; order is not preserved. 

## Advanced usage

Nautikos takes several options: 

* `--dry-run`: prints the lines that would be modified, but doesn't edit in place 
* `--config config-file.yaml`: path to config YAML, default is `./nautikos.yaml`
