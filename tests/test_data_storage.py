from data_storage import DataStorage, Data

def test_store():
    storage = DataStorage()
    content = "Hello, World!"
    data = storage.store(content)
    assert data.id == 1
    assert data.version == 1
    assert data.created_at is not None

def test_retrieve():
    storage = DataStorage()
    content = "Hello, World!"
    data = storage.store(content)
    retrieved_data = storage.retrieve(data.id)
    assert retrieved_data.id == data.id
    assert retrieved_data.version == data.version
    assert retrieved_data.created_at == data.created_at

def test_update():
    storage = DataStorage()
    content = "Hello, World!"
    data = storage.store(content)
    updated_content = "Hello, Universe!"
    updated_data = storage.update(data.id, updated_content)
    assert updated_data.id == data.id
    assert updated_data.version == 2
    assert updated_data.created_at == data.created_at

def test_delete():
    storage = DataStorage()
    content = "Hello, World!"
    data = storage.store(content)
    storage.delete(data.id)
    try:
        storage.retrieve(data.id)
        assert False
    except ValueError:
        assert True

def test_encrypt_decrypt():
    storage = DataStorage()
    content = "Hello, World!"
    encrypted_content = storage.encrypt(content)
    assert encrypted_content != content
    decrypted_content = storage.decrypt(encrypted_content)
    assert decrypted_content != content
