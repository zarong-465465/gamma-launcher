from hashlib import file_digest
from pathlib import Path

from launcher.commands.common import read_mod_maker, parse_moddb_data


class CheckMD5:

    arguments: dict = {
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
    }

    name: str = "check-md5"

    help: str = "Check MD5 hash for all addons"

    def run(self, args) -> None:
        errors = []
        modpack_dl_dir = Path(args.gamma) / "downloads"
        modpack_data_dir = Path(args.gamma) / ".Grok's Modpack Installer" / "G.A.M.M.A" / "modpack_data"

        mod_maker = read_mod_maker(
            modpack_data_dir / 'modlist.txt',
            modpack_data_dir / 'modpack_maker_list.txt'
        )

        print('-- Starting MD5 Check')
        for i in filter(lambda v: v and v['info_url'], mod_maker.values()):
            try:
                info = parse_moddb_data(i['info_url'])
                file = modpack_dl_dir / info['Filename']
            except KeyError:
                errors += [f"Error: parsing failure for {i['info_url']}"]
                continue

            if info.get('Download', '') not in i['url']:
                errors += [f"WARNING: Skipping {file.name} since ModDB info do not match download url"]
                continue

            if not file.exists():
                errors += [f"Error: {file.name} not found on disk"]
                continue

            with open(file, 'rb') as f:
                md5 = file_digest(f, 'md5').hexdigest()
            print(f"{file.name} remote hash is: '{info['MD5 Hash']}'")
            print(f"{file.name} local  hash is: '{md5}'")

            if md5 != info['MD5 Hash']:
                errors += [f"Error: {file.name} -- remote({info['MD5 Hash']}) != local({md5})"]

            print('-' * 25)

        for err in errors:
            print(err)
