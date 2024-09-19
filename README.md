# role-based app backend

## Setup environment

### Requirements

- Python (You can install it by following the steps in this [link](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-22-04))
- Poetry (You can install it by following the steps in this [link](https://python-poetry.org/docs/master#installing-with-the-official-installer))
- Make (You'll have to search it how to install for your operative system)
- Docker
  You can follow the instructions below to install on each of the following operating systems:
  - [**Mac**](https://docs.docker.com/desktop/install/mac-install/)
  - [**Linux**](https://docs.docker.com/engine/install/)
  - [**Windows**](https://docs.docker.com/desktop/install/windows-install/)
- pyenv (You can install it by following the steps in this [link](https://github.com/pyenv/pyenv-installer))[OPTIONAL]

This step is optional, if you want to work with a simple Python version management tool (pyenv), if you don't, just install Python 3.9.0 version. Remember before working with pyenv, make sure you have the necessary dependencies for your operating system. Here a [link](https://github.com/pyenv/pyenv/wiki/Common-build-problems) that can help you.

In this project we'll use Python 3.9, so you have to install it by using the next command.(If you choose work with pyenv)

```
pyenv install 3.9.0
```
In the project directory, the following command is executed to indicate which version of Python will be used in that directory, in this case 3.9.0 version. (If you choose work with pyenv)

```
pyenv local 3.9.0
```

Then, you must indicate Poetry which version of Python will be used to configure the virtual environment.

```
poetry env use 3.9.0
```

To activate the virtual environment and execute instructions within it, you must run `poetry shell`.

You can also execute commands directly within the virtual environment by typing `poetry run` followed by the instruction in the command line.

After to do the last step, execute  `make install` command which will create the virtual environment and download the project dependencies.

### **Add variables**
In the root directory create a file .env with these values

```
export DB_PORT=xxxx
export DB_USERNAME=xxxx
export DB_NAME=xxxx
export DB_PASS=xxxx
export DB_VERSION=xxxx
export DB_TEST_VERSION=xxxx
export DB_HOST=xxxx
export DB_TEST_PORT=xxxx
export DB_TEST_USERNAME=xxxx
export DB_TEST_NAME=xxxxx
export DB_TEST_PASS=xxxxx
```

## Setup database

- Create the database on your computer with docker:

```shell
make up
```

- Upgrade migrations :

```shell
make upgrade-migrations
```

## Set Up Backend locally

- Now in your command line you will see `(env)` appearing, that means that your virtual enviroment is activated.
- Finally to make the server run:

```
make start
```

- The server will be open with the direction `http://localhost:8000/`

...

## **Makefile**

Execute the next command to show makefile help:

```shell
$ make help
```

### Test

We are using [Pytest](https://docs.pytest.org/en/latest/index.html) for tests. The tests are located in the package

This command run all tests:

```shell
make test
```
> The `make test` command already starts the test database, runs the lint, runs the tests and stops the test database.

Run a single test:

```shell
make test specific_test=file_name
```

## How to contribute to the project

Clone the repository and from the `main` branch create a new branch for each new task. You must follow the recommended branch name like below:

If your name is Andres Viera

```
    AV/DB-<number_ticket>-<title_ticket>
```
Where "AV" are the initials of your name.

E.G:

```
    AV/DB-250-update-readme
```
## Commit the message:

- The project use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) standards.
- The message should be in the following format:
    ```
    feat: BD-219 modify readme
    fix: BD-02 fix function get_example.py
    ```
- Commit types:
    - `fix` : hotfix or something that was fixed because of a bug
    - `feat` : refers to a feature, a new requirement
    - `test` : refers to test code, e.g. unit testing, integration testing
    - `refactor` : refers something was modified in the code, e.g. naming

## Create the Pull Request (PR)

- Submit the feature (`git push`) and create a PR to `dev` branch.
- Make sure the PR title starts with a commit type followed by the branch name. i.e:
```
    feat: AV/BD-<number_ticket>-<title_ticket>
```
Only `feat` and `fix` are allowed as commit types in the PR title.
- One commit PRs aren't allowed. Github actions will commit once one commit PR is created.
- Explain what has been done, what has been fixed or if you have created a new feature.
- Include reviewers in the PR.

## Architecture
The application follows a DDD approach with a hexagonal clean architecture.

We have a directory for each domain entity (i.e. Office, Parking etc)
Inside each entity directory we have other 3 directories (application, domain and infrastructure)
This drawing shows how these three folders work and what logic should be included in these directories.

![Image about diagram architecture](https://wata.es/wp-content/uploads/2021/05/diagrama-arquitectura-hexagonal-wata-factory-1024x796.png)
### Note: All controllers must have absolute imports
## AWS Architecture
![AWS architecture](https://i.imgur.com/hcTNeTP.png)
