from PyInstaller.utils.hooks import collect_entry_point, copy_metadata

# Keyring discovers OS backends through distribution entry points at runtime.
datas, hiddenimports = collect_entry_point('keyring.backends')
datas += copy_metadata('trezor')
