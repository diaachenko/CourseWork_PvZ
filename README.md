# CourseWork_PvZ
**Coursework of Computer Science LPNU Second Year Student Nazar Diachenko. Topic: "Develompent of Tower Defense game".**

_This product was not made with an intent of copying or profitting, but to study OOP and test my skills. Original idea belongs to PopCap Games._
Sprites were downloaded from The Sprites Resource: [https://www.spriters-resource.com/pc_computer/plantsvszombies/](url)
Music and SFX materials were downloaded from Khinsider: [https://downloads.khinsider.com/game-soundtracks/album/plants-vs.-zombies-2009-gamerip-pc-ios-x360-ps3-ds-android-mobile-psvita-xbox-one-ps4-switch](url)

**How to run this:**
1. Download the contents of _progfiles_ folder onto your device. Make sure you don't lose the _.dll_ file -- this is where project's engine lies;
2. Run the _main.py_ file;
3. You're ready to go!

**How to make changes to the engine:**
1. Paste contents of _TowerEngine_ folder into C++ IDE;
2. Do whatever changes you want;
3. Don't forget to modify _bridge.cpp_ file, if necessary. Also, when you change _bridge.cpp_, you need to adjust _cpp_bridge.py_ to fit with those changes;
4. Build project with Release x64 config;
5. Find the _.ddl_ file (most likely will be in _projectfolder\x64\Release\projectname.dll_);
6. Copy it and paste it to the folder with _.py_ files;
