# Kubernetes Notes

## Pods
Smallest deployable unit in Kubernetes.

## Services
- ClusterIP: Internal access
- NodePort: External access on node port
- LoadBalancer: Cloud load balancer

## Deployments
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag
  template:
    metadata:
      labels:
        app: rag
    spec:
      containers:
      - name: rag
        image: rag-app:latest
        ports:
        - containerPort: 8000
```
