SULPM stands for Small Universal Linux Package Manager.

It is an open-source package manager that relies on a combination of JSON and files.

It should work on any distro with curl + python3 preinstalled, this makes it cross-distro like snap, yay!
You can also use python3.x in paths, and it'll be automatically replaced with the correct version!
SULPM packages also don't really need to be archived, you just have to get it on github.

Changelog:
1.1.0 - Add dynamic base URL support. e.g. sulpm project user repository (default is still supported, with user being Darkwing14 and repository being SULPM).

1.2.0 - Add deletion functionality. e.g. sulpm remove project.

1.2.1 - Hotfix to make global installs safer with sudo.
