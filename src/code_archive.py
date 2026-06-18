import argparse
import json
import dataclasses
import os

@dataclasses.dataclass
class Backup:
    data: dict

def backup(data: dict) -> Backup:
    return Backup(data)

def restore(backup_file: str) -> dict:
    with open(backup_file, 'r') as f:
        data = json.load(f)
    return data

def main():
    parser = argparse.ArgumentParser(description='Code Archive CLI')
    subparsers = parser.add_subparsers(dest='command')
    backup_parser = subparsers.add_parser('backup')
    backup_parser.add_argument('--data', required=True, help='Data to backup')
    restore_parser = subparsers.add_parser('restore')
    restore_parser.add_argument('--file', required=True, help='Backup file to restore from')
    args = parser.parse_args()
    if args.command == 'backup':
        data = json.loads(args.data)
        backup_data = backup(data)
        with open('backup.json', 'w') as f:
            json.dump(backup_data.data, f)
        print('Backup successful')
    elif args.command == 'restore':
        data = restore(args.file)
        print('Restored data:', data)

if __name__ == '__main__':
    main()
