[app]
title = System Warning
package.name = syswarn
package.domain = org.prank

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav
source.include_patterns = sound.wav

version = 1.0
requirements = python3,kivy,pyjnius,android

orientation = portrait
fullscreen = 1
presplash.filename = 

android.permissions = VIBRATE,WAKE_LOCK
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = False
android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 1