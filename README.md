# Nautikos 

Nautikos is a CLI tool for updating image tags in Kubernetes manifests, as part of a GitOps CI/CD process. 

In a GitOps process, a deployment repo typically contains Kubernetes manifests for multiple services and environments. When you create a new image for your application, you want the correct manifests to be updated with the new tag. Doing this manually is error prone. Having to write logic in every repo or pipeline to perform this is tedious. This is where Nautikos comes in. 

Nautikos is configured through a YAML-file (`nautikos.yaml`), that specifies what images to update, and where. 

```yaml
service: 
    - image: some-repository
      environments: 
        - name: prod 
          manifests: 
            - path/to/prod-env-1-file.yaml
            - path/to/prod-env-2-file.yaml 
        - name: dev
          manifests: 
            - path/to/dev-env-file.yaml
```

Nautikos run as a CLI: 

```bash 
nautikos --image some-repository --env prod --tag 1.2.3
```

This will update the tags for the image `some-repository` to `1.2.3` in the files `prod-env-1-file.yaml` and `prod-env-2-file.yaml`.

The tool works with standard Kubernetes manifests, and with Kustomization files. 
