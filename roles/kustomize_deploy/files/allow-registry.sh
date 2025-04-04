#!/usr/bin/bash

cat > ~/registry-policy-unsigned.yaml <<'EOF'
---
- hosts: computes
  tasks:
    - name: Do no block on signature for container
      ansible.builtin.copy:
        content: |
          {
              "default": [
                  {
                      "type": "insecureAcceptAnything"
                  }
              ],
              "transports": {
                  "docker": {
                      "registry.access.redhat.com": [
                          {
                              "type": "insecureAcceptAnything"
                          }
                      ],
                      "registry.redhat.io": [
                          {
                              "type": "insecureAcceptAnything"
                          }
                      ]
                  },
                  "docker-daemon": {
                      "": [
                          {
                              "type": "insecureAcceptAnything"
                          }
                      ]
                  }
              }
          }
        dest: "/etc/containers/policy.json"
      become: true
EOF

ansible-playbook \
    -i /home/zuul/ci-framework-data/artifacts/zuul_inventory.yml \
    ~/registry-policy-unsigned.yaml

