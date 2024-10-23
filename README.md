# Deepwoken Build Comparer
CLI Application that allows you to compare your character in-game to @cyfiee's [Deepwoken Builder](https://deepwoken.co/builder) build link/ID that you're following.

Useful for streamlining your progression, so you don't have to constantly check your notes and manually compare the talents in your character and build.

Report bugs to the [issues section](https://github.com/brycentjw/deepwoken-build-comparer/issues) or direct message me via discord @brycentjw (you can find me in the deepwoken discord, or deepwoken builder discord)

# Download

To install this, head over to the [Releases](https://github.com/brycentjw/deepwoken-build-comparer/releases) section and download the rar file at the very top, once downloaded, extract the files into a folder on your desktop and run main.exe.

# Frequently Asked Questions
## **Q:** How do I import character data? | What's character data?

**A:** Deepwoken added a new feature that allows you to copy your character's data, which includes things like your character's name, current power, race, origin (bugged), oath (bugged), attributes, mantras, and talents.

You can find this when pressing tab in-game to open your inventory, and on the right where it displays your attributes, there should be a button that you can click to copy paste your character data. Keep in mind that this may take some time to load your character's talents if you've just joined the game.
![image](https://github.com/user-attachments/assets/f6c4dc48-0436-4d78-b89a-6107a2beae7b)
Click the highlighted area, then use CTRL+A and CTRL+C to copy the entire character data.
![image](https://github.com/user-attachments/assets/f1f193bd-2be3-4910-9fdc-7e2289a76b4c)
This exported character data can be inaccurate due to known issues, rejoin the game to ensure that it's as accurate as possible.

There are known issues with this feature, please refer to the Known Issues category to see a list.


## **Q:** How do I get a builder link/ID? | What's a builder link/ID?

**A:** This program uses @cyfiee's [Deepwoken Builder](https://deepwoken.co/builder) as reference for your build planning. You can try this out by going to the [Deepwoken Builder](https://deepwoken.co/builder) and creating your build there, and when exporting the build as link you are able to input that into the program.


## **Q:** Why is my program/terminal stuck?

**A:** If your terminal looks like this, press any of your arrow keys while in the terminal. This happens only if you focus the terminal window before it gets to the prompt, which shouldn't be a problem as long as you press the arrow keys to fix it.
![image](https://github.com/user-attachments/assets/548456ee-386f-4746-b8da-338ccab5d9fe)


## **Q:** I managed to import my character data and set my builder link/ID, and selected 'Print build and character data comparisons'. What do these things mean?
"Talents that the character has, and is also in the build": These are talents that are in the deepwoken builder link/ID and are also found in your currently imported character.
"Talents that are in the build, but the character doesn't have": These are talents that are in the deepwoken builder link/ID, but are not found in your currently imported character.
"Talents that the character has, but aren't in the build": These are extra talents that are not in the deepwoken builder link/ID, but are found in your currently imported character.
"Talents that are in the build and can be obtained, but the character doesn't have": These are missing talents that are in the deepwoken builder link/ID, and are currently obtainable for your currently imported character.

## **Q:** You should add ${feature}.

**A:** If you have a idea or a request for a feature you can submit such ideas/requests in [Github Issues](https://github.com/brycentjw/deepwoken-build-comparer/issues)


## **Q:** I’ve encountered a bug/issue on this software

**A:** If you have a bug or issue, check if it's already in the Known Issues section, if not then please explain your issue with screenshots (if possible) and/or a highly descriptive explanation in [Github Issues](https://github.com/brycentjw/deepwoken-build-comparer/issues) and I will try to get back to you ASAP.


# Known Issues

As of 23/10/2024, there is a bug with the character data export in regards to shrining, as using the Shrine Of Chance will not remove the talent when exporting data. This can be fixed by rejoining the game to refresh the character's talents.

As of 23/10/2024, there is no option to differentiate where certain talents are from, such as the backpack equipment giving you the 'Robber Baron' talent. This will still appear as a talent as if it's part of the character, so please keep this in mind when reviewing the compared character and build. There is a feature that allows you to explicitly ignore these talents manually, so make use of this.

As of 23/10/2024, there is a weird interaction with equipment talents being 'duplicated' when exporting character data. This should not affect this program, but nonetheless an issue with exporting data.

As of 23/10/2024, there are talents that will be noted as "can be obtained", however cannot be obtained due to some other requirement (i.e: Ardour Scream needing Mumur: Ardour, Warding Radiance needing Fire Forge mantra). This is something I may fix in the future, but for now please keep this in mind when using this program to check for obtainable talents.

# Remarks
If you like this program that I wrote, please share this amongst your friends or people you know! I spent a lot of time on this, so I would greatly appreciate it if it was used by more people. Whether or not you do, thank you for using my program.
