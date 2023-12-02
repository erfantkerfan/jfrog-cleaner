## Jfrog artifactory cleaner

### This project helps you to clean up your artifactory

You can read through sample config file and make it however you like but simply give it a repo and folder and tell it how long you want its content to be kept and also exclude some patterns (Regex).

#### How to run:

I made sure you wont be needing any extra packages in latest ubuntu server release so you can simply clone, create a new config file and run it like this:

`python3 main.py --help`

You can find out different flags yourself.

#### ToDo:

- Adding Dockefile

- Adding the ability to read password from ENV for better security

#### Notes:

- *Open for contribution*

- *The time I spent on this project was sponsored by my employer at the time: [Azki](https://www.azki.com)*
