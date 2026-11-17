"""Synthetic Git repositories only; no real canonical data, network or credentials."""
import copy
from pathlib import Path
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import prepare_release as release
import publication_safety as safety


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.base=Path(cls.temp.name)
        cls.home=cls.base/'home';cls.home.mkdir()
        for name in release.APP:
            path=cls.home/name;path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(release.ROOT/name,path)
        release.command(['git','init','-q',str(cls.home)])
        cls.commit(cls.home)
        cls.home_ref=release.revision(cls.home,'HEAD')
        cls.bike=release.fixtures(cls.home,cls.home_ref,cls.base/'fixture')
        cls.bike_ref=release.revision(cls.bike,'HEAD')
        cls.valid=release.prepare(cls.home,cls.home_ref,cls.bike,cls.bike_ref,cls.base/'releases',mode='synthetic',version='A')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def commit(repo):
        release.command(['git','-C',str(repo),'add','.'])
        release.command(['git','-C',str(repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Fixture revision'])

    def setUp(self):
        self.work=tempfile.TemporaryDirectory(dir=self.base);self.addCleanup(self.work.cleanup)
        self.work=Path(self.work.name)
        self.copy=self.work/'release';shutil.copytree(self.valid,self.copy)

    def mutate(self,name,data=b'bad'):
        target=self.copy/'publication'/name
        (self.copy/'publication').chmod(0o700)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.parent.chmod(0o700)
        if target.exists():target.chmod(0o600)
        target.write_bytes(data)

    def test_positive_release_and_manifest(self):
        manifest=release.verify(self.valid)
        self.assertEqual(manifest['state'],'prepared-not-deployed')
        self.assertEqual(manifest['validation']['deployment_tests'],'Not run')
        self.assertEqual(len(manifest['files']),17)
        self.assertEqual(manifest['sources'],{'home':self.home_ref,'bike_library':self.bike_ref})
        self.assertNotIn(str(self.base),(self.valid/'manifest.json').read_text())
        for path in self.valid.rglob('*'):
            self.assertFalse(path.stat().st_mode & 0o077)
        self.assertTrue(all(not (p.stat().st_mode & stat.S_IWUSR) for p in (self.valid/'publication').rglob('*')))
        self.assertEqual({r['path'] for r in manifest['files']},safety.policy((self.valid/'metadata/bikes.json').read_bytes(),(self.valid/'metadata/assets.json').read_bytes())[0])

    def test_unexpected_files_fail_before_test_double(self):
        for name in ('extra.pdf','source.md','workshop/maintenance_log.csv','.env','_redirects','_worker.js','assets/photo.jpg','stale.html'):
            with self.subTest(name=name):
                self.mutate(name)
                uploader=Mock()
                with self.assertRaises(ValueError):
                    release.preflight(self.copy,account='a'*32,project='fixture',hostname='home.pastthegrid.uk',owner_authorised=True,access_verified=True)
                    uploader(self.copy/'publication')
                uploader.assert_not_called()
                (self.copy/'publication'/name).unlink()
                # Remove only test-created now-empty directories.
                for directory in sorted((self.copy/'publication').rglob('*'),reverse=True):
                    if directory.is_dir() and not any(directory.iterdir()):directory.rmdir()

    def test_mutated_bytes_and_controls(self):
        for name in ('index.html','_headers','404.html',safety.PHOTO):
            with self.subTest(name=name):
                original=(self.copy/'publication'/name).read_bytes()
                self.mutate(name,original+b'changed')
                with self.assertRaises(ValueError):release.verify(self.copy)
                self.mutate(name,original)

    def test_symlinks_fifo_and_policy_change(self):
        target=self.copy/'publication/index.html';target.parent.chmod(0o700);target.unlink()
        target.symlink_to(self.valid/'publication/index.html')
        with self.assertRaises(ValueError):release.verify(self.copy)
        target.unlink();os.mkfifo(target,0o600)
        with self.assertRaises(ValueError):release.verify(self.copy)
        target.unlink()
        policy=safety.strict_json((self.valid/'metadata/assets.json').read_bytes())
        policy['standert-hero']['source']='../private.jpg'
        with self.assertRaises(ValueError):safety.policy((self.valid/'metadata/bikes.json').read_bytes(),safety.canonical(policy))

    def test_image_metadata_and_broken_links_independent_of_hash_list(self):
        data=(self.copy/'publication'/safety.PHOTO).read_bytes()
        dirty=data+b'EXIF\x04\0\0\0test';dirty=dirty[:4]+(len(dirty)-8).to_bytes(4,'little')+dirty[8:]
        self.mutate(safety.PHOTO,dirty)
        with self.assertRaises(ValueError):
            safety.validate(self.copy/'publication',(self.copy/'metadata/bikes.json').read_bytes(),(self.copy/'metadata/assets.json').read_bytes())
        self.mutate(safety.PHOTO,data)
        index=(self.copy/'publication/index.html').read_text()
        for text in (index.replace('bikes/','missing/',1),index.replace('</main>','<script>alert(1)</script></main>'),index.replace('</main>','<p>/Users/private/file</p></main>'),index.replace('href="bikes/"','href="./"')):
            self.mutate('index.html',text.encode())
            with self.assertRaises(ValueError):safety.validate(self.copy/'publication',(self.copy/'metadata/bikes.json').read_bytes(),(self.copy/'metadata/assets.json').read_bytes())

    def test_archive_corruption_and_exact_restore(self):
        restored=release.restore(self.valid,self.work/'restored')
        self.assertEqual(safety.inventory(restored),safety.inventory(self.valid/'publication'))
        archive=self.copy/'publication.tar';archive.chmod(0o600);archive.write_bytes(b'corrupt')
        with self.assertRaises(ValueError):release.verify(self.copy)

    def test_invalid_revision_missing_configuration_and_storage(self):
        for args in ((self.home,'missing',self.bike,self.bike_ref),(self.home,self.home_ref,None,None)):
            with self.assertRaises(ValueError):release.prepare(*args,self.work/'storage',mode='synthetic',version='A')
        with self.assertRaisesRegex(ValueError,'encrypted'):
            release.prepare(self.home,self.home_ref,self.bike,self.bike_ref,self.work/'storage')
        unsafe=self.work/'unsafe';unsafe.mkdir(mode=0o755);unsafe.chmod(0o755)
        with self.assertRaises(ValueError):release.private_directory(unsafe)

    def test_dirty_everyday_repos_ignored_and_reproducible_payload(self):
        before_home=release.command(['git','-C',str(self.home),'status','--porcelain'])
        before_bike=release.command(['git','-C',str(self.bike),'status','--porcelain'])
        # These are fixture repos; deliberately dirty both, then select older commits.
        h=self.home/'src/index.html';b=self.bike/'workshop/maintenance_log.csv'
        oldh,oldb=h.read_bytes(),b.read_bytes()
        try:
            h.write_text('everyday edit');b.write_text('everyday edit')
            statuses=[release.command(['git','-C',str(p),'status','--porcelain']) for p in (self.home,self.bike)]
            second=release.prepare(self.home,self.home_ref,self.bike,self.bike_ref,self.work/'storage',mode='synthetic',version='A')
            self.assertEqual(h.read_text(),'everyday edit');self.assertEqual(b.read_text(),'everyday edit')
            self.assertEqual(statuses,[release.command(['git','-C',str(p),'status','--porcelain']) for p in (self.home,self.bike)])
            self.assertEqual((second/'publication.tar').read_bytes(),(self.valid/'publication.tar').read_bytes())
        finally:h.write_bytes(oldh);b.write_bytes(oldb)
        self.assertEqual(before_home,release.command(['git','-C',str(self.home),'status','--porcelain']))
        self.assertEqual(before_bike,release.command(['git','-C',str(self.bike),'status','--porcelain']))

    def test_missing_lfs_and_bad_record_fail_without_release(self):
        for kind in ('missing','lfs','bad-record','missing-config'):
            repo=self.work/kind;shutil.copytree(self.bike,repo)
            if kind=='missing':(repo/'photos/standert/standert.jpg').unlink()
            elif kind=='lfs':(repo/'photos/standert/standert.jpg').write_text('version https://git-lfs.github.com/spec/v1\n')
            elif kind=='bad-record':(repo/'workshop/maintenance_log.csv').write_text('invalid,columns\n')
            else:
                repo=self.work/'home-missing-config';shutil.copytree(self.home,repo);(repo/'config/assets.json').unlink()
            self.commit(repo)
            storage=self.work/(kind+'-storage')
            with self.assertRaises(ValueError):release.prepare(repo if kind=='missing-config' else self.home,'HEAD' if kind=='missing-config' else self.home_ref,repo if kind!='missing-config' else self.bike,'HEAD',storage,mode='synthetic',version='A')
            self.assertFalse(storage.exists() and any(storage.iterdir()))

    def test_preflight_fails_closed_and_never_uploads(self):
        uploader=Mock()
        with self.assertRaises(ValueError):
            release.preflight(self.valid,account='a'*32,project='fixture',hostname='home.pastthegrid.uk')
            uploader()
        uploader.assert_not_called()
        result=release.dry_run(self.valid,account='a'*32,project='fixture',hostname='home.pastthegrid.uk',owner_authorised=True,access_verified=True)
        self.assertEqual(result['upload_invocations'],0)
        self.assertFalse(result['live_upload_enabled'])

    def test_placeholder_stale_output_and_frozen_hash(self):
        repo=self.work/'placeholder';shutil.copytree(self.home,repo)
        (repo/'scripts/build.py').write_text("from pathlib import Path\np=Path(__file__).resolve().parents[1]/'dist'\np.mkdir()\n(p/'index.html').write_text('<!doctype html><main><h1>Placeholder</h1></main>')\n")
        self.commit(repo)
        with self.assertRaises(ValueError):release.prepare(repo,'HEAD',self.bike,self.bike_ref,self.work/'storage',mode='synthetic',version='A')
        # Valid CSS with changed bytes must fail the frozen hash, independent of syntax.
        path=self.copy/'publication/assets/css/home.css'
        self.mutate('assets/css/home.css',path.read_bytes()+b'/* mutation */')
        with self.assertRaisesRegex(ValueError,'frozen manifest'):release.verify(self.copy)
        # Stale everyday build output is not exported from a selected Git revision.
        stale=self.home/'dist/stale.pdf';stale.parent.mkdir(exist_ok=True);stale.write_bytes(b'stale')
        try:
            prepared=release.prepare(self.home,self.home_ref,self.bike,self.bike_ref,self.work/'storage2',mode='synthetic',version='A')
            self.assertFalse((prepared/'publication/stale.pdf').exists())
            self.assertTrue(stale.exists())
        finally:stale.unlink();stale.parent.rmdir()

    def test_retains_current_previous_and_only_plans_older_removal(self):
        ledger=self.work/'ledger';releases=[self.valid]
        for version in ('B','A'):
            releases.append(release.prepare(self.home,self.home_ref,self.bike,self.bike_ref,self.work/'retained',mode='synthetic',version=version))
        for i,prepared in enumerate(releases):
            receipt={'schema':1,'kind':'simulation','deployment_id':'fixture-'+str(i),'account':'a'*32,'project':'fixture','hostname':'home.pastthegrid.uk','verified_at':f'2026-11-17T1{i}:00:00+00:00','outcome':'verified','evidence_sha256':'b'*64}
            release.record_receipt(prepared,receipt,ledger)
        plan=release.retention_plan(ledger,account='a'*32,project='fixture')
        self.assertEqual(plan['current']['release_id'],release.verify(releases[2])['release_id'])
        self.assertEqual(plan['previous']['release_id'],release.verify(releases[1])['release_id'])
        self.assertEqual(plan['superseded'],[release.verify(releases[0])['release_id']])
        for prepared in releases:self.assertTrue((prepared/'publication.tar').is_file())

    def test_simulation_receipts_retention_no_production_promotion(self):
        ledger=self.work/'ledger'
        receipt={'schema':1,'kind':'simulation','deployment_id':'fixture-1','account':'a'*32,'project':'fixture','hostname':'home.pastthegrid.uk','verified_at':'2026-11-17T12:00:00+00:00','outcome':'verified','evidence_sha256':'b'*64}
        original=(self.valid/'manifest.json').read_bytes()
        release.record_receipt(self.valid,receipt,ledger)
        plan=release.retention_plan(ledger,account='a'*32,project='fixture')
        self.assertEqual(plan['current']['release_id'],release.verify(self.valid)['release_id'])
        self.assertFalse(plan['deletion_performed'])
        live=release.retention_plan(ledger,kind='owner-attested-live',account='a'*32,project='fixture')
        self.assertIsNone(live['current'])
        self.assertEqual(original,(self.valid/'manifest.json').read_bytes())


if __name__=='__main__':unittest.main()
