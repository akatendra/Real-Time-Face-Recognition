# Real Time Face Recognition #
Real time face recognition for marking ZOOM conference attendee.
***
### The project is built on libraries: ###
Face recognition

[https://github.com/ageitgey/face_recognition](https://github.com/ageitgey/face_recognition)

Opencv-python

[https://github.com/opencv/opencv-python](https://github.com/opencv/opencv-python)
***
Folders:

1. class_trofim
>Folder with reference images of class members. The folder also contains files: 
>>1. With information about recognizing faces of class participants **face_encodings.npy**
>>2. File with the names of class participants (names are taken from the names of the reference images) **names.npy**
>>3. xlsx-file in which the presence of ZOOM conference is noted **attendance.xlsx**
2. video
>In this folder, place a video of the ZOOM conference where you want to mark the attendees. Read README.txt in this folder where to rich test video-file.


***

Files:
1. main_fast9.py
>The program make screenshots from window with ZOOM conference. Program search faces on screenshot, recognize faces and put frames around faces and plates with names of person. Information about the presence of the class participant is recorded in future in the file **attendance.xlsx**.

2. classes.py
>The file contains the classes necessary for the operation of the programs

3. setup_class.py
>A program that processes reference images of ZOOM class participants for subsequent recognition of those present at the ZOOM conference. The program generates three files:
>>- face_encodings.npy
>>>The result of reference pictures processing. Contains information about faces. 128 points per face.
>>- names.npy
>>>Names are taken from the names of the reference picture files for attendance
>>- attendance.xlsx
>>>File template for attendance marking
>These three files are placed in the **class_got** folder.

4. xlsx.py
>Contains the necessary functions for working with xlsx files. The openpyxl library is used
