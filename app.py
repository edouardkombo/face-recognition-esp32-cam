import face_recognition
from flask import Flask,jsonify,request,render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

@app.route('/')
def default():
    return render_template('index.html')

@app.route('/feed')
def video_feed():
    return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def stream():
    # Load a sample picture and learn how to recognize it.
    mj_image = face_recognition.load_image_file("./known/mj.jpg")
    mj_face_encoding = face_recognition.face_encodings(mj_image)[0]

    # Load a second sample picture and learn how to recognize it.
    janet_image = face_recognition.load_image_file("./known/janet-jackson.jpg")
    janet_face_encoding = face_recognition.face_encodings(janet_image)[0]

    # Load a third sample picture and learn how to recognize it.
    carly_image = face_recognition.load_image_file("./known/carly-rae.jpg")
    carly_face_encoding = face_recognition.face_encodings(carly_image)[0]

    # Load a fourth sample picture and learn how to recognize it.
    filippo_image = face_recognition.load_image_file("./known/filippo.jpeg")
    filippo_face_encoding = face_recognition.face_encodings(filippo_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        mj_face_encoding,
        janet_face_encoding,
        carly_face_encoding,
        filippo_face_encoding
    ]
    known_face_names = [
        "Michael Jackson",
        "Janet Jackson",
        "Carly Rae Jepsen",
        "Filippo"
    ]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        try:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            
            if (frame==None):
                continue

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame


            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)
            cv2.imwrite('vid.jpg', frame)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + open('vid.jpg', 'rb').read() + b'\r\n')

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(str(e))

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=4000)
