Fix Python encodings
====================

This role ensures the `python3-libs` package is installed,
as well as verifies the necessary encoding file is in the system
– and if not, it is fetched directly from the CPython repository.

**Important!**
Make sure to call this role from a playbook **without** gathering facts! \
(Set `gather_facts: false` ~ otherwise it makes no sense to use this role!)


Details
-------

When Ansible tries to invoke modules on target machines, it relies
on the call [^1] to ZipFile module from the Python standard library [^2].
The handling of zip files requires to support necessary encodings,
which should typically be CP437 (Code Page 437 [^3]) and UTF-8
(but sometimes it can be also CP1252/Windows-1252 or ISO-8859-1 [^4]).

When attempting to run Ansible modules against some freshly provisioned
hypervisors, sometimes, rarely, but still from time to time, we encounter:

```
PLAY [Prepare the hypervisor.] ************************************************

TASK [Create zuul user name=zuul, state=present] ******************************
fatal: [hypervisor]: FAILED! => {
    "changed": false,
    "module_stderr": "
        Warning: Permanently added '(...)' (ED25519) to the list of known hosts.
        Traceback (most recent call last):
            File \"<stdin>\", line 107, in <module>
            File \"<stdin>\", line 99, in _ansiballz_main
            File \"<stdin>\", line 35, in invoke_module
            File \"/usr/lib64/python3.9/zipfile.py\", line 1286, in __init__
                self._RealGetContents()
            File \"/usr/lib64/python3.9/zipfile.py\", line 1371, in _RealGetContents
                filename = filename.decode('cp437')
            LookupError: unknown encoding: cp437
    ",
    "module_stdout": "",
    "msg": "MODULE FAILURE See stdout/stderr for the exact error",
    "rc": 1
}
```

In Red Hat distributions it should come from the `python3-libs` package,
where it is shipped as just compiled Python file:

```
# rpm -qal python3-libs | grep -i 'encodings/cp437'
/usr/lib64/python3.9/encodings/cp437.pyc
```

However, in some installations we either seem to lack `python3-libs`
or simply that file is removed accidentally by some cleaning tool.
Unfortunately, it looks like a problem that occur from time to time [^5].

This role ensures the `python3-libs` package is installed,
as well as verifies the necessary encoding file is in the system
– and if not, it is fetched directly from the CPython repository [^6].
To make sure it is all doable, everything in this role is performed via Ansible
raw action plugin [^7] that does not invoke the modules subsystem [^8]
on the target host.


References
----------

[^1]: https://github.com/ansible/ansible/blob/stable-2.19/lib/ansible/_internal/_ansiballz/_wrapper.py#L121

[^2]: https://docs.python.org/3/library/zipfile.html

[^3]: https://en.wikipedia.org/wiki/Code_page_437

[^4]: https://marcosc.com/2008/12/zip-files-and-encoding-i-hate-you/

[^5]: https://github.com/pypa/pip/issues/11449

[^6]: https://raw.githubusercontent.com/python/cpython/main/Lib/encodings/cp437.py

[^7]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/raw_module.html

[^8]: https://stackoverflow.com/a/37079451
