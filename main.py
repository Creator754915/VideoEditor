import threading
import time
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.simpledialog import askstring, askfloat

import cv2
from PIL import ImageTk
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
from moviepy.video.VideoClip import TextClip

video_clips = []
audio_clips = []
text_clips = []

preview_clip = None
preview_label = None

output_format = ".mp4"
base_rect_width = 5
rotation_degree = 0

bg_color = "#525252"
text_color = "white"
button_color = "#525252"
button_text_color = "white"


def import_video():
    global video_clips
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers vidéo", "*.mp4")])
    video_clip = VideoFileClip(file_path)
    video_clips.append(video_clip)
    update_timeline()


def import_audio():
    global audio_clips
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers audio", "*.mp3")])
    audio_clip = AudioFileClip(file_path)
    audio_clips.append(audio_clip)
    update_timeline()


def create_text_clip():
    text = askstring("Entrer le texte", "Saisissez le texte pour le clip texte:")
    if text:
        duration = askfloat("Durée du texte", "Saisissez la durée du texte (en secondes):")
        if duration:
            text_clip = {"text": text, "duration": duration}
            text_clips.append(text_clip)

            update_timeline()


def remove_last_video():
    if video_clips:
        video_clips.pop()
        update_timeline()


def remove_last_audio():
    if audio_clips:
        audio_clips.pop()
        update_timeline()


def close_preview():
    global preview_clip
    if preview_clip:
        preview_clip.close()
        preview_clip = None


def preview_video():
    global preview_clip
    if video_clips:
        preview_clip = concatenate_videoclips(video_clips)

        if rotation_degree != 0:
            preview_clip = preview_clip.rotate(rotation_degree, unit='deg', resample='bicubic')
        preview_label.configure(image=None) 
        preview_label.image = ImageTk.PhotoImage(image=Image.fromarray(preview_clip.get_frame(0)))
        preview_label.configure(image=preview_label.image)


def create_video():
    if video_clips and audio_clips:
        final_video = concatenate_videoclips(video_clips)
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.set_audio(final_audio)
        output_filename_str = output_filename_entry.get()
        output_path = f"{output_filename_str}{output_format}"
        final_video.write_videofile(output_path, codec="libx264")
        print(f"Vidéo créée avec succès: {output_path}")


def add_transition():
    global video_clips
    if len(video_clips) >= 2:
        transition_duration = askfloat("Durée de la transition", "Saisissez la durée de la transition (en secondes):")
        if transition_duration:
            transition_clip = VideoFileClip("path_to_transition_video.mp4").subclip(0, transition_duration)
            video_clips.append(transition_clip)
            update_timeline()


def rotate_left():
    global rotation_degree
    rotation_degree = (rotation_degree - 90) % 360
    update_timeline()


def rotate_right():
    global rotation_degree
    rotation_degree = (rotation_degree + 90) % 360
    update_timeline()


def update_timeline():
    global base_rect_width

    timeline_canvas.delete("all")

    total_width = 10
    for video_clip in video_clips:
        video_duration = video_clip.duration
        video_width = int(video_duration * base_rect_width)
        total_width += video_width + 10

    for audio_clip in audio_clips:
        audio_duration = audio_clip.duration
        audio_width = int(audio_duration * base_rect_width)
        total_width += audio_width + 10

    for text_clip in text_clips:
        text_duration = text_clip["duration"]
        text_rect_width = int(text_duration * base_rect_width)
        total_width += text_rect_width + 10

    timeline_canvas.config(scrollregion=(0, 0, total_width, 200))

    timeline_canvas.delete("background")

    canvas_width = timeline_canvas.winfo_width()
    canvas_height = timeline_canvas.winfo_height()

    rect_height = 24
    num_rectangles = canvas_height // rect_height

    for i in range(num_rectangles):
        y1 = i * rect_height
        y2 = y1 + rect_height
        timeline_canvas.create_rectangle(0, y1, canvas_width, y2, fill="#525252", outline="lightgreen",
                                         tags="background")

    video_rect_x = 5
    audio_rect_x = 5
    text_rect_x = 5

    for video_clip in video_clips:
        video_duration = video_clip.duration
        video_rect_width = int(video_duration * base_rect_width)
        timeline_canvas.create_rectangle(video_rect_x, 50, video_rect_x + video_rect_width, 70, fill="purple")
        duration_text = f"{video_duration:.1f}s"
        timeline_canvas.create_text(video_rect_x + video_rect_width / 2, 62, text=duration_text)
        video_rect_x += video_rect_width + 10

        if video_rect_x < canvas_width:
            transition_duration = 2.0
            transition_width = int(transition_duration * base_rect_width)
            timeline_canvas.create_rectangle(video_rect_x, 50, video_rect_x + transition_width, 70, fill="yellow")
            video_rect_x += transition_width + 5

    for audio_clip in audio_clips:
        audio_duration = audio_clip.duration
        audio_rect_width = int(audio_duration * base_rect_width)
        timeline_canvas.create_rectangle(audio_rect_x, 98, audio_rect_x + audio_rect_width, 118, fill="blue")
        duration_text = f"{audio_duration:.1f}s"
        timeline_canvas.create_text(audio_rect_x + audio_rect_width / 2, 108, text=duration_text)
        audio_rect_x += audio_rect_width + 10

    for text_clip in text_clips:
        text_duration = text_clip["duration"]
        text_rect_width = int(text_duration * base_rect_width)
        timeline_canvas.create_rectangle(text_rect_x, 146, text_rect_x + text_rect_width, 166, fill="green")
        text = text_clip["text"]
        timeline_canvas.create_text(text_rect_x + text_rect_width / 2, 156, text=text)
        text_rect_x += text_rect_width + 10


def adjust_rect_width(event):
    global base_rect_width

    if event.state & 4:
        if event.delta > 0:  
            base_rect_width += 1
        else: 
            if base_rect_width > 1:
                base_rect_width -= 1

        update_timeline()


def preview_on_space(event):
    timeline_canvas.create_rectangle(3, 0, 6, 185, fill="black", tags="time_line_rec")
    for i in range(timeline_canvas.winfo_width()-10):
        timeline_canvas.delete("time_line_rec")
        timeline_canvas.create_rectangle(3+i, 0, 6+i, 185, fill="black", tags="time_line_rec")

    if event.keysym == "space":
        preview_video()

app = Tk()
app.geometry("800x420")
app.minsize(800, 420)
app.title("Logiciel de Montage Vidéo Simple")
app.configure(bg="#525252")

button_frame = Frame(app, bg=bg_color)
button_frame.pack(side=LEFT)

button_width = 20

button_frame = Frame(app, bg=bg_color)
button_frame.pack(side=LEFT, padx=10, pady=10)

video_button = Button(button_frame, text="Importer une vidéo", command=import_video, width=button_width)
video_button.pack(pady=5)

audio_button = Button(button_frame, text="Importer un son", command=import_audio, width=button_width)
audio_button.pack(pady=5)

create_text_button = Button(button_frame, text="Créer du texte", command=create_text_clip, width=button_width, )
create_text_button.pack(pady=5)

add_transition_button = Button(button_frame, text="Ajouter une transition", command=add_transition, width=button_width)
add_transition_button.pack(pady=5)

rotate_left_button = Button(button_frame, text="Rotation gauche", command=rotate_left, width=button_width)
rotate_left_button.pack(pady=5)

rotate_right_button = Button(button_frame, text="Rotation droite", command=rotate_right, width=button_width)
rotate_right_button.pack(pady=5)

remove_video_button = Button(button_frame, text="Supprimer dernier clip", command=remove_last_video,
                             width=button_width)
remove_video_button.pack(pady=5)

remove_audio_button = Button(button_frame, text="Supprimer dernier son", command=remove_last_audio,
                             width=button_width)
remove_audio_button.pack(pady=5)

timeline_frame = Frame(app)
timeline_frame.pack(side=BOTTOM, fill=BOTH, expand=YES)
timeline_canvas = Canvas(timeline_frame, width=750, height=200)
timeline_canvas.pack(side=TOP)
timeline_scroll = Scrollbar(timeline_frame, orient=HORIZONTAL, command=timeline_canvas.xview)
timeline_scroll.pack(side=BOTTOM, fill=X)
timeline_canvas.config(xscrollcommand=timeline_scroll.set)
timeline_canvas.xview_moveto(0)


create_video_button = Button(app, text="Créer la vidéo", command=create_video, width=button_width)
create_video_button.pack()

preview_button = Button(app, text="Prévisualiser la vidéo", command=preview_video, width=button_width)
preview_button.pack()

output_filename_label = Label(app, text="Nom de la vidéo finale:")
output_filename_label.pack()
output_filename_entry = Entry(app)
output_filename_entry.pack()

output_format_label = Label(app, text="Format de sortie:")
output_format_label.pack()
output_format_combobox = ttk.Combobox(app, values=[".mp4", ".avi", ".mov"])
output_format_combobox.set(".mp4")
output_format_combobox.pack()

preview_frame = Frame(app)
preview_frame.pack(side=RIGHT, padx=10, pady=10)

preview_label = Label(preview_frame)
preview_label.pack()

app.bind("<Control-MouseWheel>", adjust_rect_width)
app.bind("<space>", preview_on_space)

app.mainloop()
