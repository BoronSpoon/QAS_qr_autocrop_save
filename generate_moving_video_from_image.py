import cv2
import numpy as np
import os

#frame_count = 600
frame_count = 10
rotations = [np.pi/180*np.random.choice(np.linspace(-2,2,101)) for i in range(frame_count)] # max 5 degree rotation per frame
rotations[0] = 0
rotations = np.add.accumulate(rotations)
rotations = np.maximum(-np.pi*np.ones(frame_count), rotations)
rotations = np.minimum(np.pi*np.ones(frame_count), rotations)
rotations = np.hstack([rotations, rotations[:-1][::-1]])

zooms = [np.random.choice(np.linspace(-0.01,0.01,101)) for i in range(frame_count)] # max 5 degree rotation per frame
zooms[0] = 1 # first frame has no zoom
zooms = np.add.accumulate(zooms)
zooms = np.maximum(0.5*np.ones(frame_count), zooms)
zooms = np.minimum(2*np.ones(frame_count), zooms)
zooms = np.hstack([zooms, zooms[:-1][::-1]])

shift_xs = [np.random.choice(np.linspace(-5,5,101)) for i in range(frame_count)] # max 5 pixels per frame
shift_xs[0] = 0
shift_xs = np.add.accumulate(shift_xs)
shift_xs = np.maximum(-200*np.ones(frame_count), shift_xs)
shift_xs = np.minimum(200*np.ones(frame_count), shift_xs)
shift_xs = np.hstack([shift_xs, shift_xs[:-1][::-1]])

shift_ys = [np.random.choice(np.linspace(-5,5,101)) for i in range(frame_count)] # max 5 pixels per frame
shift_xs[0] = 0
shift_ys = np.add.accumulate(shift_ys)
shift_ys = np.maximum(-200*np.ones(frame_count), shift_ys)
shift_ys = np.minimum(200*np.ones(frame_count), shift_ys)
shift_ys = np.hstack([shift_ys, shift_ys[:-1][::-1]])

cwd = os.path.dirname(__file__)
writer = cv2.VideoWriter(
    #os.path.join(cwd, "videos", "1.avi"),
    os.path.join(cwd, "videos", "2.avi"),
    cv2.VideoWriter_fourcc('M','J','P','G'), 60, (1920, 1080)
)

original_frame = cv2.imread(os.path.join(cwd, "images", "test_images", "1.png"))
for rotation, zoom, shift_x, shift_y in zip(rotations, zooms, shift_xs, shift_ys):
    M1 = np.array([[zoom,0,0], [0,zoom,0]]).astype(np.float32)
    M2 = np.array([[1,0,int(shift_x)], [0,1,int(shift_y)]]).astype(np.float32)
    M3 = cv2.getRotationMatrix2D((int(1920/2), int(1080/2)), rotation * 360/(2*np.pi), scale=1)
    frame = np.copy(original_frame)
    frame = cv2.warpAffine(frame, M1, [1920, 1080], borderValue=(217,169,145))
    frame = cv2.warpAffine(frame, M2, [1920, 1080], borderValue=(217,169,145))
    frame = cv2.warpAffine(frame, M3, [1920, 1080], borderValue=(217,169,145))
    cv2.imshow("frame", cv2.resize(frame, (int(frame.shape[1]/3), int(frame.shape[0]/3))))
    cv2.waitKey(1)
    writer.write(frame)
writer.release()

