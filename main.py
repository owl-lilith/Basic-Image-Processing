from tkinter import *
from tkinter import filedialog # Used to open a file dialog for selecting images from the file system.
import cv2 as cv
import numpy as np
from PIL import Image, ImageTk #  Used to convert OpenCV images to a format that can be displayed in Tkinter (since OpenCV and Tkinter handle images differently).

# Initialize global variables
src = None
dst = None

# Create the main window
window = Tk()
window.title('Image Processing (Basic Operations)')

# Define the function to perform thresholding
def image_processing(val):
    global dst
    if src is not None:
        dst = src
        # Fetches the current value from the slider
        threshold_type = threshold_operation_type_var.get()
        threshold_value = threshold_operation_value_var.get()
        # threshold
        _, dst = cv.threshold(dst, threshold_value, 255, threshold_type)
        
        # morphology
        morphological_type = morphological_operation_type_var.get()
        morphological_kernel = morphological_operation_kernel_var.get()
        morphological_kernel_size = (morphological_kernel, morphological_kernel)
        morphological_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, morphological_kernel_size)
        gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
        gray = cv.bitwise_not(gray)
        bitwise_image = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 15, -2)
        horizontal = np.copy(bitwise_image)
        vertical = np.copy(bitwise_image)
        rows, columns = gray.shape
        horizontal_size = columns // 30
        vertical_size = rows // 30
        if morphological_type == 0:
            dst = cv.dilate(dst, morphological_kernel, iterations=1)
        elif morphological_type == 1:
            dst = cv.erode(dst, morphological_kernel, iterations=1)
        elif morphological_type == 2:
            dst = cv.morphologyEx(dst, cv.MORPH_OPEN, morphological_kernel)
        elif morphological_type == 3:
            dst = cv.morphologyEx(dst, cv.MORPH_CLOSE, morphological_kernel)
        elif morphological_type == 4:
            dst = cv.morphologyEx(dst, cv.MORPH_GRADIENT, morphological_kernel)
        elif morphological_type == 5:
            dst = cv.morphologyEx(dst, cv.MORPH_TOPHAT, morphological_kernel)
        elif morphological_type == 6:
            dst = cv.morphologyEx(dst, cv.MORPH_BLACKHAT, morphological_kernel)
        elif morphological_type == 7:
            horizontalStructure = cv.getStructuringElement(cv.MORPH_RECT, (horizontal_size, 1))
            horizontal = cv.erode(horizontal, horizontalStructure)
            dst = cv.dilate(horizontal, horizontalStructure)
        else:
            verticalStructure = cv.getStructuringElement(cv.MORPH_RECT, (1, vertical_size))
            vertical = cv.erode(vertical, verticalStructure)
            dst = cv.dilate(vertical, verticalStructure)
        
        # blur
        blurring_type = blurring_filters_type_var.get()
        blurring_kernel = blurring_filters_kernel_var.get() * 2 + 1
        blurring_kernel_size = (blurring_kernel, blurring_kernel)
        if blurring_type == 0:
            dst = cv.blur(dst, blurring_kernel_size)
        elif blurring_type == 1:
            dst = cv.GaussianBlur(dst, blurring_kernel_size, 0)
        elif blurring_type == 2:
            dst = cv.medianBlur(dst, blurring_kernel)
        else:
            dst = cv.bilateralFilter(dst, blurring_kernel, blurring_kernel * 2, blurring_kernel / 2)
        
        show_image(dst)

def zoom_in():
    global dst
    global src
    if dst is not None:
        rows, columns, _ = dst.shape
        print(dst.shape)
        if dst.shape[1] < 512 and dst.shape[0] < 512:
            dst = cv.pyrUp(dst, dstsize=(columns * 2, rows * 2))
    show_image(dst)
    
def zoom_out():
    global dst
    if dst is not None:
        rows, columns, _ = dst.shape
        print(dst.shape)
        if dst.shape[1] > 256 and dst.shape[0] > 256:
            dst = cv.pyrDown(dst, dstsize=(columns // 2, rows // 2))
    show_image(dst)

# Load the image and convert it to grayscale
def load_image():
    global src
    global dst
    file_path = filedialog.askopenfilename()
    if file_path:
        src = cv.imread(file_path)
        if src is None:
            print('Could not open or find the image:', file_path)
            return
        src = cv.cvtColor(src, cv.COLOR_BGR2RGB)
        dst = src
        show_image(src)

def save_image():
    global dst
    if dst is not None:
        # Ask the user where to save the image
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg"),
                                                            ("All files", "*.*")])
        if save_path:
            # Save the image using OpenCV
            dst = cv.cvtColor(dst, cv.COLOR_BGR2RGB)
            cv.imwrite(save_path, dst)
            print(f"Image saved to {save_path}")
    else:
        print("No image to save")

# Display the processed image in Tkinter window
def show_image(img):
    # img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
    img = Image.fromarray(img) # Converts the NumPy array (OpenCV image) into a PIL.Image object.
    imgtk = ImageTk.PhotoImage(image=img) # Converts the PIL.Image object into a Tkinter-compatible image.
    panel.imgtk = imgtk
    panel.config(image=imgtk) # Updates the image shown on the Tkinter Label (panel).

# Create two frames: one for the image (left) and one for the controls (right)
image_frame = Frame(window)
control_frame = Frame(window)
control_frame0 = Frame(control_frame)
control_frame1 = Frame(control_frame)
control_frame2 = Frame(control_frame)
control_frame3 = Frame(control_frame)

# Pack the frames to the left and right sides
image_frame.pack(side=LEFT, padx=10, pady=10)
control_frame.pack(side=RIGHT, padx=10, pady=10)
control_frame0.pack(side=TOP, padx=10, pady=10)
control_frame1.pack(side=TOP, padx=10, pady=10)
control_frame2.pack(side=TOP, padx=10, pady=10)
control_frame3.pack(side=TOP, padx=10, pady=10)


# Add a button to load image
load_button = Button(control_frame0, text="Load Image", command=load_image)
load_button.pack(side=TOP)

zoom_in_button = Button(control_frame0, text="Zoom In", command=zoom_in)
zoom_in_button.pack(side=RIGHT)
zoom_out_button = Button(control_frame0, text="Zoom out", command=zoom_out)
zoom_out_button.pack(side=LEFT)

# Create a canvas to display images
panel = Label(image_frame)
panel.pack()

# Create sliders for threshold type and value
# objects that store the current values of the sliders for threshold type and value
threshold_operation_type_var = IntVar()
threshold_operation_value_var = IntVar()

morphological_operation_type_var = IntVar()
morphological_operation_kernel_var = IntVar()

blurring_filters_type_var = IntVar()
blurring_filters_kernel_var = IntVar()

# threshold operation
threshold_operation_label = Label(control_frame1, text='-- Threshold Operations --')
threshold_operation_label.pack(side=LEFT)

threshold_operation_type_label = Label(control_frame1, text='Type: \n 0: Binary \n 1: Binary Inverted \n 2: Truncate \n 3: To Zero \n 4: To Zero Inverted')
threshold_operation_type_label.pack(side=LEFT)

threshold_operation_type_slider = Scale(control_frame1, from_=0, to=4, orient=HORIZONTAL, variable=threshold_operation_type_var, command=image_processing)
threshold_operation_type_slider.pack(side=LEFT)

threshold_operation_value_label = Label(control_frame1, text='Value')
threshold_operation_value_label.pack(side=LEFT)

threshold_operation_value_slider = Scale(control_frame1, from_=0, to=255, orient=HORIZONTAL, variable=threshold_operation_value_var, command=image_processing)
threshold_operation_value_slider.pack(side=LEFT)

# morphological operation
morphological_operation_label = Label(control_frame2, text='-- Morphological Operations --')
morphological_operation_label.pack(side=LEFT)

morphological_operation_type_label = Label(control_frame2, text='Type: \n 0: Dilation \n 1: Erosion Inverted \n 2: Opening \n 3: Closing \n 4: Morphological Gradient \n 5: Top Hat \n 6: Black Hat \n 7: Horizontal Edge \n 8: Vertical Edge')
morphological_operation_type_label.pack(side=LEFT)

morphological_operation_type_slider = Scale(control_frame2, from_=0, to=8, orient=HORIZONTAL, variable=morphological_operation_type_var, command=image_processing)
morphological_operation_type_slider.pack(side=LEFT)

morphological_operation_kernel_label = Label(control_frame2, text='Kernel')
morphological_operation_kernel_label.pack(side=LEFT)

morphological_operation_kernel_slider = Scale(control_frame2, from_=1, to=30, orient=HORIZONTAL, variable=morphological_operation_kernel_var, command=image_processing)
morphological_operation_kernel_slider.pack(side=LEFT)

# blurring filters
blurring_filters_label = Label(control_frame3, text='-- Blurring Filters --')
blurring_filters_label.pack(side=LEFT)

blurring_filters_type_label = Label(control_frame3, text='Type: \n 0: Normal \n 1: Gaussian \n 2: Median \n 3: Bilateral ')
blurring_filters_type_label.pack(side=LEFT)

blurring_filters_type_slider = Scale(control_frame3, from_=0, to=3, orient=HORIZONTAL, variable=blurring_filters_type_var, command=image_processing)
blurring_filters_type_slider.pack(side=LEFT)

blurring_filters_kernel_label = Label(control_frame3, text='Kernel (2 * n + 1)')
blurring_filters_kernel_label.pack(side=LEFT)

blurring_filters_kernel_slider = Scale(control_frame3, from_=1, to=31, orient=HORIZONTAL, variable=blurring_filters_kernel_var, command=image_processing)
blurring_filters_kernel_slider.pack(side=LEFT)

save_button = Button(control_frame3, text="Save Image", command=save_image)
save_button.pack(side=BOTTOM)

# Start the Tkinter main loop
window.mainloop()
