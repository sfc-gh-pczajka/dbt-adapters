import pytest
import os

# Import the fuctional fixtures as a plugin
# Note: fixtures with session scope need to be local

pytest_plugins = ["dbt.tests.fixtures.project"]

SKIP_REASON = "not passing on reference driver due to account configuration"
TESTS_TO_SKIP = {
    "tests/functional/auth_tests/test_oauth.py",
    "tests/functional/auth_tests/test_jwt.py",
    "tests/functional/auth_tests/test_key_pair.py",
    "tests/functional/adapter/catalog_integrations/test_iceberg_rest_catalog_integrations.py",
    "tests/functional/adapter/test_sample_mode.py::TestSnowflakeSampleMode::test_sample_mode",
    "tests/functional/adapter/python_model_tests/test_table_type.py::TestTableType::test_expected_table_types_are_created",
    "tests/functional/generic_test_tests/test_generic_tests.py::TestWarehouseConfigExplicitWarehouse::test_expected_warehouse",
    "tests/functional/iceberg/test_iceberg_partition_by.py::TestPartitionByIcebergRestGlueCatalog",
    "tests/functional/iceberg/test_iceberg_partition_by.py::TestPartitionByIcebergBuiltinCatalog",
    "tests/functional/iceberg/test_iceberg_partition_by.py::TestPartitionByIcebergRestCatalog",
    "tests/functional/iceberg/test_iceberg_partition_by.py::TestPartitionByIgnoredIfNotIceberg",
    "tests/functional/adapter/catalog_tests/test_catalog.py",
    "tests/functional/auth_tests/test_pat.py",
    "tests/functional/adapter/change_tracking/test_change_tracking_show_tables.py::TestIcebergTableChangeTrackingShowTables",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        nodeid = item.nodeid
        for pattern in TESTS_TO_SKIP:
            if nodeid.startswith(pattern) or ("::" in pattern and pattern in nodeid):
                item.add_marker(pytest.mark.skip(reason=SKIP_REASON))
                break


# The profile dictionary, used to write out profiles.yml
@pytest.fixture(scope="class")
def dbt_profile_target():
    profile = {
        "type": "snowflake",
        "threads": 4,
        "account": os.getenv("SNOWFLAKE_TEST_ACCOUNT"),
        "database": os.getenv("SNOWFLAKE_TEST_DATABASE"),
        "warehouse": os.getenv("SNOWFLAKE_TEST_WAREHOUSE"),
    }

    if os.getenv("SNOWFLAKE_TEST_PRIVATE_KEY"):
        profile["private_key"] = os.getenv("SNOWFLAKE_TEST_PRIVATE_KEY")
    elif os.getenv("SNOWFLAKE_TEST_PRIVATE_KEY_PATH"):
        profile["private_key_path"] = os.getenv("SNOWFLAKE_TEST_PRIVATE_KEY_PATH")

    # Support PAT or password authentication
    authenticator = os.getenv("SNOWFLAKE_TEST_AUTHENTICATOR")
    if authenticator:
        profile["authenticator"] = authenticator
        if os.getenv("SNOWFLAKE_TEST_TOKEN"):
            profile["token"] = os.getenv("SNOWFLAKE_TEST_TOKEN")
    if os.getenv("SNOWFLAKE_TEST_USER"):
        profile["user"] = os.getenv("SNOWFLAKE_TEST_USER")
    if os.getenv("SNOWFLAKE_TEST_PASSWORD"):
        profile["password"] = os.getenv("SNOWFLAKE_TEST_PASSWORD")

    if os.getenv("SNOWFLAKE_TEST_ROLE"):
        profile["role"] = os.getenv("SNOWFLAKE_TEST_ROLE")

    # Optional parameters allow testing against local DEV Snowflake instances.
    if os.getenv("SNOWFLAKE_TEST_HOST"):
        profile["host"] = os.getenv("SNOWFLAKE_TEST_HOST")
    if os.getenv("SNOWFLAKE_TEST_PORT"):
        profile["port"] = int(os.getenv("SNOWFLAKE_TEST_PORT"))
    if os.getenv("SNOWFLAKE_TEST_PROTOCOL"):
        profile["protocol"] = os.getenv("SNOWFLAKE_TEST_PROTOCOL")
    return profile
