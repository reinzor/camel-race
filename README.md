# Camel race

User interface animation   |  Client play illustration
:-------------------------:|:-------------------------:
![](img/ui_animation.gif)  |  ![](img/illustration.gif)


# The system

## 1 x Raspberry Pi 3 (Server)
- Websocket server that relays all incoming events to all other clients (python) 
- Websocket client for gpio push-buttons interaction (python)
- Web browser with websocket client (js) that shows the web interface 
- Wooden casing

## n x Raspberry Pi zero W (Clients)

![](img/ee.jpg)

Holes 1             |  Holes2
:------------------:|:---------------------:
![](img/holes.jpg)  |  ![](img/holes2.jpeg)

- Websocket client for the gpio break beam sensors (python)
- Wooden casing
- 5 x IR break beam sensor

# Installation

## Server

TODO

## Client

TODO
