# CoE 135 Project (CLEAN BRANCH)
Members: Espiritu, Raagas, Salgado

# 4-way Video & Audio Conferencing using Sockets (Python)
This project aims to make a maximum of 4-way video & audio conferencing using sockets on Python. This project tool is intended to be used within the same network (Wi-Fi/LAN) without the need for an ISP service. This tool can be used by workers/students inside a building or campus to talk face-to-face.

# Progress Report
The list below shows our progress made every week.

Week 0: Accessing the PC Camera using OpenCV library  
Week 1: Sending of camera stream data through Sockets. (1-sided video-only communication)  
Week 2: Implementation of Multi-threading and Syncronization to make a 1-1 video-only communication.  
Week 3: Integrating Audio Stream sending to make a 1-1 Video-Audio Communication (Unstable)  
Week 4: Stable One-to-one Video Communication with One-sided Audio Communication (Client hears the Host). Chatbox implemented.  
Week 5: One-to-one (maybe one-to-many, needs to be tested) Video-Audio-Chatroom Communication synced. [Working Client-Server](https://github.com/espiritukarl/CoE135Proj/tree/master/Week3)

## Things to Implement:  
- Proper disconnection handling for video only 
- Synchronized disconnection (audio&chatroom synchronized but video not yet)
- Test One-to-Many connection
- [NEW!] Send Video/Audio Data of a client to another client (for 3-4 ways system)
- [NEW!] Arrangement of threads and acceptance for each participant setting (e.g. choose 3-way or 4-way)

## Prerequisites
- Microsoft Windows 7/8.1/10 Pro/Education/Enterprise
- Python 3.6 (Specific)
- Camera for each participant (Installed with drivers)
- Microphone (or Line-in) and Speakers (Audio Out) for each participant
- Powershell/Command Prompt Terminal (Any Terminal for Windows will do)
- Installed all Python Libraries Required (e.g. PyAudio)