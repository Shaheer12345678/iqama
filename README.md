# Iqama

Prayer times, reminders, and a weekly prayer log for the system tray. Iqama
sits quietly in your Windows tray, fetches the day's prayer times for your
city, reminds you before each one, and tracks a simple weekly prayer log.

## How to Install

**No technical knowledge needed. No Python, no terminal, nothing to type.**

1. Go to the [Releases page](https://github.com/Shaheer12345678/iqama/releases)
   on GitHub.
2. Under the newest release, click **Iqama.exe** to download it. (Your
   browser may show a small warning that the file type is unfamiliar --
   that's normal for a `.exe` download; click **Keep** if asked.)
3. Once it's downloaded, double-click **Iqama.exe** to run it.
   - Windows may show a blue "Windows protected your PC" screen the first
     time, because the app isn't signed with a paid certificate. Click
     **More info**, then **Run anyway**. This is a one-time step.
4. That's it -- Iqama is now running. Look for its crescent-moon icon in
   the system tray (the small icons near your clock, bottom-right of the
   screen; you may need to click the little "^" arrow to see it).
5. Right-click the tray icon to open **Settings** and set your city. Your
   prayer times will load automatically after that.

If you'd like Iqama to start automatically every time you turn on your
computer, right-click the tray icon and check **Start with Windows**.

To close the app completely, right-click the tray icon and choose **Quit**.

## Features

- Runs quietly in the system tray; hover the icon to see time remaining
  until the next prayer
- Daily prayer times for your city via the [Aladhan API](https://aladhan.com/prayer-times-api),
  cached locally so it still works offline after the first fetch of the day
- Desktop notifications before each prayer (lead time configurable) and at
  the Adhan time itself
- A weekly log to track which prayers you've prayed, with a completion chart
- Optional auto-start with Windows

## For Developers

### Setup

```bash
git clone https://github.com/Shaheer12345678/iqama.git
cd iqama
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
```

### Run from source

```bash
python -m iqama.main
```

### Run the tests

```bash
pytest
```

### Project layout

```
src/iqama/
  config.py           # constants, defaults, app-data-dir/resource helpers
  main.py              # entry point
  data/                # SQLite schema + repositories, Aladhan API client
  services/            # settings, prayer-time service, notifications, Windows startup
  ui/                  # tray shell, settings window, weekly log, about dialog
tests/                 # unit tests for the data and service layers
resources/             # tray/app icon (icon.ico, icon.png)
scripts/generate_icon.py  # regenerates the placeholder icon (needs Pillow)
packaging/             # PyInstaller entry point + .spec
```

### Building the .exe

Requires the `dev` extras (`pip install -e ".[dev]"`, which includes
PyInstaller). From the project root:

```bash
pyinstaller packaging/iqama.spec --distpath dist --workpath build
```

The standalone executable is written to `dist/Iqama.exe`. It bundles its
own Python runtime and all dependencies -- nothing else needs to be
installed on the machine that runs it.

To swap in real artwork instead of the placeholder icon, replace
`resources/icon.ico` and `resources/icon.png` with your own (same file
names, any reasonable size -- `icon.ico` should ideally contain multiple
resolutions). Nothing else in the app or build needs to change.

## License

MIT -- see [LICENSE](LICENSE).
