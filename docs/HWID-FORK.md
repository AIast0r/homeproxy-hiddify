# HWID subscription support (fork patch)

This branch adds opt-in identity headers to Re:HomeProxy's subscription downloader.
It leaves the stock routing / rules / sing-box core selection code unchanged.

## LuCI configuration

Go to **Services → Re:HomeProxy → Node Settings → Subscriptions**:

- Enable **Send HWID**.
- Optionally provide an existing **Subscription HWID** (use this when the provider limits device slots).
- Set **User-Agent** to a supported application value if required by the provider.
- Optionally set device OS, OS version and model. Empty OS defaults to OpenWrt.
- Save and update subscriptions.

When enabled without an explicit HWID, the downloader generates a random
32-character hexadecimal ID and saves it in `/etc/config/homeproxy`.
The ID persists across subscription updates and reboots, but changes if the
configuration is erased. Keep a backup if the provider tracks device slots.

## Security limitations

- Identity headers are sent only to HTTPS subscription URLs.
- Redirects are deliberately not followed in HWID mode to avoid transmitting
  the device identifier to an unrelated host. Providers which require a
  redirect must supply a final canonical URL.
- curl is a package dependency. This change does **not** modify sing-box.
- Existing subscriptions continue to use the original fetcher with HWID off.
- Support is global across subscriptions, not per subscription URL.
- Runtime compatibility with a specific provider must be verified on device.

## Updating from upstream manually

```sh
git remote add upstream https://github.com/1andrevich/homeproxy-hiddify.git
git fetch upstream
git checkout master
git merge upstream/master
git cherry-pick <HWID-commit(s)> # only if not already merged
```

Prefer merging the HWID PR into master once verified; then ordinary upstream
merges preserve the patches and Git will report conflicts when code overlaps.

## Checks

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The GitHub workflow builds APK and IPK artifacts for PRs to master once
GitHub Actions is enabled on the fork. Until actual OpenWrt runtime tests,
treat the branch as a testing candidate, not a production release.
