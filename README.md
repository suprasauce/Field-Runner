# Field Runner [(Download)](https://sauce-fl.itch.io/field-runner)

![](https://github.com/suprasauce/field_runner/blob/main/gif.gif)

## Description

Field Runner is a 2-d game made using pygame. You are postman and your duty is to transfer a package from one letter box situated at the starting of the map to the other letter box situated at the end of the map.

While you are delivering the package, you will face enemies who will try to shoot you and it is your duty to protect the package and yourself from the bullets of the enemies.

The package cannot move out on its own, you have to drag it and the package can  also stick to the player by using stick power. You are also provided with a shockwave power.

## Installation

### Windows
1. Clone the project on your local machine in your prefered directory by typing the following command in git bash/ Powershell/ CMD (or download the file yourself)

```
git clone https://github.com/suprasauce/Field-Runner.git
```

2. Install [python](https://www.python.org/) for windows if you don't have it (preferably python 3.8+). Activate a virtual environment in Powershell/ CMD by either installing virtualenv and following its instructions to make a virtual environment, or by using the venv package which comes with python by default

```
python -m venv env
```
This will make a folder named env.
Then type 

(Powershell)
```
path_where_env_is_stored\env\Scripts\Activate.ps1
```
(CMD)
```
path_where_env_is_stored\env\Scripts\activate
```

3. Go to the project directory <br />
To install pygame, run
```
pip install pygame
```

4. Run the game.py file by typing the following command in CMD/ Powershell (make sure virtual env is activated) in the directory where you cloned the folder

```
python main.py
```




