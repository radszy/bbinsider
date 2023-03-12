# Running BB Insider

### Prerequisties
* Latest Python
* Python libraries: requests, tabulate and Pillow

### Windows
* Install Python and required libraries
  - Goto https://www.python.org/downloads/ and get download the latest version.
  - In the installation wizard check option to add python.exe to your PATH.
  - Open Command Prompt (cmd.exe) and execute following command:
    - `python.exe -m pip install requests tabulate Pillow`
* Run the script (still in the Command Prompt)
  - `cd C:\Users\radszy\bbinsider`
  - `chcp 65001`
  - `python.exe main.py --print-stats --print-events --matchid 123786926`

### Linux
* Install Python and required libraries
  - `sudo apt update`
  - `sudo apt install software-properties-common -y`
  - `sudo add-apt-repository ppa:deadsnakes/ppa`
  - `sudo apt install Python3.10`
  - `python3.10 -m pip install requests tabulate Pillow`
* Run the script
  - `cd ~/Downloads/bbinsider`
  - `python3.10 ./main.py --print-stats --print-events --matchid 123786926`

### Mac
* Install Python and required libraries
  - `brew install python`
  - `python -m pip install requests tabulate Pillow`
* Run the script
  - `cd ~/Downloads/bbinsider`
  - `python ./main.py --print-stats --print-events --matchid 123786926`
