terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.23.0"
    }
  }
}

provider "kubernetes" {
 config_path = "~/.crc/machines/crc/kubeconfig"
}

resource "kubernetes_namespace" "tofu-tests" {
  metadata {
    name = "tofu-experiements"
  }
}

resource "kubernetes_deployment" "ubuntu" {
  metadata {
    name = "ubuntu"
    namespace = kubernetes_namespace.tofu-tests.metadata.0.name
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        app = "ubuntu"
      }
    }
    template {
      metadata {
        labels = {
          app = "ubuntu"
        }
      }
      spec {
        container {
          name  = "ubuntu"
          image = "ubuntu:latest"
          command = ["/bin/bash", "-c", "--" ]
          args = [ "while true; do sleep 30; done;" ]
        }
      }
    }
  }
}
