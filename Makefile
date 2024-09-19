include $(wildcard .env)
export

SYMBOL=for i in `seq 1 50`; do echo -n '='; done;
frame=$(SYMBOL) echo -n " "$(1)" "; $(SYMBOL) echo "\n"

POETRY=poetry
PYLINT=$(POETRY) run pylint --extension-pkg-whitelist='pydantic'
PACKAGE=role-based_app
TEST_PACKAGE=tests

help:
		@$(call frame,"HELP")
		@echo "- make install --> Install the dependencies"
		@echo "- make up --> Setup Environment"
		@echo "- make start --> Run local app"
		@echo "- make create-test-db --> Setup Test Environment"
		@echo "- make stop-db --> Stop local database"
		@echo "- make remove-db --> Remove local database"
		@echo "- make remove-test-db --> Remove local database"
		@echo "- make test --> Run all tests"
		@echo "- make unit-test --> Run all unit-tests"
		@echo "- make integration-test --> Run all integration-tests"
		@echo "- make unit-test specific_test=<name_of_the_test> --> Run specific unit-test"
		@echo "- make integration-test specific_test=<name_of_the_test> --> Run specific integration-test"
		@echo "- make upgrade-migrations --> Run migrations to local database"
		@$(call frame,"END HELP")

install:
		@$(call frame,"Installing dependencies role-based")
		$(POETRY) install
		$(POETRY_EXPORT)

unit-test:
		@$(call frame,"Test with pytest")
		@if [ "$(specific_test)" ]; then \
		python -m pytest -vv -s -k $(specific_test);\
		else \
		python -m pytest -v tests/unit;\
		fi
		@echo "Completed test!"

integration-test: export ENVIRONMENT = test
integration-test:
		@$(call frame,"Start Test Database")
		docker start role-based-test-db
		@echo "Test Database Started!"

		@$(call frame,"Run Migrations")
		alembic upgrade head
		@echo "Completed run migrations!"

		@$(call frame,"Test with pytest")
		@if [ "$(specific_test)" ]; then \
		pytest -vv -s -k $(specific_test);\
		else \
		pytest -v tests/integration;\
		fi
		@echo "Completed test!"

		@$(call frame,"Stop Test Database")
		docker stop role-based-test-db
		@echo "Test Database Stoped!"

test: export ENVIRONMENT = test
test:
		@$(call frame,"Start Test Database")
		docker start role-based-test-db
		@echo "Test Database Started!"

		@$(call frame,"Run Migrations")
		alembic upgrade head
		@echo "Completed run migrations!"

		@$(call frame,"Test with pytest")
		@if [ "$(specific_test)" ]; then \
		pytest -vv -s -k $(specific_test);\
		else \
		pytest -vvv;\
		fi
		@echo "Completed test!"

		@$(call frame,"Stop Test Database")
		docker stop role-based-test-db
		@echo "Test Database Stoped!"

lint:
		@$(call frame,"Lint with pylint")
		$(PYLINT) ${PACKAGE}
		$(PYLINT) ${TEST_PACKAGE}
		flake8 ${PACKAGE}
		flake8 ${TEST_PACKAGE}

up:
		@$(call frame,"Set up role-based App Environment")
		docker run -d --name role-based-db -v role-based_db:/var/lib/postgresql/data -p ${DB_PORT}:5432 -e POSTGRES_USER=${DB_USERNAME} -e POSTGRES_DB=${DB_NAME} -e POSTGRES_PASSWORD=${DB_PASS} postgres:${DB_VERSION}

stop-db:
		@$(call frame,"Stop Database")
		docker stop role-based-db
		@echo "Database Stoped!"

stop-test-db:
		@$(call frame,"Stop Database")
		docker stop role-based-test-db
		@echo "Database Stoped!"

remove-db:
		@$(call frame,"Remove Database")
		@$(call frame,"Stop Database")
		docker stop role-based-db
		@echo "Database Stoped!"

		@$(call frame,"Remove Container")
		docker rm role-based-db
		@echo "Container Removed!"

		@$(call frame,"Remove Volume")
		docker volume rm role-based_db
		@echo "Volume Removed!"

upgrade-migrations:
		@$(call frame,"Run Migrations")
		alembic upgrade head
		@echo "Completed run migrations!"

start:
		@$(call frame,"Start Test Database")
		docker start role-based-db
		@$(call frame,"Run Migrations")
		alembic upgrade head
		@echo "Completed run migrations!"
		@$(call frame,"Run App Locally")
		uvicorn role-based_app.main:app --reload

create-test-db:
		@$(call frame,"Create Test Database")
		docker run -d --name role-based-test-db -v role-based_test_db:/var/lib/postgresql/data -p ${DB_TEST_PORT}:5432 -e POSTGRES_USER=${DB_TEST_USERNAME} -e POSTGRES_DB=${DB_TEST_NAME} -e POSTGRES_PASSWORD=${DB_TEST_PASS} postgres:${DB_TEST_VERSION}

remove-test-db:
		@$(call frame,"Remove Test Database")
		@$(call frame,"Stop Test Database")
		docker stop role-based-test-db
		@echo "Database Stoped!"

		@$(call frame,"Remove Test Container")
		docker rm role-based-test-db
		@echo "Container Removed!"

		@$(call frame,"Remove Test Volume")
		docker volume rm role-based_test_db
		@echo "Volume Removed!"

build_and_deploy_image:
		@$(call frame,"Build project image")
		docker build -t ${ECR_REGISTRY}/${ECR_NAME}${ENVIRONMENT_SUFFIX}:$(ECR_TAG) -f Dockerfile .
		@echo "Project image builded!"

		@$(call frame,"Push project image")
		docker push ${ECR_REGISTRY}/${ECR_NAME}${ENVIRONMENT_SUFFIX}:$(ECR_TAG)
		@echo "Project image pushed!"

start_docker_app:
	docker-compose up role-based-backend role-based-backend-db

docker_unit_test:
	docker-compose up -d role-based-backend-unit-tests
	docker exec -it role-based-backend-unit-tests poetry run pytest --disable-warnings -v tests/unit

docker_integration_test:
	docker-compose up -d role-based-backend
	docker exec -it role-based-app-backend poetry run pytest --disable-warnings -vv tests/integration

docker_test:
	docker-compose up -d role-based-backend
	docker exec -it role-based-app-backend poetry run pytest --disable-warnings -v tests

docker_lint:
	docker-compose up -d role-based-backend-unit-tests
	docker exec -it role-based-backend-unit-tests poetry run pylint --extension-pkg-whitelist='pydantic' ${PACKAGE}
	docker exec -it role-based-backend-unit-tests poetry run pylint --extension-pkg-whitelist='pydantic' ${TEST_PACKAGE}
	docker exec -it role-based-backend-unit-tests poetry run flake8 ${PACKAGE}
	docker exec -it role-based-backend-unit-tests poetry run flake8 ${TEST_PACKAGE}
