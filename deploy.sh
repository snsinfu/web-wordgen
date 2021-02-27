#!/bin/sh -eu

kubectl image build -t localhost/wordgen/web:latest .
kubectl apply -f manifest.yaml
kubectl rollout restart -n wordgen deployment/web
