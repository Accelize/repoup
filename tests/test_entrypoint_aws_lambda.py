"""Test AWS lambda entrypoint."""
from json import dumps
from uuid import uuid4
from tests.conftest import StorageHelper
from tests.test_repository_rpm import PKG, PKG_PATH, PKG_REPO_PATH


def test_add_remove_package(storage_helper: StorageHelper) -> None:
    """Test AWS lambda entrypoint with add/remove packages."""
    from repoup.entrypoint.aws_lambda import handler

    s3 = dict(object=dict(key=PKG_PATH), bucket=dict(name="bucket"))

    # Add package
    storage_helper.put(PKG_PATH, PKG_PATH)
    put_record = dict(Records=[dict(eventName="ObjectCreated:Put", s3=s3)])
    handler(put_record, None)
    content = storage_helper.keys
    assert PKG_REPO_PATH in content
    assert PKG not in content

    # Already added package
    storage_helper.put(PKG_PATH, PKG_PATH)
    handler(put_record, None)
    assert PKG not in storage_helper.keys

    # Remove package
    handler(dict(Records=[dict(eventName="ObjectRemoved:Delete", s3=s3)]), None)
    content = storage_helper.keys
    assert PKG_REPO_PATH not in content

    # Invalid argument
    handler(dict(Records=[dict(eventName="s3:ObjectTagging:Put", s3=s3)]), None)
    content = storage_helper.keys
    assert PKG_REPO_PATH not in content

    # Add package, trigger with SQS
    storage_helper.put(PKG_PATH, PKG_PATH)
    handler(
        dict(Records=[dict(messageId=str(uuid4()), body=dumps(put_record))]),
        None,
    )
    content = storage_helper.keys
    assert PKG_REPO_PATH in content
    assert PKG not in content

    # SQS empty event
    handler(dict(Records=[dict(messageId=str(uuid4()), body=dumps(dict()))]), None)
