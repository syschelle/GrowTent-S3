# Release commands for GrowTent-S3 v0.1.0

Use these commands from the local `GrowTent-S3` project folder.

## First push to the new repository

```bash
git remote set-url origin https://github.com/syschelle/GrowTent-S3.git
git add -A
git commit -m "Initial ESP32-S3 Relay 6CH firmware with pumps 4-6"
git push -u origin main
```

If the GitHub repository already contains only the generated LICENSE/README and you intentionally want this local project to become the source of truth:

```bash
git push --force-with-lease -u origin main
```

## Create the first S3 release

```bash
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Actions workflow builds `firmware.bin` from the `esp32-s3-relay-6ch` PlatformIO environment and publishes it to the GitHub release.

## If v0.1.0 already exists and must be recreated

Only do this if no device has already consumed that release via OTA.

```bash
git push --delete origin v0.1.0
git tag -d v0.1.0
git tag v0.1.0
git push origin v0.1.0
```
