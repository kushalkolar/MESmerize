---
name: Installation Issue
about: For difficulties related to installation
title: "[INSTALLATION HELP]"
labels: help wanted
assignees: kushalkolar

---

Please try these things before posting an installation issue:

1. Create a fresh new anaconda or virtual environment.

2. If you're having difficulties with `caiman` installation try installing a specific version, for example:
  `conda install -c conda-forge caiman==1.8.5`

3. If you want to use caiman features, `caiman` _must_ but installed in the same environment as `mesmerize`.

4. If you want to use certain features like kshape clustering or cross-correlation, `tslearn` must be installed in the same environment as `mesmerize`.

Otherwise use this template:

**System information**
1. OS (ex. Windows 10, Mac OSX Mojave, Ubuntu 20.04 LTS)
2. CPU (ex. Intel i7 9700k, AMD Ryzen 3950x)
3. RAM
4. Do you have an SSD or magnetic HDD

**Copy & paste the entire output of the terminal while you were trying to install when the issue came up:**

```
PASTE HERE
```

**Installation method**
1. Are you using anaconda, python virtual environments, or something else?
  -> if using conda, what is the conda version

2. If you're installing mesmerize through pip, what version of pip is installed in the environment?

3. Are you trying to install in developer mode from the repo?

4. What is the python version in the environment you're trying to install `mesmerize` in?

5. Information if you're using some other installation method.
