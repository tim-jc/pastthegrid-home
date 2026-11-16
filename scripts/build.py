"""Build approved static files and optional text-only Standert content."""
from pathlib import Path
import shutil
import os
import sys

# Also support loading this entry point through importlib in standard-library tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bike_library
import image_assets

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "index.html",
    "assets/css/home.css",
    "assets/identity/identity.css",
    "assets/identity/symbol.svg",
    "assets/identity/favicon.svg",
)


def build(root=ROOT, bike_library_root=None):
    root = Path(root).resolve()
    source, output = root / "src", root / "dist"
    # Validate everything before removing a previous build. Reject symlinks,
    # including ancestors, so selected assets cannot escape the source tree.
    if source.is_symlink() or output.is_symlink():
        raise ValueError("src and dist must be real directories, not symlinks")
    for name in FILES:
        path = source / name
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise ValueError("Symlink source is not permitted: " + name)
        if not path.is_file():
            raise FileNotFoundError("Missing required source asset: " + name)
    template = (source / "index.html").read_text(encoding="utf-8")
    pages = {}
    asset = None
    if bike_library_root is not None:
        if not str(bike_library_root).strip():
            raise ValueError("BIKE_LIBRARY_ROOT must not be empty")
        mappings = bike_library.registry(root / 'config/bikes.json')
        bikes = bike_library.discover(bike_library_root, mappings)
        rows = bike_library.maintenance_rows(bike_library_root, mappings)
        asset = image_assets.prepare(bike_library_root, root / "config/assets.json")
        for bike in bikes:
            page, warnings, completed, planned = bike_library.render(
                bike_library_root, template, hero=asset if bike['source'] == bike_library.BIKE else None,
                bike=bike['source'], rows=rows, mappings=mappings)
            pages[bike['page']] = page
            for warning in sorted(set(warnings)):
                print("Build warning (" + bike['title'] + "): " + warning, file=sys.stderr)
            print(f"{bike['title']}: {completed} completed; {planned} planned or undated")
        pages[Path('bikes/index.html')] = bike_library.index(template, bikes)
        template = template.replace('Coming next', 'Available records').replace(
            '<p class="forthcoming">Forthcoming — beginning with the Standert Kreissäge RS.</p>',
            '<p><a class="text-link" href="bikes/">Browse the Bike Library →</a></p>')
        template = template.replace('maintenance history and supporting documents.', 'specifications, technical notes and maintenance history.')
    if output.exists():
        shutil.rmtree(output)
    for name in FILES:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    for relative, page in pages.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
    if pages:
        (output / "index.html").write_text(template, encoding="utf-8")
    if asset is not None:
        item, encoded, dimensions = asset
        target = output / item['output']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
        if image_assets.validate(target.read_bytes()) != dimensions:
            raise ValueError("Published image verification failed")
    return output


if __name__ == "__main__":
    try:
        print("Built static site: " + str(build(bike_library_root=os.environ.get("BIKE_LIBRARY_ROOT"))))
    except (OSError, ValueError, bike_library.csv.Error) as error:
        raise SystemExit("Build failed: " + str(error))
