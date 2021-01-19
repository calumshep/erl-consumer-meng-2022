# MEng Group Project - European Robotic League
## Initial Installation
Install [Docker](https://www.docker.com/)
Verify Docker installation by running
```
docker info
```
Clone this repository
```
git clone https://github.com/chulme/european_robotic_league.git
cd european_robot_league
```
Download all of the images necessary for running the simulator, [curtosy of hsr-project](https://github.com/hsr-project/tmc_wrs_docker).
```
./pull-images.sh
```
Start the simulator
```
docker-compose up
```
Install the additional project-specific software eg. Jason, by opening the [IDE](http://localhost:3000/) and accessing the terminal.
```
sudo bash pull-new-software.bash
```

# Development
- The simulator's screen http://localhost:3000
- IDE http://localhost:3001

# Installation of Additional Software
To use additional software, we must first add automated instructions to pull-new-software.sh so that everyone can easily update their image. I have created the `additional_software` folder so that we can have a singular installation folder for this.