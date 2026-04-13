# Publishing Your Mod

> [Compatibility Guide](compatibility.md) | Guides | [Troubleshooting](troubleshooting.md)

Your mod works. Time to get it out there.

## Before You Upload

Quick sanity check:

- `mod.txt` is at the root of the archive (not nested in a folder)
- `name`, `id`, and `version` are set
- Archive uses forward-slash paths (not Windows backslashes)
- No leftover debug `print()` spam in the log
- Ran the compatibility analyzer, no critical warnings
- Tested with at least one other popular mod installed
- Archive is `.vmz` or `.zip`

## Uploading to ModWorkshop

1. Go to ModWorkshop and log in
2. Click **Upload Mod**
3. Fill in the name, description, select "Road to Vostok" as the game, pick a category
4. Submit the mod page
5. Edit it, go to **Downloads & Updates**, upload your archive
6. In **Dependencies & Instructions**, select the **"VostokMods .ZIP"** template
7. Publish

## Auto-Updates

The mod loader can check ModWorkshop for newer versions and offer downloads. To hook this up:

Find your ModWorkshop ID — it's the number in your mod's URL:

```
https://modworkshop.net/mod/55672/edit
                            ^^^^^
```

Add it to `mod.txt`:

```ini
[updates]
modworkshop=55672
```

The launcher's **Updates tab** lets users check ModWorkshop for newer versions. They click "Check for Updates" to compare versions, then "Download" for any mod that has an update available. The loader compares your `mod.txt` version against what's on ModWorkshop.

## Pushing Updates

1. Bump `version` in `mod.txt` (e.g., `1.0.0` → `1.1.0`)
2. Re-zip
3. Upload the new version on ModWorkshop under **Downloads & Updates**
4. Click the radio button next to the latest version to make it active
5. Set the version name via the gear menu to match your `mod.txt` version

Keep the ModWorkshop version string in sync with your `mod.txt` version. A mismatch causes unnecessary downloads.

## Versioning

Use dot-separated version numbers (the mod loader compares integer parts; pre-release tags like `1.0.0-beta.1` are not supported):

```
1.0.0 → 1.0.1   Bug fix
1.0.0 → 1.1.0   New feature
1.0.0 → 2.0.0   Breaking change
```

When a game update breaks your mod and you just need to fix compatibility, bump the patch version and note the game build in your changelog:

```
1.0.1 - Updated for RTV Demo build 2025.03.15
```

## Write a Decent Description

Your ModWorkshop page should cover:
- What the mod does (one sentence)
- How to use it (controls, config)
- Compatibility (what works, what doesn't)
- Which game version you tested against
- A reminder that users need the mod loader

## What Next?

- [Troubleshooting](troubleshooting.md) — common issues and fixes
