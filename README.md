Enable Ingress

```
minikube addons enable ingress
minikube addons enable ingress-dns
```

Bond domain name with IP Address
```
echo "$(minikube ip) domain-service.local" | sudo tee -a /etc/hosts
```

Build dockers
```bash
docker build -t backend-command:1.0.0 -f backend-command/backend-command.Dockerfile .
docker build -t backend-query:1.0.0 -f backend-query/backend-query.Dockerfile .
docker build -t todo-ui:1.0.0 -f todo-ui/todo-ui.Dockerfile .
```
Run dockers
```bash
docker run -d --name backend-command -p 8001:8000 backend-command:1.0.0
docker run -d --name backend-query -p 8002:8000 backend-query:1.0.0
docker run -d --name todo-ui -p 80:80 todo-ui:1.0.0
```

Upload dockers
```bash
docker image pull wurstmeister/zookeeper:3.4.6
docker image pull wurstmeister/kafka:2.12-2.5.0
docker image pull postgres:13

minikube image load backend-command:1.0.0
minikube image load backend-query:1.0.0
minikube image load todo-ui:1.0.0
minikube image load wurstmeister/zookeeper:3.4.6
minikube image load wurstmeister/kafka:2.12-2.5.0
minikube image load postgres
```


How to run

```bash
kubectl apply -f domain-service/backend-command-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

```bash
kubectl apply -f k8s/deployments/zookeeper-deployment.yaml
kubectl apply -f k8s/deployments/kafka-deployment.yaml
kubectl apply -f k8s/services/zookeeper-service.yaml
kubectl apply -f k8s/services/kafka-service.yaml
```