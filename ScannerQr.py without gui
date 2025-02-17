from pyzbar.pyzbar import decode
from PIL import Image
import cv2

# Initialize camera
cap = cv2.VideoCapture(0)
cv2.namedWindow("QR Code Detection")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Decode QR codes
    decoded_objects = decode(gray)
    
    for obj in decoded_objects:
        print(f"Type: {obj.type}")
        print(f"Data: {obj.data.decode('utf-8')}")

        # Draw rectangle around detected QR code
        points = obj.polygon
        if len(points) == 4:
            for i in range(4):
                cv2.line(frame, tuple(points[i]), tuple(points[(i + 1) % 4]), (0, 255, 0), 3)

    # Display the frame
    cv2.imshow("QR Code Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
