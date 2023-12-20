provider "openshift" {}

resource "openshift_deployment_config" "test" {
  metadata {
    name = "Tofu-example"
    labels = {
      test = "MyExampleApp"
    }
  }

  spec {
    replicas = 3

      spec {
        container {
          image = "nginx:1.7.8"
          name  = "example"

          resources {
            limits {
              cpu    = "0.5"
              memory = "512Mi"
            }
            requests {
              cpu    = "250m"
              memory = "50Mi"
                }
            }
            }
        }
    }
}
