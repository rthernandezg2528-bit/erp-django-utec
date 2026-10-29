from whitenoise.storage import CompressedManifestStaticFilesStorage


class NonStrictManifestStorage(CompressedManifestStaticFilesStorage):
    """Si falta un archivo en el manifiesto, usa la URL normal en vez de dar 500."""
    manifest_strict = False