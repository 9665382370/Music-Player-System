from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import mysql.connector
import os

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

def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        return render_template('upload_audio.html', songs=songs)
    


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            connection = create_connection()
            if connection:
                try:
                    cursor = connection.cursor()

                    cursor.execute("""
                        INSERT INTO songs (title, artist, file_path) VALUES (%s, %s, %s)
                    """, (title, artist, f'uploads/{filename}'))

                    connection.commit()
                    cursor.close()
                    connection.close()

                except mysql.connector.Error as err:
                    print(f"Error: {err}")

    return redirect(url_for('upload_form'))

if __name__ == '__main__':
    app.run(debug=True)
