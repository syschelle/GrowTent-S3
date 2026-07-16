# Release commands for GrowTent-S3 v0.1.3

Run these commands from the local `syschelle/GrowTent-S3` repository after
copying the updated project files into it.

## Commit the UI and relay-name migration

```bash
git status
git add -A
git commit -m "Update S3 board label and restore relay 4-6 names"
git push origin main
```

## Create release v0.1.3

```bash
git tag v0.1.3
git push origin v0.1.3
```

The GitHub Actions workflow builds `firmware.bin` from the
`esp32-s3-relay-6ch` PlatformIO environment and publishes it to the release.

## If the local v0.1.3 tag already exists but was not pushed

```bash
git tag -d v0.1.3
git tag v0.1.3
git push origin v0.1.3
```

## If v0.1.3 already exists remotely and must be recreated

Only recreate a published tag when no device has already consumed that
release through OTA.

```bash
git push --delete origin v0.1.3
git tag -d v0.1.3
git tag v0.1.3
git push origin v0.1.3
```
