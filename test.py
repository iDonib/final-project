import face_recognition
import ast

a = input("Enter: ")
b = input("Enter: ")

a = ast.literal_eval(a)
b = ast.literal_eval(b)

match = face_recognition.compare_faces([a], b)
print(match)
