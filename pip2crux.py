#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from urllib.request import urlopen
from urllib.error import HTTPError

MODULE_JSON = 'https://pypi.org/pypi/{name}/json'


class PyModule:
    def __init__(self, json_data):
        info = json_data['info']
        self.pypi_name = info['name']
        self.name = f"python3-{self.pypi_name.lower().replace('_', '-')}"
        self.version = info['version']
        self.desc = (info.get('summary') or 'A Python module').replace('"', "'").strip()
        self.url = info.get('home_page') or info.get('project_urls', {}).get('Homepage', '')
        self.depends = self._get_depends(info)

        # Literal $version for CRUX pkgmk
        initial = self.pypi_name[0].lower()
        self.source_url = (
            f"https://files.pythonhosted.org/packages/source/"
            f"{initial}/{self.pypi_name}/{self.pypi_name}-$version.tar.gz"
        )

    def _get_depends(self, info):
        requires = info.get('requires_dist', []) or []
        deps = []
        for req in requires:
            match = re.match(r'^([A-Za-z0-9._-]+)', req)
            if match:
                dep = match.group(1).lower().replace('_', '-')
                if dep not in {'python', 'setuptools', 'wheel', 'pip', 'setuptools_scm'}:
                    deps.append(f"python3-{dep}")
        return sorted(set(deps))


def fetch_pypi_data(package_name):
    url = MODULE_JSON.format(name=package_name)
    try:
        with urlopen(url) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        print(f"Error: Failed to fetch {url} - {e}", file=sys.stderr)
        sys.exit(1)


def generate_pkgfile(mod):
    depends_str = ' '.join(mod.depends) if mod.depends else ''
    maintainer = "# Maintainer: Firstname Lastname, email at mail dot com"

    return f"""# Description: {mod.desc}
# URL: {mod.url}
{maintainer}
# Depends on: {depends_str}

name={mod.name}
version={mod.version}
release=1
source=({mod.source_url})

build() {{
    cd ${{name#*-}}-$version

    /usr/bin/pip3 install --isolate --root="$PKG" --ignore-installed --no-deps .

    find $PKG \\( -iname "README*" -o \\
                 -iname INSTALLER -o \\
                 -iname REQUESTED -o \\
                 -iname "LICENSE*"   \\) -delete

    chmod -R g-w $PKG
}}
"""


def main():
    parser = argparse.ArgumentParser(
        description='Generate CRUX port directory with Pkgfile for a Python package from PyPI'
    )
    parser.add_argument('package', help='PyPI package name (e.g. requests, pyyaml)')
    parser.add_argument('--output', '-o', metavar='DIR', default=os.getcwd(),
                        help='Base directory where the port folder will be created (default: current directory)')
    args = parser.parse_args()

    data = fetch_pypi_data(args.package)
    mod = PyModule(data)

    port_dir = os.path.join(args.output, mod.name)

    try:
        os.makedirs(port_dir, exist_ok=True)
        print(f"Created port directory: {port_dir}")
    except OSError as e:
        print(f"Error creating directory {port_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    pkgfile_path = os.path.join(port_dir, "Pkgfile")
    content = generate_pkgfile(mod)

    try:
        with open(pkgfile_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Pkgfile successfully written to: {pkgfile_path}")
        print("\nNext steps:")
        print(f"   cd {port_dir}")
        print("   pkgmk -do          # download source and build")
        print("   # Then review dependencies and adjust as needed")
    except IOError as e:
        print(f"Error writing Pkgfile: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
