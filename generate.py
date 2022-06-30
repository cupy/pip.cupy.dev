#!/usr/bin/env python

import os
import sys

import github


_header = '''\
<!doctype html>
<html>
<head>
<title>CuPy: {title}</title>
<meta name="robots" content="noindex,nofollow" />
</head>
<body>
<h1>CuPy: {title}</h1>
<pre style="color: #eeeeee; background-color: #333333; margin: 5px; padding: 10px; border-radius: 10px;">
<span style="user-select: none;">$ </span>{command}
</pre>
'''

_footer = '''\
</body>
</html>
'''


class Generator:
    def __init__(self):
        self._lines = None

    def process_release(self, release):
        self._lines.append(f'<h2>{release.title}</h2>')
        count = 0
        for asset in release.get_assets():
            self.process_asset(asset)
            count += 1
        print(f'Processed: {release.title} ({count} assets)')

    def process_asset(self, asset):
        url = asset.browser_download_url
        self._lines.append(f'<a href="{url}">{os.path.basename(url)}</a><br>')

    def generate(self, repo, out_file, *, title, command):
        print(f'=== Generating {out_file}')
        self._lines = [
            _header.format(title=title, command=command)
        ]
        for release in repo.get_releases():
            self.process_release(release)
        self._lines.append(_footer)
        output = '\n'.join(self._lines)
        with open(out_file, 'w') as f:
            f.write(output)


class PreReleaseGenerator(Generator):
    def process_release(self, release):
        if not release.prerelease:
            print(f'Skipping stable release: {release.title}')
            return
        super().process_release(release)


class AArch64Generator(Generator):
    def process_asset(self, asset):
        if not 'aarch64' in asset.name:
            print(f'Skipping non-aarch64 asset: {asset.name}')
            return
        super().process_asset(asset)


def main(out_dir):
    token = os.environ['GITHUB_TOKEN']
    repo = github.Github(token).get_repo('cupy/cupy')

    gen = PreReleaseGenerator()
    output = gen.generate(
        repo,
        f'{out_dir}/pre/index.html',
        title='Pre-Release Wheels',
        command='pip install --pre cupy-cudaXXX -f https://pip.cupy.dev/pre',
    )

    gen = AArch64Generator()
    output = gen.generate(
        repo,
        f'{out_dir}/aarch64/index.html',
        title='Arm Wheels',
        command='pip install cupy-cudaXXX -f https://pip.cupy.dev/aarch64',
    )


if __name__ == '__main__':
    main(sys.argv[1])
