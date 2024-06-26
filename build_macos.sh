#!/usr/bin/env bash

echo "Building test app..."

# Install deps
python3 -m pip install -r requirements.txt --break-system-packages
python3 -m pip install nuitka --break-system-packages

# Compile python
python3 -m nuitka main.py -o Test --standalone --onefile

# Make an app bundle
mkdir -p Test.app/Contents/MacOS
cp Test Test.app/Contents/MacOS
cp Info.plist Test.app/Contents

# Thanks https://stackoverflow.com/a/31883126/9376340

mkdir -p Test.app/Contents/Resources/AppIcon.iconset

# Normal screen icons
for SIZE in 16 32 64 128 256 512; do
    sips -z $SIZE $SIZE icon.png --out Test.app/Contents/Resources/AppIcon.iconset/icon_${SIZE}x${SIZE}.png || exit 1
done

# Retina display icons
for SIZE in 32 64 256 512; do
    sips -z $SIZE $SIZE icon.png --out Test.app/Contents/Resources/AppIcon.iconset/icon_$(expr $SIZE / 2)x$(expr $SIZE / 2)x2.png || exit 1
done

# Make a multi-resolution Icon
iconutil -c icns -o Test.app/Contents/Resources/AppIcon.icns Test.app/Contents/Resources/AppIcon.iconset || exit 1
rm -rf Test.app/Contents/Resources/AppIcon.iconset

# Sign the app bundle
codesign --force --deep --sign - Test.app || exit 1

# Clean up the repo
chmod +x ./clean_up.sh
./clean_up.sh
