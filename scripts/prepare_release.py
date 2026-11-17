"""Local release preparation only. No network, credentials or live upload adapter."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import io
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid

import publication_safety as safety

ROOT = Path(__file__).resolve().parents[1]
APP = ('scripts/build.py','scripts/bike_library.py','scripts/image_assets.py',
       'config/bikes.json','config/assets.json','src/index.html','src/assets/css/home.css',
       'src/assets/identity/identity.css','src/assets/identity/symbol.svg','src/assets/identity/favicon.svg')


def command(args, env=None, cwd=None):
    result = subprocess.run(args, env=env, cwd=cwd, capture_output=True)
    if result.returncode:
        raise ValueError('Local tool failed: ' + Path(args[0]).name)
    return result.stdout


def revision(repo, ref):
    if not ref or ref.startswith('-'):
        raise ValueError('Explicit committed source revision required')
    result = command(['git','-C',str(repo),'rev-parse','--verify',ref+'^{commit}']).decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40}', result):
        raise ValueError('Unsupported Git commit identifier')
    return result


def export(repo, commit, names, target):
    entries = command(['git','-C',str(repo),'ls-tree','-rz','--full-tree',commit]).split(b'\0')
    blobs = {}
    for entry in entries:
        if entry:
            info, name = entry.split(b'\t',1)
            mode, kind, oid = info.split()
            blobs[name.decode()] = (mode,kind,oid)
    hashes = {}
    for name in sorted(names):
        safety.safe_path(name)
        if name not in blobs or blobs[name][0] not in (b'100644',b'100755') or blobs[name][1] != b'blob':
            raise ValueError('Missing, linked or unmaterialised committed input: ' + name)
        data = command(['git','-C',str(repo),'cat-file','blob',blobs[name][2].decode()])
        if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError('Unresolved Git LFS input')
        path = target/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data);path.chmod(0o400)
        hashes[name] = safety.digest(data)
    return hashes


def hashes(tree):
    return {str(p.relative_to(tree)):safety.digest(p.read_bytes()) for p in sorted(tree.rglob('*')) if p.is_file()}


def private_directory(path):
    path = Path(path).expanduser()
    if path.is_symlink():
        raise ValueError('Storage cannot be a symlink')
    if not path.exists():
        path.mkdir(parents=True,mode=0o700)
    if not path.is_dir() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise ValueError('Storage must be owner-only (0700), owned by this user')
    return path.resolve()


@contextmanager
def private_environment(temp):
    old_umask = os.umask(0o077)
    old_tmp = tempfile.tempdir
    tempfile.tempdir = str(temp)
    try:
        yield
    finally:
        tempfile.tempdir = old_tmp
        os.umask(old_umask)


def toolchain():
    versions = {'python':sys.version.split()[0]}
    for tool, args in (('git',['--version']),('cwebp',['-version']),('dwebp',['-version']),('cjpeg',['-version'])):
        result = subprocess.run([tool,*args],capture_output=True)
        if result.returncode: raise ValueError('Build tool version unavailable: '+tool)
        versions[tool] = (result.stdout+result.stderr).decode().splitlines()[0].strip()
    versions['deployment_pins'] = safety.strict_json((ROOT/'tooling/deployment/pins.json').read_bytes())
    # Node version only; never invoke Wrangler or authentication.
    versions['observed_node'] = command(['node','--version']).decode().strip() if shutil.which('node') else 'not installed'
    return versions


def neutral_tree(tree, version, records):
    """Same validated inventory; replace all content/identity pixels with synthetic data."""
    expected = {record['path'] for record in records}
    for index, name in enumerate(sorted(expected)):
        if name in safety.CONTROL:
            continue
        marker = f'SYNTHETIC-{version}-{index:02d}'
        if name.endswith('.html'):
            depth = len(Path(name).parts)-1
            prefix = '../'*depth
            home_link = 'bikes/' if name == 'index.html' else prefix+'bikes/'
            links = ''.join('<a href="'+prefix+other+'">Fixture route</a>' for other in sorted(expected) if other.endswith('.html'))
            content = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                       '<title>Hosting fixture</title><link rel="stylesheet" href="'+prefix+'assets/css/home.css"></head>'
                       '<body><main id="main"><h1>'+marker+'</h1><a href="'+home_link+'">Fixture index</a>'+links
                       +'<img src="'+prefix+safety.PHOTO+'" width="32" height="16" alt="Synthetic colour pattern"></main></body></html>')
            (tree/name).write_text(content)
        elif name.endswith('.css'):
            (tree/name).write_text('/* '+marker+' */\nbody { margin: 1rem; font-family: sans-serif; } img { max-width: 100%; height: auto; }\n')
        elif name.endswith('.svg'):
            (tree/name).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><title>'+marker+'</title><rect width="40" height="40" fill="#345678"/></svg>')
    # Image already came from a generated synthetic source JPEG through normal build.


def freeze(tree):
    for path in tree.rglob('*'):
        path.chmod(0o500 if path.is_dir() else 0o400)
    tree.chmod(0o500)


def archive(tree, target, records):
    with tarfile.open(target,'w',format=tarfile.USTAR_FORMAT) as tar:
        for record in records:
            data = (tree/record['path']).read_bytes()
            item = tarfile.TarInfo(record['path']);item.size=len(data);item.mode=0o400
            item.uid=item.gid=item.mtime=0;item.uname=item.gname=''
            tar.addfile(item,io.BytesIO(data))
    target.chmod(0o400)


def prepare(home_repo, home_ref, bike_repo, bike_ref, storage, *, mode='private', version=None, encrypted=False):
    if mode not in ('private','synthetic') or (mode == 'synthetic' and version not in ('A','B')):
        raise ValueError('Invalid release mode/version')
    if mode == 'private' and not encrypted:
        raise ValueError('Private releases require operator-confirmed encrypted storage')
    if not bike_repo or not bike_ref:
        raise ValueError('Canonical repository and committed revision required')
    home_commit, bike_commit = revision(home_repo,home_ref), revision(bike_repo,bike_ref)
    storage = private_directory(storage)
    # Prevent accidental output inside either source repository.
    if any(storage.is_relative_to(Path(repo).resolve()) for repo in (home_repo,bike_repo)):
        raise ValueError('Release storage must be outside source repositories')
    release_id = ('synthetic-'+version.lower() if mode=='synthetic' else 'private')+'-'+uuid.uuid4().hex
    destination = storage/release_id
    # All failures clean only our newly created temporary workspace, never prior releases.
    with tempfile.TemporaryDirectory(prefix='.prepare-',dir=storage) as work:
        work=Path(work)
        temp=work/'tmp';temp.mkdir(mode=0o700)
        with private_environment(temp):
            home, bike = work/'home', work/'canonical'
            home.mkdir();bike.mkdir()
            home_hashes = export(home_repo,home_commit,APP,home)
            bikes_data=(home/'config/bikes.json').read_bytes();assets_data=(home/'config/assets.json').read_bytes()
            _, needed = safety.policy(bikes_data,assets_data)
            bike_hashes = export(bike_repo,bike_commit,needed,bike)
            if mode == 'synthetic':
                marker = bike/'SYNTHETIC_ONLY'  # sentinel must be committed; never create it in a real source.
                export(bike_repo,bike_commit,{'SYNTHETIC_ONLY'},bike)
                if marker.read_text() != 'Generated hosting fixtures only\n':
                    raise ValueError('Not a generated synthetic fixture repository')
                # Sentinel validated separately; source records must also be neutral.
                for name in needed:
                    if name.endswith('.md') and not (bike/name).read_text().startswith('# Fixture '):
                        raise ValueError('Synthetic source is not neutral')
                bike_hashes=hashes(bike)
            # Only output directory is writable; source exports remain read-only.
            env={'PATH':os.environ.get('PATH',''),'LANG':'en_US.UTF-8','TMPDIR':str(temp),
                 'PYTHONDONTWRITEBYTECODE':'1','BIKE_LIBRARY_ROOT':str(bike)}
            command([sys.executable,str(home/'scripts/build.py')],env=env,cwd=home)
            if hashes(bike)!=bike_hashes or any(hashes(home).get(n)!=h for n,h in home_hashes.items()):
                raise ValueError('Committed source inputs changed during build')
            tree=home/'dist'
            for name,source in safety.CONTROL.items():
                (tree/name).write_bytes(source.read_bytes())
            records=safety.validate(tree,bikes_data,assets_data)
            if mode=='synthetic':
                neutral_tree(tree,version,records)
                records=safety.validate(tree,bikes_data,assets_data)
            result=work/'result';result.mkdir()
            shutil.move(str(tree),str(result/'publication'))
            metadata=result/'metadata';metadata.mkdir()
            (metadata/'bikes.json').write_bytes(bikes_data)
            (metadata/'assets.json').write_bytes(assets_data)
            archive(result/'publication',result/'publication.tar',records)
            workflow = {name:safety.digest((ROOT/name).read_bytes()) for name in
                        ('scripts/prepare_release.py','scripts/publication_safety.py','release/headers.txt','release/404.html','tooling/deployment/pins.json')}
            manifest={'schema':1,'release_id':release_id,'prepared_at':datetime.now(timezone.utc).isoformat(),
                      'mode':mode,'fixture_version':version,'state':'prepared-not-deployed',
                      'test_cases':[{'path':'/bikes','purpose':'canonical slash redirect'},{'path':'/bikes/index.html','purpose':'direct index/normalisation'},{'path':'/unknown-fixture-route','purpose':'non-sensitive 404; no SPA fallback'}] if mode=='synthetic' else [],
                      'sources':{'home':home_commit,'bike_library':bike_commit},
                      'input_hashes':{'home':home_hashes,'bike_library':bike_hashes},
                      'workflow_hashes':workflow,'toolchain':toolchain(),
                      'storage':'operator-attested-encrypted' if encrypted else 'synthetic-only-no-private-data',
                      'files':records,'archive_sha256':safety.digest((result/'publication.tar').read_bytes()),
                      'validation':{'source_integrity':True,'independent_publication_safety':True,'deployment_tests':'Not run'}}
            data=safety.canonical(manifest)
            (result/'manifest.json').write_bytes(data)
            (result/'manifest.sha256').write_text(safety.digest(data)+'\n')
            for path in result.rglob('*'):
                if path.is_file():path.chmod(0o400)
            freeze(result/'publication')
            verify(result)
            result.rename(destination)
    return destination


def verify(release):
    release=Path(release)
    if release.is_symlink() or not release.is_dir():raise ValueError('Invalid release directory')
    required={'publication','metadata','publication.tar','manifest.json','manifest.sha256'}
    if {p.name for p in release.iterdir()} != required:raise ValueError('Unexpected release metadata')
    for path in release.rglob('*'):
        mode=path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)) or path.stat().st_uid!=os.getuid() or mode & 0o077:
            raise ValueError('Unsafe release object/permissions')
    data=(release/'manifest.json').read_bytes()
    if safety.digest(data)!=(release/'manifest.sha256').read_text().strip():raise ValueError('Manifest integrity failed')
    manifest=safety.strict_json(data)
    if set(manifest)!={'schema','release_id','prepared_at','mode','fixture_version','state','test_cases','sources','input_hashes','workflow_hashes','toolchain','storage','files','archive_sha256','validation'}:
        raise ValueError('Unknown manifest fields')
    if manifest['schema']!=1 or manifest['state']!='prepared-not-deployed':raise ValueError('Invalid prepared release state')
    if set(manifest['sources'])!={'home','bike_library'} or not all(re.fullmatch('[0-9a-f]{40}',v) for v in manifest['sources'].values()):
        raise ValueError('Missing full committed source identities')
    if manifest['mode'] not in ('private','synthetic') or manifest['validation']!={'source_integrity':True,'independent_publication_safety':True,'deployment_tests':'Not run'}:
        raise ValueError('Invalid validation/mode record')
    if manifest['mode']=='private' and manifest['storage']!='operator-attested-encrypted':raise ValueError('Encrypted storage attestation missing')
    if set(p.name for p in (release/'metadata').iterdir())!={'bikes.json','assets.json'}:raise ValueError('Unexpected policy metadata')
    bikes_data=(release/'metadata/bikes.json').read_bytes();assets_data=(release/'metadata/assets.json').read_bytes()
    for name,content in (('config/bikes.json',bikes_data),('config/assets.json',assets_data)):
        if safety.digest(content)!=manifest['input_hashes']['home'][name]:raise ValueError('Policy input hash changed')
    safety.validate(release/'publication',bikes_data,assets_data,manifest['files'])
    if safety.digest((release/'publication.tar').read_bytes())!=manifest['archive_sha256']:raise ValueError('Archive checksum failed')
    with tarfile.open(release/'publication.tar','r:') as tar:
        members=tar.getmembers()
        if [m.name for m in members]!=[f['path'] for f in manifest['files']]:raise ValueError('Archive inventory failed')
        for member,record in zip(members,manifest['files']):
            if not member.isfile() or member.size!=record['size'] or safety.digest(tar.extractfile(member).read())!=record['sha256']:
                raise ValueError('Archive content failed')
    return manifest


def restore(release, target):
    manifest=verify(release)
    target=Path(target)
    if target.exists() or target.is_symlink():raise ValueError('Restore target must not exist')
    with private_environment(target.parent):
        target.mkdir(mode=0o700)
        try:
            with tarfile.open(Path(release)/'publication.tar','r:') as tar:
                for member in tar.getmembers():
                    path=target/safety.safe_path(member.name);path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_bytes(tar.extractfile(member).read())
            safety.validate(target,(Path(release)/'metadata/bikes.json').read_bytes(),(Path(release)/'metadata/assets.json').read_bytes(),manifest['files'])
            freeze(target)
        except Exception:
            shutil.rmtree(target);raise
    return target


def preflight(release, *, account, project, hostname, owner_authorised=False, access_verified=False):
    manifest=verify(release)
    if not re.fullmatch(r'[0-9a-f]{32}',account) or not re.fullmatch(r'[a-z0-9-]+',project) or hostname!='home.pastthegrid.uk':
        raise ValueError('Explicit named destination required')
    if not owner_authorised or not access_verified:raise ValueError('Owner authorisation and independent live Access evidence required')
    return manifest


def dry_run(release, **destination):
    preflight(release,**destination)
    return {'result':'local-preflight-only','upload_invocations':0,'live_upload_enabled':False}


def fixtures(home_repo, home_ref, target):
    """Create neutral canonical Git fixture; no actual Bike Library is accessed."""
    target=Path(target)
    if target.exists():raise ValueError('Fixture directory must not exist')
    commit=revision(home_repo,home_ref)
    target.mkdir(mode=0o700,parents=True)
    with tempfile.TemporaryDirectory(dir=target) as work:
        home=Path(work)/'home';home.mkdir()
        export(home_repo,commit,APP,home)
        bike=target/'canonical';bike.mkdir()
        bikes=safety.strict_json((home/'config/bikes.json').read_bytes())
        assets=safety.strict_json((home/'config/assets.json').read_bytes())
        _,needed=safety.policy((home/'config/bikes.json').read_bytes(),(home/'config/assets.json').read_bytes())
        for i,name in enumerate(sorted(bikes)):
            path=bike/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(f'# Fixture {i+1}\n\n## Summary\n\n| Item | Specification |\n|---|---|\n| Status | Fixture |\n\n# Technical notes\n\nSynthetic content only.\n')
        log=bike/'workshop/maintenance_log.csv';log.parent.mkdir()
        log.write_text('work_date,bike,work_done,notes\n')
        pixels=b'P6\n32 16\n255\n'+bytes([50,100,150])*32*16
        image=subprocess.run(['cjpeg','-quality','90'],input=pixels,capture_output=True,check=True).stdout
        path=bike/assets['standert-hero']['source'];path.parent.mkdir(parents=True);path.write_bytes(image)
        (bike/'SYNTHETIC_ONLY').write_text('Generated hosting fixtures only\n')
        command(['git','init','-q',str(bike)])
        command(['git','-C',str(bike),'add','.'])
        command(['git','-C',str(bike),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Synthetic source fixture'])
    return bike



def record_receipt(release, receipt, ledger):
    """Import external evidence or test-double receipt; never contact a service.

    Live verification is an operator attestation, not proved by this local parser.
    Simulation receipts cannot promote any production retention pointers.
    """
    manifest=verify(release)
    if set(receipt)!={'schema','kind','deployment_id','account','project','hostname','verified_at','outcome','evidence_sha256'}:
        raise ValueError('Invalid receipt schema')
    if receipt['schema']!=1 or receipt['kind'] not in ('simulation','owner-attested-live') or receipt['outcome'] not in ('verified','failed'):
        raise ValueError('Invalid receipt classification')
    if not re.fullmatch(r'[a-zA-Z0-9-]{1,100}',receipt['deployment_id']) or not re.fullmatch('[0-9a-f]{64}',receipt['evidence_sha256']):
        raise ValueError('Invalid receipt evidence')
    if not re.fullmatch('[0-9a-f]{32}',receipt['account']) or not re.fullmatch('[a-z0-9-]+',receipt['project']) or receipt['hostname']!='home.pastthegrid.uk':
        raise ValueError('Invalid receipt destination')
    when=datetime.fromisoformat(receipt['verified_at'])
    if when.tzinfo is None:raise ValueError('Receipt timestamp must have timezone')
    ledger=private_directory(ledger)
    if ledger.is_relative_to(Path(release).resolve()):raise ValueError('Receipts must remain outside immutable release')
    event=dict(receipt,release_id=manifest['release_id'],manifest_sha256=safety.digest((Path(release)/'manifest.json').read_bytes()),sources=manifest['sources'])
    path=ledger/(uuid.uuid4().hex+'.json')
    with private_environment(ledger):
        path.write_bytes(safety.canonical(event));path.chmod(0o400)
    return path


def retention_plan(ledger, *, kind='simulation', account, project):
    """A non-destructive plan. Retain two distinct verified releases per destination."""
    events=[]
    for path in Path(ledger).glob('*.json'):
        if path.is_symlink() or not path.is_file():raise ValueError('Unsafe ledger object')
        event=safety.strict_json(path.read_bytes())
        if event['kind']==kind and event['account']==account and event['project']==project and event['outcome']=='verified':
            events.append(event)
    events.sort(key=lambda event:datetime.fromisoformat(event['verified_at']),reverse=True)
    distinct=[]
    for event in events:
        if event['release_id'] not in [e['release_id'] for e in distinct]:distinct.append(event)
    return {'classification':kind,'current':distinct[0] if distinct else None,
            'previous':distinct[1] if len(distinct)>1 else None,
            'superseded':[event['release_id'] for event in distinct[2:]],'deletion_performed':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    fixture=sub.add_parser('fixtures');fixture.add_argument('--home-repo',required=True);fixture.add_argument('--home-ref',required=True);fixture.add_argument('--directory',required=True)
    prep=sub.add_parser('prepare')
    for name in ('home-repo','home-ref','bike-repo','bike-ref','storage'):prep.add_argument('--'+name,required=True)
    prep.add_argument('--synthetic-version',choices=['A','B']);prep.add_argument('--confirm-encrypted-storage',action='store_true')
    for action in ('verify','restore','preflight'):
        p=sub.add_parser(action);p.add_argument('release')
        if action=='restore':p.add_argument('--target',required=True)
        if action=='preflight':
            p.add_argument('--account',required=True);p.add_argument('--project',required=True);p.add_argument('--hostname',required=True)
    receipt=sub.add_parser('receipt');receipt.add_argument('release');receipt.add_argument('--file',required=True);receipt.add_argument('--ledger',required=True)
    retention=sub.add_parser('retention');retention.add_argument('--ledger',required=True);retention.add_argument('--account',required=True);retention.add_argument('--project',required=True);retention.add_argument('--kind',choices=['simulation','owner-attested-live'],default='simulation')
    args=parser.parse_args()
    if args.action=='fixtures':print(fixtures(args.home_repo,args.home_ref,args.directory))
    elif args.action=='prepare':print(prepare(args.home_repo,args.home_ref,args.bike_repo,args.bike_ref,args.storage,mode='synthetic' if args.synthetic_version else 'private',version=args.synthetic_version,encrypted=args.confirm_encrypted_storage))
    elif args.action=='verify':print(safety.canonical(verify(args.release)).decode(),end='')
    elif args.action=='restore':print(restore(args.release,args.target))
    elif args.action=='receipt':
        print(record_receipt(args.release,safety.strict_json(Path(args.file).read_bytes()),args.ledger))
    elif args.action=='retention':
        print(safety.canonical(retention_plan(args.ledger,kind=args.kind,account=args.account,project=args.project)).decode(),end='')
    elif args.action=='preflight':
        # Live evidence and publication authorisation cannot be asserted by this CLI.
        dry_run(args.release,account=args.account,project=args.project,hostname=args.hostname)


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,tarfile.TarError) as error:
        raise SystemExit('Release operation failed: '+str(error))
