from code_archive import CodeArchive, Snapshot

def test_backup():
    archive = CodeArchive()
    repo = "test_repo"
    snapshot_id, status = archive.backup(repo)
    assert status == "created"
    assert isinstance(snapshot_id, str)
    assert len(snapshot_id) > 0

def test_get_snapshot():
    archive = CodeArchive()
    repo = "test_repo"
    snapshot_id, _ = archive.backup(repo)
    snapshot = archive.get_snapshot(snapshot_id)
    assert isinstance(snapshot, Snapshot)
    assert snapshot.id == snapshot_id
    assert snapshot.status == "created"

def test_get_non_existent_snapshot():
    archive = CodeArchive()
    snapshot_id = "non_existent_id"
    snapshot = archive.get_snapshot(snapshot_id)
    assert snapshot is None
