#!/usr/bin/env python

import os
import sys

import github


_header = '''\
<!doctype html>
<html>
<head>
<title>CuPy: Pre-Release Wheels</title>
<meta name="robots" content="noindex,nofollow" />
</head>
<body>
<h1>CuPy: Pre-Release Wheels</h1>
<pre style="color: #eeeeee; background-color: #333333; margin: 5px; padding: 10px; border-radius: 10px;">
<span style="user-select: none;">$ </span>pip install 'cupy-cudaXXX==X.Y.Z' -f https://pip.cupy.dev/pre
</pre>
'''

_footer = '''\
</body>
</html>
'''


def main(out_file):
    token = os.environ['GITHUB_TOKEN']
    repo = github.Github(token).get_repo('cupy/cupy')

    lines = [_header]
    for release in repo.get_releases():
        if not release.prerelease:
            print(f'Skipping stable release: {release.title}')
            continue
        lines.append(f'<h2>{release.title}</h2>')
        count = 0
        for asset in release.get_assets():
            count += 1
            url = asset.browser_download_url
            lines.append(f'<a href="{url}">{os.path.basename(url)}</a><br>')
        print(f'Processed: {release.title} ({count} assets)')
    lines.append(_footer)

    with open(out_file, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main(sys.argv[1])
