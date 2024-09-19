""" Set PostgreSql database with sqlalchemy """

import os
from os.path import dirname, join
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), ".env")

db_username = os.environ.get("DB_USERNAME", "user_test")
db_pass = os.environ.get("DB_PASS", "")
db_name = os.environ.get("DB_NAME", "test_db")
db_port = os.environ.get("DB_PORT", "1234")
db_host = os.environ.get("DB_HOST", "localhost")
db_test_port = os.environ.get("DB_TEST_PORT", "5432")
db_test_username = os.environ.get("DB_TEST_USERNAME", "postgres")
db_test_pass = os.environ.get("DB_TEST_PASS", "postgres")
db_test_name = os.environ.get("DB_TEST_NAME", "postgres")

db_string = "postgresql://"+db_username+":"+db_pass+"@"+db_host+":"+db_port+"/"+db_name
db_test_string = "postgresql://"+db_test_username+":"+db_test_pass +\
    "@"+db_host+":"+db_test_port+"/"+db_test_name

role_based_STAGE_KEY = os.environ.get("role-based_STAGE_KEY")
role_based_URL = os.environ.get("role-based_URL")

base = declarative_base()
