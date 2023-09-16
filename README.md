
* Patreon: https://www.patreon.com/sd_hassan

# TikTok Face Extractor

This is a Python script that allows you to extract faces from TikTok videos.

## Features

-   Downloads a TikTok video from a given URL or downloads a profile upp to 28 videos
-   Allows the ability to "subscribe" to a tiktok profile, it will download the latest video then will perform auto checks every 10 mins for new videos and download any new videos that are posted until the bot is stopped
-   Extracts faces from the downloaded video
-   Saves the extracted faces to disk

## Installation

1.  Clone this repository or download the ZIP file and extract the contents.
2.  Install the required dependencies by running `pip install -r requirements.txt` in the root directory of the project.

## Usage

1.  Open a terminal or command prompt and navigate to the root directory of the project.
2.  Run the command `python hassan-tiktok.py` to launch the script.
3.  Select either a profile or URL download option then enter the URL or the username of the TikTok video/account you want to extract faces from.
4.  The script will download the video and extract the faces. The extracted faces will be saved in the `faces` directory.


If you get a build error when installing requirements, you may need the Visual Studio Build tools c++ workload

Download build tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

Then in the same folder where your EXE is, run this command:

`.\vs_BuildTools.exe --quiet --wait --norestart --nocache --installPath C:\BuildTools --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.Windows10SDK.19041`

or

`vs_BuildTools.exe --quiet --wait --norestart --nocache --installPath C:\BuildTools --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.Windows10SDK.19041`

Leave it running and you can see in your C:\BuildTools that new folders are being added. When it's finished, restart the PC and your package should install correctly 
## Video



https://user-images.githubusercontent.com/119671806/236033777-a93326aa-8f1c-4844-bd50-d69463f0443b.mp4

