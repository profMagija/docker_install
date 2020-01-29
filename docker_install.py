#!/bin/env python3

import urllib.request
import urllib.parse
import socket
import json
import shutil
import gzip
import tarfile
import tempfile
import io
import ssl

AUTH_URL = 'https://auth.docker.io/token'
REPO_URL = 'https://registry-1.docker.io'

def urlget(url, params=None, headers={}):
    if params is not None:
        url = url + '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers=headers, )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.urlopen(request, context=ctx)

def get_auth_token(service, scope):
    resp = urlget(AUTH_URL, params={
        'service': service,
        'scope': scope
    })
    return json.load(resp)['token']

def get_tags(name, token):
    resp = urlget(REPO_URL + f'/v2/{name}/tags/list', headers={
        'Authorization': f'Bearer {token}'
    })
    return json.load(resp)

def get_manifest(name, reference, token):
    resp = urlget(REPO_URL + f'/v2/{name}/manifests/{reference}', headers={
        'Authorization': f'Bearer {token}'
    })
    return json.load(resp)

def get_blob(name, digest, token):
    resp = urlget(REPO_URL + f'/v2/{name}/blobs/{digest}', headers={
        'Authorization': f'Bearer {token}'
    })
    return resp

def get_image_blobs(name, tag):
    token = get_auth_token('registry.docker.io', f'repository:{name}:pull')
    manifest = get_manifest(name, tag, token)
    for digest in manifest['fsLayers']:
        blobSum = digest['blobSum']
        print('pulling', blobSum[7:15])
        yield blobSum, get_blob(name, blobSum, token)

def do_erase():
    for tree in ['/' + x for x in 'bin etc home lib lib64 opt root run sbin srv usr var'.split()]:
        shutil.rmtree(tree, ignore_errors=True)

def apply_image(name, tag):
    erased = False
    for bsum, blob in get_image_blobs(name, tag):
        if not erased:
            do_erase()
            erased = True
        with tarfile.open(fileobj=io.BytesIO(blob.read()), mode='r:gz') as tarf:
            print('extracting', bsum[7:15])
            tarf.extractall(path="/", numeric_owner=True)

def usage(msg=None):

    import sys
    def uprint(s):
        print(s, file=sys.stderr)

    if msg is not None:
        uprint('error: ' + msg)

    uprint(f'usage: {sys.argv[0]} [OPTIONS] IMAGE')
    uprint(f'')
    uprint(f'options:')
    uprint(f'    -h   --help    display this help')
    uprint(f'')
    uprint(f'example:')
    uprint(f'    {sys.argv[0]} alpine:latest')

    sys.exit(1)

def main(args):
    import os, sys

    image = None
    tag = None

    for arg in args[1:]:
        if arg in ['-h', '--help']:
            usage()
        elif arg[0] == '-':
            usage(f'unknown argument {arg}')
        else:
            if image is not None:
                usage('only one image allowed')
            image = arg

    if image is None:
        usage('image is required')

    if ':' in image:
        image, tag = image.split(':', 1)
    else:
        tag = 'latest'

    if '/' not in image:
        image = 'library/' + image

    print(f'getting {image}:{tag}')

    apply_image(image, tag)
    print('done, starting shell ...')
    os.execl('/bin/su', '/bin/su', '-')

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))



