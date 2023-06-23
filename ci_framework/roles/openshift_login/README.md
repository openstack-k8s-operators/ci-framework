# openshift_login
Manages OpenShift login operations

This role performs OpenShift login based on calls to the `oc` cli tool and exposes a well defined set of
variables that, after a successful login, can be used as credentials and API endpoints in other parts of
the framework. If more than one login attempts are neeeded the role retries as many time as dictated by
`cifmw_openshift_login_retries`.

Many login scenarios are allowed by passing or ommiting the following variables:
- `cifmw_openshift_login_kubeconfig`: The kubeconfig file path, if not given, the role will try to use user/password login
    and will create the kubeconfig in the default location `~/.kube/config`.
- `cifmw_openshift_login_api`: The OpenShift API endpoint. If not given the role will extract it from the kubeconfig.
- `cifmw_openshift_login_user` and `cifmw_openshift_login_password`: User/password for password based logins.
- `cifmw_openshift_login_provided_token`: Token only based logins.

After successful login, the following variables will hold all the needed information to perform call to the cluster:
* `cifmw_openshift_login_api` and `cifmw_openshift_api`: OpenShift API endpoint.
* `cifmw_openshift_login_kubeconfig` and `cifmw_openshift_kubeconfig`: Current kubeconfig file. Token and context populated with the latest changes.
* `cifmw_openshift_login_context` and `cifmw_openshift_context`: The current selected context in `cifmw_openshift_login_kubeconfig`/`cifmw_openshift_kubeconfig`.
* `cifmw_openshift_login_token` and `cifmw_openshift_token`: OpenShift token/API key.
* `cifmw_openshift_login_user` and `cifmw_openshift_user`: The user associated to the `cifmw_openshift_login_token`/`cifmw_openshift_token`.

## Privilege escalation
No privilege escalation needed.

## Parameters
* `cifmw_openshift_login_kubeconfig`: (String) Optional. Path to the kubeconfig file. Defaults to `cifmw_openshift_kubeconfig` and `~/.kube/config` as last instance.
* `cifmw_openshift_login_api`: (String) Optional. Path to the kubeconfig file. Defaults to `cifmw_openshift_api` and to the real API endpoint after login.
* `cifmw_openshift_login_user`: (String) Optional. Login user. If provided, the user that logins. Defaults to `cifmw_openshift_user` and to the logged in user after login.
* `cifmw_openshift_login_provided_token`: (String) Optional. Initial login token. If provided, that token will be used to authenticate into OpenShift. Defaults to `cifmw_openshift_provided_token`.
* `cifmw_openshift_login_password`: (String) Optional. Login password. If provided is the password used for login in. Defaults to `cifmw_openshift_password`.
* `cifmw_openshift_login_force_refresh`: (Boolean) Disallow reusing already existing token. Defaults to `false`.
* `cifmw_openshift_login_retries`: (Integer) Number of attempts to retry the login action if it fails. Defaults to `10`.
* `cifmw_openshift_login_retries_delay`: (Integer) Delay, in seconds, between login retries. Defaults to `20`.
* `cifmw_openshift_login_assume_cert_system_user`: (Boolean) When trying cert key login from kubeconfig, assume that the infered user is a `system:` admin. Defaults to `true`.
* `cifmw_openshift_login_skip_tls_verify`: (Boolean) Skip TLS verification to login. Note: This option may break admin login using certs. Defaults to `false`.

## Examples
### 1 - Login using user/password and API convination
```yaml
- hosts: all
  tasks:
    - name: Log in user/password/API
      include_role:
        name: openshift_login
      vars:
        cifmw_openshift_login_api: "https://api.crc.testing:6443"
        cifmw_openshift_login_user: "kubeadmin"
        cifmw_openshift_login_password: "12345678"
```

### 2 - Login using user/password and kubeconfig convination
```yaml
- hosts: all
  tasks:
    - name: Log in user/password/API
      include_role:
        name: openshift_login
      vars:
        # API infered from the given kubeconfig
        cifmw_openshift_login_kubeconfig: "/home/zuul/.crc/machines/crc/kubeconfig"
        cifmw_openshift_login_user: "kubeadmin"
        cifmw_openshift_login_password: "12345678"
```

### 3 - Login using admin kubeconfig
```yaml
- hosts: all
  tasks:
    - name: Log in user/password/API
      include_role:
        name: openshift_login
      vars:
        # X509 key in the kubeconfig client data
        cifmw_openshift_login_kubeconfig: "/home/zuul/.crc/machines/crc/kubeconfig"
```

### 4 - Token based login
```yaml
- hosts: all
  tasks:
    - name: Log in with token
      include_role:
        name: openshift_login
      vars:
        cifmw_openshift_login_provided_token: "sha256~Abcdefghij..."
```
