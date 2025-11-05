# Soundfonts Directory

This directory stores `.sf2` soundfont files used for MIDI → audio rendering.

## Recommended Soundfonts

### GeneralUser GS (Recommended - Free)
- **Size:** ~30MB
- **Quality:** High-quality, general-purpose
- **Download:** https://www.schristiancollins.com/generaluser.php
- **File:** `GeneralUser_GS_v1.471.sf2`

### MuseScore General (Alternative - Free)
- **Size:** ~35MB  
- **Quality:** Good, modern sounds
- **Download:** https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/
- **File:** `MuseScore_General.sf3`

## Installation

1. Download a soundfont from the links above
2. Place the `.sf2` or `.sf3` file in this directory
3. The audio rendering scripts will auto-detect available soundfonts

## Quick Download (macOS/Linux)

```bash
# Download GeneralUser GS
cd soundfonts
curl -L -O https://schristiancollins.com/downloads/GeneralUser_GS_v1.471.zip
unzip GeneralUser_GS_v1.471.zip
mv "GeneralUser GS v1.471/GeneralUser GS v1.471.sf2" ./GeneralUser_GS.sf2
rm -rf "GeneralUser GS v1.471" GeneralUser_GS_v1.471.zip
```

## Note

Soundfont files (`.sf2`/`.sf3`) are **not** tracked in git due to their size. You must download them manually.

