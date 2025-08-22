import cv2

def convert_to_vertical(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    target_width = int(height * 9 / 16)
    x_offset = (width - target_width) // 2

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (target_width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cropped = frame[:, x_offset:x_offset + target_width]
        out.write(cropped)

    cap.release
