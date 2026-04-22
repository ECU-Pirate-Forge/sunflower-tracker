
# Sunflower Tracker

The Sunflower Tracker is a software system designed to address problems concerning solar panels, more specifically the problems that arise when a solar panel is placed at a fixed position which can lead to inefficient sunlight absorption. The name of the project is in reference to sunflowers, which are capable of following the sun's trajectory from east to west each day to maximize the amount of sunlight they are being exposed to. Through the use of a 2D Webots simulation, this software hopes to provide an accurate representation of how potential real hardware could behave to allow solar panels the ability to maximize sunlight exposure, just like a sunflower, and maximize power generation.

The target audience and primary users of this software would include:
- Students, researchers, and others who are looking for a hands-on simulation that can demonstrate sun-tracking behavior, which can be used for different projects.
- Homeowners that rely on solar power for their daily lives, as this can allow them to maximize their power output if what is demonstrated in the software can be applied to hardware.

## Features
The following features are present within the Sunflower Tracker:
- ***Auto Sun Tracking***, which is a feature that can be considered the main purpose of the software. It would allow the system to automatcially position the tracking device in the direction of the strongest source of sunlight based on data like a sun positioning model, tracking sensors, or both if necessary. This feature is divided into three different modes
    - ***Open-Loop*** mode allows the device to move in a fixed pattern without being fully dependent on the sun.
    - ***Closed-Loop*** mode allows the device to strictly follow the sun's path throughout the day, beoming motionless once the sun sets in its entirety.
    - ***Hybrid*** mode allows for a com
- ***User Input***, in which the software's user will be able to provide information such as the date and time and location to receive results that would be an accurate representation of what maximizing sunlight would look like in their general area.
- ***User Interface***, a screen that will display the current status of the device, including the direction it currently faces and what mode it is currently in.
- ***Manual Control***, which is a feature that can allow the user to manually set the direction of the tracker or temporarily pause the ability to track at their leisure, allowing for better control over the system from the user's end.
    - ***Location Specification*** is another feature similar to this, as the user is able to manually set their general timezone/location, as well as their latitude and longitude of their location, allowing the simulation to provide adequate movement of the sun according to their general location.
- ***Logging***, where the system will come with the ability to store records of information such as the device's angle, light intensity, and any potential errors that can occur during the tracking process. These records would also have timestamps that allow the users and developers to know exactly when something occurred, whether it was a good or bad occurrence.

---

# Getting Started
The following section will deal with instructions for getting set up with the project on your own computer.

## Installing Webots
<img align="right" width="464" height="198" alt="image" src="https://github.com/user-attachments/assets/be4e0969-f3f5-44ed-ba56-9baf26e4a113" />
The first step should be to ensure that Webots is installed and capable of running on your system. This project will be using Webots to utilize a simulated model as representation of how the sunflower tracker should behave in real life. To install Webots onto your own system:
- Go to the following website and download the Webots installer: https://cyberbotics.com/#download
- Follow the installation instructions. If you are unsure about the settings, go with the default/recommended settings for installation as prompted by the installer.

Once the installation is complete, Webots should be openable on your computer. Simply locate the application and open it to begin. Other important things to note include:
- The application will prompt you to take a guided tour upon opening after the initial installation. If new to Webots, the guided tour is recommended. If you do not wish to do the guided tour at first and want to explore Webots on your own, that is fine. You can find the guided tour again by going to the navigation bar and clicking [Help -> Webots Guided Tour]

## Opening the Sunflower Tracker Project
The next step will be to open the world file that is associated with this project's repository. The following steps will need to be taken in order to access this world on your system: <img align="right" width="442" height="333" alt="image" src="https://github.com/user-attachments/assets/aaae65dc-10a5-4155-8bf5-81cf25dfb190" />

- Clone the Github repository onto your system. There are a few ways that this can be done. First, you must navigate to the main page for the repository above and click the green "Code" button to bring down a dropdown list of ways to clone your repository.
    - HTTPS allows you to clone the repository using the URL provided. This typically works well with certain integrated development environments (IDEs).
    - SSH will allow you to use a protected key to download the repository. However, if no keys are available on your account, you must add one or choose another option.
    - GitHub CLI allows you to clone the repository by bringing up the Command Prompt (or Terminal depending on your system) to run a command using the git keyword. You must have Git installed on your system in order to use this method.
    - You also have the option to use the GitHub Desktop application to clone repositories. Once you have downloaded and logged into the application, navigate back to the "Code" button and click "Open with GitHub Desktop." Once prompted, open the application. You will be able to choose a download location and the application will handle cloning the repository for you.
    - You also have the option to choose "Download ZIP", which downloads the entire repository as a .zip file. In this situation, it is typically hard to update your contributions directly to the project as you have no connection being made between the repository and the location where you've cloned it on your system.

Once you have cloned the repository, navigate to the folder where you have stored it. Once in that folder go through the following filepath to reach the webots simulation: ```sunflower-tracker/webots/SunflowerSIM/worlds```. Open the file titled "Sunflower SIM.wbt". This will automatically launch Webots and open the world containing the current progress of the Sunflower Tracker simulation, similar to what is pictured below.
<img width="1919" height="999" alt="image" src="https://github.com/user-attachments/assets/83eafb3f-f058-4f25-a0d9-0fa728e85ab7" />

```bash
To Be Added
```

---

## Contributing
For basic information regarding contribution, see the [Contributors file](CONTRIBUTING.md).
For information regarding how the development team is meant to properly contribute and review code, see the [Code Review file](CODE_REVIEW_README.md).

## License
This project is licensed under the [MIT License](LICENSE).
