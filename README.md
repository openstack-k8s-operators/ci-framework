# CI-Framework

Still under heavy development - more info coming soon.

## Contribute
### Add a new Ansible role
Run the following command to get your new role in:
```Bash
$ ansible-galaxy role init \
    --init-path ci_framework/roles \
    --role-skeleton _skeleton_role_ \
    YOUR_ROLE_NAME
```


### Run tests
#### Makefile
Run ```make help``` to list the available targets. Usually, you'll want to run
```make run_ctx_pre_commit``` or ```make run_ctx_molecule``` to run the tests
in a local container.


## License
Copyright 2023.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
