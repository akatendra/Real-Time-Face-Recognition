import threading

from classes import *


def face_recognition(frm):
    global resize
    global buffering_flag
    global frame_count
    global known_face_encodings
    global known_face_names
    global face_locations
    global face_names
    if resize != 1:
        stored_frame = frm
        frame = cv.resize(frm, (0, 0), fx=1 / resize,
                          fy=1 / resize)
        # Convert the image from BGR color (which OpenCV uses) to RGB color
        # (which face_recognition uses)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    else:
        stored_frame = frm
        frame = frm

    if not buffering_flag:
        print('frame_count:', frame_count)
    if frame_count == 1:

        # Find all the faces and face encodings in the screenshot
        time_fr = time()
        face_locations = fr.face_locations(frame)
        if not buffering_flag:
            print('face_location time:', time() - time_fr)
        time_fr = time()
        face_encodings = fr.face_encodings(frame, face_locations)
        if not buffering_flag:
            print('face_encodings time:', time() - time_fr)
        # Loop through each face in this frame of video
        face_names = []
        if not buffering_flag:
            print('count_face_encodings:', len(face_encodings))
        for face_encoding in face_encodings:
            # See if the face is a match for the known faces
            matches = fr.compare_faces(known_face_encodings, face_encoding)

            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = fr.face_distance(known_face_encodings,
                                              face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since
        # the frame we detected in was scaled
        if resize != 1:
            top *= resize
            right *= resize
            bottom *= resize
            left *= resize
        # Draw a box around the face
        name_len = len(name)
        frame_width = right - left
        name_plate_width = name_len * 10  # 10 is width of one letter approximately.
        if frame_width < name_plate_width:
            d_left = int((name_plate_width - frame_width) / 2)
        else:
            d_left = 1
        stored_frame = cv.rectangle(stored_frame, (left, top), (right, bottom),
                             (255, 0, 255),
                             2)

        # Draw a label with a name below the face
        cv.rectangle(stored_frame, (left - d_left, bottom),
                     (right + d_left, bottom + 35),
                     (255, 0, 255), cv.FILLED)
        cv.putText(stored_frame, name, (left - d_left + 5, bottom + 20),
                   cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

    return stored_frame


##################### PATHES #####################

path = 'class_trofim'

##################### Read recognition data #####################
start_time = time()
known_face_names = np.load(
    f'{path}/names.npy')  # LIST CONTAINING ALL THE CORRESPONDING CLASS Names
known_face_encodings = np.load(
    f'{path}/face_encodings.npy')  # LIST CONTAINING ALL THE CORRESPONDING KNOWN FACE
print('Recognition data received', time() - start_time, 'sec')

########## Settings ##########
resize = 2  # Must be integer more than "0". Shows how many times the image should be reduced
frame_rate = 100  # Which screenshot will be processed by facial recognition
frame_count = 1
buffer_size = 1000000  # How many screenshots will be written to the buffer before it starts displaying
stack_size = 0
########## Settings ##########

##################### Initialize #####################


buffering_flag = True  # If True buffering is going on. False - Buffering is stoped
face_locations = np.ndarray
face_names = []
##################### Initialize #####################

# initialize the Video Stream
video_getter = VideoGet('Video conference at ZOOM.mp4').start()
video_shower = VideoShow(video_getter.screenshot)
cps = CountsPerSec().start()
stack = VideoQueue(video_getter.screenshot).start_add()

begin_time = time()

while True:
    if video_getter.stopped or video_shower.stopped or stack.stopped:
        video_shower.stop()
        video_getter.stop()
        stack.stop()
        cv.destroyAllWindows()
        print('Video stream canceled!')
        break
    # Get an updated screenshot
    screenshot = video_getter.screenshot

    screenshot = face_recognition(screenshot)

    # Put screenshots into Queue
    stack.screenshot = screenshot
    stack_size = stack.size()
    print('stack_size:', stack_size)

    # Display the results

    #  Buffering
    if stack_size >= buffer_size and buffering_flag is True:
        stack.start_pop()
        video_shower.start()
        buffering_flag = False
    else:
        print(f'Buffering... ({stack_size})')
        # print('\r', end='')


    # Display the resulting image

    video_shower.screenshot = stack.screenshot_out

    cps_ = cps.counts_per_sec()
    print(f'CPS: {cps_}')
    cps.increment()
    # debug the loop rate
    loop_time = time() - begin_time
    if loop_time == 0:
        fps_ = 0
    else:
        fps_ = 1 / loop_time
    print(f'FPS: {fps_}')
    begin_time = time()



    if frame_count == frame_rate:
        frame_count = 1
    else:
        frame_count += 1

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        video_getter.stop()
        video_shower.stop()
        stack.stop()
        cv.destroyAllWindows()
        break

    print(f'There are : {threading.active_count()} threads')
    for thread in threading.enumerate():
        print(f'Thread name: {thread.getName()}')
    print(f'Now active thread: {threading.current_thread()}')

print('Done.')
