
from flask import Flask, render_template, request, redirect, url_for, send_file
import mysql.connector
import os
os.system('cls')
from playsound import playsound
from werkzeug.utils import secure_filename
import pygame

app = Flask(__name__)
# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root@123',
    'database': 'team5'
}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp3'}

# function => allow only .mp3 audio files only
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# create connection with database
def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# create table to store songs path
def create_songs_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                artist VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

#Step 1 upload form on music player 
@app.route('/')
def upload_form():
    connection = create_connection()

    if connection:
        create_songs_table(connection)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM songs")
        songs = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('PlaySong.html', songs=songs)    # redirect to PlaySong.html
    
# # Play song function
# @app.route('/play_song/<path:file_path>')
# def play_song(file_path):
#     sound_file = os.path.join('static', 'uploads', os.path.basename(file_path))
#     print(f"Playing sound file: {sound_file}") 
#     playsound(sound_file) 
#     return render_template('playingsong.html', file_path=file_path)


# Initialize Pygame mixer
pygame.mixer.init()

# Create a dictionary to store pygame mixer instances for each song
song_instances = {}

@app.route('/play_song/<path:file_path>')
def play_song(file_path):
    sound_file = os.path.join('static', 'uploads', os.path.basename(file_path))

    # Check if the song is already playing
    if file_path in song_instances:
        # Pause the song
        pygame.mixer.pause()
    else:
        # Create a new pygame mixer instance for the song
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

        # Store the pygame mixer instance in the dictionary
        song_instances[file_path] = pygame.mixer.music

    return render_template('playingsong.html', file_path=file_path)

# Add a route to resume the paused song
@app.route('/resume_song/<path:file_path>')
def resume_song(file_path):
    # Check if the song is paused
    if file_path in song_instances:
        # Resume the song
        pygame.mixer.unpause()

    return render_template('playingsong.html', file_path=file_path)

# Delete song function 
@app.route('/delete_song/<int:song_id>')
def delete_song(song_id):
    connection = create_connection()

    if connection:
        try:
            cursor = connection.cursor()
            
            # Get the file_path for the selected song
            cursor.execute("SELECT file_path FROM songs WHERE id = %s", (song_id,))
            file_path = cursor.fetchone()[0]

            # Delete the song from the database
            cursor.execute("DELETE FROM songs WHERE id = %s", (song_id,))
            connection.commit()
            cursor.close()
            connection.close()

            # Delete the file from the uploads folder
            os.remove(os.path.join('static', 'uploads', os.path.basename(file_path)))

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    return redirect(url_for('upload_form'))

if __name__ == '__main__':
    app.run(debug=False)
