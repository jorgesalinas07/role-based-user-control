FROM public.ecr.aws/lambda/python:3.9.2023.05.13.01

ENV POETRY_VERSION=1.3.2

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy Application
COPY role_based_app ${LAMBDA_TASK_ROOT}/role_based_app

CMD ["role_based_app.main.handler"]
