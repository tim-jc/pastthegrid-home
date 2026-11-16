# Standert photograph — Slice 2

Owner selected `standert.jpg` on 2026-11-12 and requested the Slice 2 rerun.
Inspection confirmed a landscape JPEG, 2200 × 1238, showing the complete silver
Standert alongside a railing and winding road. No source location metadata is
recorded here. Source photographs remain in Bike Library, never in Home's Git.

## Manifest and output

- Manifest: `config/assets.json`, identifier `standert-hero`.
- Canonical source: `photos/standert/standert.jpg`, relative to `BIKE_LIBRARY_ROOT`.
- Generated output: `dist/assets/bikes/standert/hero.webp`.
- Approved use: Standert hero photograph only.
- Actual derivative: 1600 × 901, 258,026 bytes (source: 1,047,302 bytes).
- Page: `bikes/standert/kreissage_rs/`.

The manifest declares source, output, type, use, alt text and caption. It accepts
exact relative paths only, forbids traversal, wildcards and absolute paths, and
requires source resolution to stay inside the configured root. Only JPEG input
and the single fixed output/use are supported. Source suffix and JPEG signature
are checked; other formats fail. It is publication configuration, not bike data.

## Processing and dependencies

Python 3.9+ with installed libwebp `cwebp` and `dwebp` (validated with 1.6.0).
Tests also use `cjpeg` to create synthetic JPEGs. No remote/runtime dependencies.
Pillow was unavailable and network installation was blocked; the existing libwebp
tools provide supported codecs without another Python dependency. The build is
not tied to macOS image conversion utilities.

1. Read selected JPEG into a temporary snapshot; original is never opened for write.
2. Read only the EXIF orientation field, without logging metadata values.
3. Decode JPEG via a lossless WebP intermediate and `dwebp` RGB PPM pixels.
4. Apply EXIF orientation 1–8 to that RGB pixel buffer.
5. Encode a fresh RGB PNG with only IHDR, IDAT and IEND chunks in temporary storage.
6. Encode lossy WebP: quality 82, method 6, metadata none, maximum dimension 1600,
   preserving aspect ratio and avoiding upscaling. No crop or colour-profile copy.
7. Inspect the actual encoded container: only one opaque VP8 pixel chunk is allowed.
   EXIF, XMP, ICC, comments, animation, thumbnails, unknown chunks and trailing data
   fail validation. Independently decode with `dwebp` and check actual dimensions.
8. Write only verified WebP bytes to the allowlisted output, then inspect those bytes
   again. No original JPEG or temporary intermediate is copied to `dist/`.

This is fresh pixel-based encoding, not EXIF deletion from an original file. The
build fails if metadata-free output cannot be demonstrated. Native-tool errors are
sanitised so diagnostics do not print source metadata or local tool paths.

Rebuild using the README command after replacing the canonical source image.
Identical sources and the same codec versions/settings yield identical output;
byte identity across libwebp versions is not guaranteed. Review colour and quality
when changing sources, especially images with non-sRGB profiles. Metadata removal
does not anonymise visual content, such as faces, signs or identifiable scenery.

## Integration and boundaries

The figure follows the bike title, uses descriptive alt text and a restrained
caption, preserves intrinsic dimensions to reserve space, and renders at full
available width up to 960px with automatic height. There is no crop, lightbox,
external image host or gallery script. Specifications and maintenance are unchanged.
Without source configuration the placeholder remains dependency-free. A configured
build with a missing approved photograph fails before replacing previous output.

All other local references remain suppressed. The owner-requested Markdown link
is supplied in `docs/standert-photo-link.patch`; the workspace sandbox denied writing
the Bike Library file. The patch is unapplied. Home already displays the manifest
photo and supports the canonical link once the owner applies it. No build step
writes to Bike Library.

## Validation and next slice

Synthetic fixtures include orientation, GPS coordinates, EXIF thumbnail pointers,
XMP and comments. Tests cover all eight pixel mappings, real orientation correction,
aspect ratio, resize, metadata-container rejection, source integrity, reproducible
encoding, manifest validation, unsafe symlinks, absent/mislabelled input, the exact
output inventory, approved/unapproved Markdown references and both build modes.

Actual image inspected visually; complete bike remains visible. Actual output,
relative references, source hash preservation and byte-identical rebuild verified.
Six-width browser validation remains pending because local server binding is denied
by the execution sandbox. No browser visual acceptance is claimed.

Suggested Slice 3: complete phone/browser acceptance and refine record navigation
if needed before extending media or adding other bikes. Keep deployment separate.
