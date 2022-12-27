## Set up `thcrap` and `vsync` patch for Touhou games bought on Steam

Based on tutorials from 
- https://www.reddit.com/r/touhou/comments/yypp3q/how_to_use_thcrap_touhou_community_reliant/
- https://steamcommunity.com/sharedfiles/filedetails/?id=2196860604
- https://github.com/tactikauan/thcrap-steam-proton-wrapper

I will use [TH10 Mountain of Faith](https://store.steampowered.com/app/1100140/Touhou_Fuujinroku__Mountain_of_Faith/) as an example in the followiing steps.
I tested on my Steam Deck but it should also works on all Linux distrobution.

## Apply `thcrap`

1. Download the [TH10](https://store.steampowered.com/app/1100140/Touhou_Fuujinroku__Mountain_of_Faith/).
   Switch to desktop mode if you are using Steam Deck.
   
1. Download `thcrap` from [here](https://www.thpatch.net/wiki/Touhou_Patch_Center:Download), and extract to a directory.
   I put `thcrap` and all other patches/scripts under `~/Touhou` directory, so it would be `/home/deck/Touhou/thcrap/`.

1. Locate your Steam game directory. For Steam Deck, it's under `/home/deck/.local/share/Steam/steamapps/common/` if you installed the game on internal SSD,
   or `/run/media/mmcblk0p1/steamapps/common/` if installed on micro SD card.
   For general Linux distributiions, if Steam is install as a system package, game directory is `/home/$USERNAME/.local/share/Steam/steamapps/common/`.
   If you installed Flatpak version of Steam, it's `/home/$USERNAME/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/`.
   For each Touhou game you would find the `.exe` file under its directory.
   In my case, TH10 on Steam Deck internal SSD, it's `/home/deck/.local/share/Steam/steamapps/common/th10/th10.exe`.
   
1. Go to the `thcrap` folder and crate a `config` folder. Inside of the `config` folder cate a `games.js` file with content
   ```
   {
     "th10": "Z:/home/deck/.local/share/Steam/steamapps/common/th10/th10.exe",
     "th10_custum": "Z:/home/deck/.local/share/Steam/steamapps/common/th10/custom.exe"
   }
   ```
   replace the path with the one in previous step. The `Z:` is how `wine` locate files on Linux.
   
1. Add the `thcrap.exe` to your Steam library. On Steam Deck you can right click `thcrap.exe` --> `Add to Steam`.
   Or you can open Steam, go to your library, and at bottom left click `ADD A GAME` manually add `thcrap.exe` to Steam.
   If you are using Flatpak version of Steam, you may need to add the permission to allow steam access `~/Touhou` directory using Flatseal.
   
1. Run `thcrap.exe` from Steam, if it doesn't run, go to the game setting (click setting bottom --> Properties --> Compatibility) check _Force the use of specific Steam Play compatibility tool_, and select specific proton version.
   The `proton 7.0-5` works for me.
   
1. During he installation you choose your language patch. I use default english pack in this example.
   Then it will ask you game location, since we already added the game in `games.js`, just click next.
   Next, it asks for shortcuts. We don't create any shortcuts here, since we will add the patch to Steam launch command.
   
1. Download `thcrap_proton` wrapper script from [here](https://raw.githubusercontent.com/tactikauan/thcrap-steam-proton-wrapper/master/thcrap_proton).
   You can find its explanation at the [github repo](https://github.com/tactikauan/thcrap-steam-proton-wrapper).
   I put the script here `/home/deck/Touhou/thcrap-steam-proton-wrapper/thcrap_proton`.
   
1. Edit the `thcrap_proton` script with your favouriate text editor, change these two variables
   ```
   THCRAP_FOLDER="/home/deck/Touhou/thcrap"
   THCRAP_CONFIG=en.js
   
   ...
   ```
   `THCRAP_FOLDER` is where your thcrap folder. `THCRAP_CONFIG` is the config file generated. You could find it under the "/home/deck/Touhou/thcrap/config" directory.

1. Make `thcrap_proton` executable. You can either right click the script --> Properties --> Permissions check _IS executable_,
   or using command line in terminal `chmod u+x /home/deck/Touhou/thcrap-steam-proton-wrapper/thcrap_proton`.

1. Change your Touhou game launch options. Go to your Steam library --> click your game --> settings icon --> properties.
   Edit _LAUNCH OPTIONS_ under _GENERAL_ settings to
   ```
   /home/deck/Touhou/thcrap-steam-proton-wrapper/thcrap_proton -e "%command%"
   ```
   Change _/home/deck/Touhou/thcrap-steam-proton-wrapper/thcrap_proton_ according to your `thcrap_proton` script location.

1. Now when you launch the game through Steam it will launch `thcrap`, then `thcrap` will update the patch and launch the game.
   It's recommended you uncheck the _Keep the updater running in background_ in `thcrap` setting, so Steam could properly shutdown the game when you quit.

## Apply `vpatch`