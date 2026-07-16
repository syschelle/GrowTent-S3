# Release commands for GrowTent-S3 v0.1.0

Use these commands from the existing local clone of `syschelle/GrowTent-S3` after replacing the project files with the contents of this package.

## Commit the relay-layout change

```bash
git status
git add -A
git commit -m "Use relays 1-3 for pumps and 4-6 for control"
git push origin main
```

## Create the first S3 release

```bash
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Actions workflow builds `firmware.bin` from the `esp32-s3-relay-6ch` PlatformIO environment and publishes it to the GitHub release.

## If the local v0.1.0 tag already exists but was not pushed

```bash
git tag -d v0.1.0
git tag v0.1.0
git push origin v0.1.0
```

## If v0.1.0 already exists remotely and must be recreated

Only do this if no device has already consumed that release via OTA.

```bash
git push --delete origin v0.1.0
git tag -d v0.1.0
git tag v0.1.0
git push origin v0.1.0
```
