Copy-quay
=========

This is a tool to copy containers from one registry to quay.

The functionality is as follow:

* Parse the containers-build job result
* Collect the containers built in the job
* Pull it from the source registry
* If it is a new container, create the repository as public in quay
* Push it to quay
* Tag the container with both current-podified and build id

Building
--------

Just run:

    $ go build -o copy-quay main.go copy.go utils.go quayapi.go

An executable copy-quay will be created

Usage
-----
Since this uses the podman api to copy the repositories, you can use podman to authenticate::

    $ podman login quay.io

Then, the simplest way to run it is::

    copy-quay --token $TOKEN --from-namespace podified-main-centos9 --to-namespace podified-main-centos9 copy

If you require to parse a job::

    copy-quay --token $TOKEN --from-namespace podified-zed-centos9 --to-namespace podified-zed-centos9 \
              --job periodic-container-tcib-build-push-centos-9-zed copy

Copying only one single container, for example from another registry::

    copy-quay --debug --pull-registry quay.ceph.io --token $TOKEN \
              --from-namespace ceph-ci --to-namespace ceph-ci \
              --tag current-ceph copy daemon

In the example above, it will copy the daemon tagged with current-ceph container
from quay.ceph.io and push it to quay.io/ceph-ci
