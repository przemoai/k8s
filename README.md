Enable Ingress

```
minikube addons enable ingress
minikube addons enable ingress-dns
```

Bond domain name with IP Address
```
echo "$(minikube ip) domain-service.local" | sudo tee -a /etc/hosts
```





How to run

```bash
kubectl apply -f domain-service/domain-service.yaml
kubectl apply -f k8s/ingress.yaml

```