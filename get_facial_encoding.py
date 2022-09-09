import face_recognition

image_location = input("Enter image path: ")
image = face_recognition.load_image_file(image_location)
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)[0]
print(f'Known list: {[face_encodings]}')
print(type(face_encodings))
print(f'Unknown list: {face_encodings}')
match = face_recognition.compare_faces([face_encodings], face_encodings)
