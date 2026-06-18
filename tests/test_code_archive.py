import pytest
import json
from src.code_archive import backup, restore

def test_backup():
    data = {'key': 'value'}
    backup_data = backup(data)
    assert backup_data.data == data

def test_restore(tmp_path):
    backup_file = tmp_path / 'backup.json'
    data = {'key': 'value'}
    with open(backup_file, 'w') as f:
        json.dump(data, f)
    restored_data = restore(str(backup_file))
    assert restored_data == data

def test_main_backup(capsys):
    import sys
    sys.argv = ['code_archive.py', 'backup', '--data', '{"key": "value"}']
    from src.code_archive import main
    main()
    captured = capsys.readouterr()
    assert 'Backup successful' in captured.out

def test_main_restore(capsys, tmp_path):
    import sys
    backup_file = tmp_path / 'backup.json'
    data = {'key': 'value'}
    with open(backup_file, 'w') as f:
        json.dump(data, f)
    sys.argv = ['code_archive.py', 'restore', '--file', str(backup_file)]
    from src.code_archive import main
    main()
    captured = capsys.readouterr()
    assert 'Restored data: {' in captured.out
