#POWERSHELL 
#  $env:FLASK_APP = "application.py"  
#  $env:FLASK_ENV = "development" 
#  $env:FLASK_DEBUG=0
#CMD 
#  set FLASK_APP=application.py 
#  set FLASK_ENV=development 
#  set FLASK_DEBUG=0
#Linux,Mac 
#  export FLASK_APP=application.py 
#  export FLASK_ENV=development 
#  export FLASK_DEBUG=0

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///EAD.db")

@app.route("/")
@login_required
def index():
    verifyAndUpdateLevel()
    playlistsCreatedByUser = db.execute('SELECT * FROM playlists WHERE user_id=:user_id',user_id=session['user_id'])
    videosCreatedByUser = db.execute('SELECT * FROM videos WHERE user_id=:user_id',user_id=session['user_id'])
    categoriesCreatedByUser = db.execute('SELECT * FROM categories WHERE user_id=:user_id',user_id=session['user_id'])
    return render_template("index.html",message=session['messageOfIndexPage'],playlists=playlistsCreatedByUser,categories=categoriesCreatedByUser,videos=videosCreatedByUser)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html",message_error="You must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html",message_error="You must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html",message_error="Invalid username/password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session['messageOfIndexPage'] = "Log in"

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    session['messageOfIndexPage'] = "Log out"
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        #Get information of Form and verify if any of them is Null
        username = request.form.get("username")
        password = request.form.get("password")
        passwordAgain = request.form.get("password_again")
        image = request.form.get("image")
        about = request.form.get("about")

        # Ensure username was submitted
        if not username:
            return render_template("register.html", message_error="You must provide username")
        
        #Ensure image was submitted
        elif not image:
            return render_template("register.html", message_error="You must provide a link of image")

        #Ensure about was submitted
        elif not about:
            return render_template("register.html", message_error="You must provide an description")

        # Ensure password was submitted
        elif not password or not passwordAgain:
            return render_template("register.html", message_error="You must provide password")

        #Ensure passwords are equal
        elif password != passwordAgain:
            return render_template("register.html", message_error="The passwords are not equal")

        #Verify if user already exists
        userAlreadyExists = db.execute("SELECT * FROM users WHERE username = :username",
        username=username)

        if(len(userAlreadyExists) == 1):
            return render_template("register.html", message_error="That name is already in use")

        # Registring user
        db.execute("INSERT INTO users (username,hash,level,image,about) VALUES(:username,:hashpassword,1,:image,:about); ",
        username=username,hashpassword=generate_password_hash(password),image=image,about=about)

        # Taking user id to the session
        user = db.execute('SELECT * FROM users WHERE username = :username',username=username)[0]
        session["user_id"] = user["id"]
        session['messageOfIndexPage'] = 'Registered!'
        return redirect('/')
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/change_password',methods=["GET","POST"])
@login_required
def change_password():
    """Change user password"""
    session['messageOfIndexPage'] = None
    if request.method == "POST":
        #Get Information from form and verify if any of them is Null.
        oldPassword = request.form.get('old_password')
        newPassword = request.form.get('new_password')
        newPasswordAgain = request.form.get('new_password_again')

        if not oldPassword:
            return apology("change_password.html", message_error='We need your old password')

        elif not newPassword or not newPasswordAgain:
            return render_template("change_password.html", message_error='We need your old password')

        #Verify if newPassword and newPasswordAgain are equal
        elif newPassword != newPasswordAgain:
            return render_template("change_password.html", message_error="The new password are not equal")

        #Verify if newPassword and oldPassword are equal
        elif newPassword == oldPassword:
            return render_template("change_password.html", message_error="Your new password cannot be equal to the old password")

        #Get old password from Database
        passwordInDatabase = db.execute('SELECT hash from users WHERE id=:userId;'
        ,userId=session["user_id"])[0]['hash']

        #Check if the old password is what is in the form
        if check_password_hash(passwordInDatabase,oldPassword) :
            #Alter hash in database
            newHash = generate_password_hash(newPassword)
            db.execute('UPDATE users SET hash = :newHash WHERE id = :userId;'
            ,newHash=newHash,userId=session["user_id"])

            #Redirect for index page
            session['messageOfIndexPage'] = 'Password has changed!'
            return redirect('/')
        else:
            return render_template("change_password.html",message_error='Your old password is not that')
    else:
        return render_template("change_password.html")


@app.route("/perfil",methods=["GET", "POST"])
@login_required
def perfil():
    aboutUser = db.execute('SELECT * FROM users WHERE id = :userId',userId=session["user_id"])[0]
    session['messageOfIndexPage'] = None
    if request.method == "POST":
        username = request.form.get("username")
        image = request.form.get("image")
        about = request.form.get("about")
        
        if not username:
            return render_template("perfil.html", message_error="You must provide a username",aboutUser=aboutUser)
        elif not image:
            return render_template("perfil.html", message_error="You must provide a link of image",aboutUser=aboutUser)
        elif not about:
            return render_template("perfil.html", message_error="You must provide a description",aboutUser=aboutUser)

        db.execute('UPDATE users SET username=:username, image=:image, about=:about  WHERE id = :userId '
        ,userId=session['user_id'],username=username,image=image,about=about)

        return redirect('/')
    else:
        return render_template("perfil.html",aboutUser=aboutUser)

@app.route("/create_category", methods=["GET", "POST"])
@login_required
def create_category():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("create_category.html", message_error="You must provide a name")

        #Verify if that category already exists
        category = db.execute('SELECT * FROM categories WHERE name = :name',name=name)
        if(len(category) == 1):
            return render_template("create_category.html", message_error="That category already exists")

        db.execute('INSERT INTO categories (name,user_id) VALUES (:name,:user_id)',name=name,user_id=session['user_id'])
        session['messageOfIndexPage'] = 'You have create a new category: ' + name
        return redirect('/')
    else:
        verifyAndUpdateLevel()
        session['messageOfIndexPage'] = None
        return render_template("create_category.html")

@app.route("/create_video",methods=["GET", "POST"])
@login_required
def create_video():
    categories = db.execute('SELECT name FROM categories')
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        link = request.form.get("link")
        
        if not name:
            return render_template("create_video.html", message_error="You must provide a name",categories=categories)
        elif not category:
            return render_template("create_video.html", message_error="You must provide a category",categories=categories)
        elif not link:
            return render_template("create_video.html", message_error="You must provide a link",categories=categories)
        
        videos = db.execute('SELECT * FROM videos WHERE name=:name',name=name)
        if len(videos) == 1:
            return render_template("create_video.html", message_error="That video already exists",categories=categories)

        db.execute('INSERT INTO videos (link,name,category,user_id) VALUES(:link,:name,:category,:user_id)',
        link=link,name=name,category=category,user_id=session['user_id'])

        session['messageOfIndexPage'] = 'You have create a new video: ' + name
        return redirect('/')
    else:
        verifyAndUpdateLevel()
        session['messageOfIndexPage'] = None
        return render_template("create_video.html",categories=categories)

@app.route("/explore")
@login_required
def explore():
    videos = db.execute('SELECT * FROM videos')
    playlists = db.execute('SELECT * FROM playlists')
    session['messageOfIndexPage'] = None
    verifyAndUpdateLevel()
    return render_template("explore.html",videos=videos,playlists=playlists)

@app.route("/explore/video/<id_video>")
@login_required
def view_video(id_video):
    video = db.execute('SELECT * FROM videos WHERE id=:id_video',id_video=id_video)[0]
    thatVideoWasLiked = db.execute('SELECT value FROM likes_videos WHERE video_id=:id_video and user_id=:user_id',
    id_video=id_video,user_id=session['user_id'])
    totalLikes = db.execute('SELECT Count(value) FROM likes_videos WHERE video_id=:id_video and value=1'
    ,id_video=id_video)
    totalDislikes= db.execute('SELECT Count(value) FROM likes_videos WHERE video_id=:id_video and value=-1'
    ,id_video=id_video)

    if thatVideoWasLiked == []:
        thatVideoWasLiked = [{'value':0}]

    if totalLikes == []:
        totalLikes = [{'Count(value)':0}]

    if totalDislikes == []:
        totalDislikes = [{'Count(value)':0}]

    session['messageOfIndexPage'] = None
    verifyAndUpdateLevel()
    return render_template("view_video.html",video=video,thatVideoWasLiked=int(thatVideoWasLiked[0]['value']),totalLikes=totalLikes[0]['Count(value)'],totalDislikes=totalDislikes[0]['Count(value)'])

@app.route("/explore/video/<id_video>/<action>",methods=['POST','DELETE'])
@login_required
def like_video(id_video,action):
    if action == 'like':
        value = 1
    elif action == 'dislike':
        value = -1
    else:
        return "Error:That value don't exists"
    
    if request.method == "POST":

        like = db.execute('SELECT * FROM likes_videos WHERE video_id=:id_video and user_id=:user_id',
        id_video=id_video,user_id=session['user_id'])

        if(len(like) == 1):
            db.execute('UPDATE likes_videos SET value=:value WHERE video_id=:id_video and user_id=:user_id',
            value=value,id_video=id_video,user_id=session['user_id'])

        else:
            db.execute('INSERT INTO likes_videos(video_id,user_id,value) VALUES(:id_video,:user_id,:value)',
            id_video=id_video,user_id=session['user_id'],value=value)   
    else:
        like = db.execute('SELECT * FROM likes_videos WHERE video_id=:id_video and user_id=:user_id',
        id_video=id_video,user_id=session['user_id'])

        if(len(like) == 1):
            db.execute('DELETE FROM likes_videos WHERE video_id=:id_video and user_id=:user_id and value=:value',
            id_video=id_video,user_id=session['user_id'],value=value)

        else:
            return "That user don't have liked or disliked that video0"
    
    return 'Sucess'


@app.route("/create_playlist",methods=["GET", "POST"])
@login_required
def create_playlist():
    categories = db.execute('SELECT name FROM categories')
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        image = request.form.get("image")
        if not name:
            return render_template("create_playlist.html",message_error="You must provide a name",categories=categories)

        elif not category:
            return render_template("create_playlist.html",message_error="You must provide a category",categories=categories)

        elif not image:
            return render_template("create_playlist.html",message_error="You must provide a link")

        playlistWithThatName = db.execute('SELECT * FROM playlists WHERE name = :name',name=name)
        if(len(playlistWithThatName) == 1):
            return render_template("create_playlist.html",message_error="That playlist already exists",categories=categories)
        
        db.execute('INSERT INTO playlists (name, category,user_id,image) VALUES (:name, :category, :user_id,:image)'
        ,name=name,category=category,user_id=session["user_id"],image=image)
        
        session['messageOfIndexPage'] = 'You have create a new playlist: ' + name
        return redirect('/')
    else:
        verifyAndUpdateLevel()
        session['messageOfIndexPage'] = None
        return render_template("create_playlist.html",categories=categories)

@app.route("/update_playlist/<id_playlist>",methods=["GET", "POST"])
@login_required
def update_playlist(id_playlist):
    playlist = db.execute('SELECT * FROM playlists WHERE id = :id_playlist',id_playlist=id_playlist)[0]
    categories = db.execute('SELECT * FROM categories WHERE name != :name',name=playlist['category'])
    videos_ids = db.execute('SELECT video_id FROM videos_playlists WHERE playlist_id =:id_playlist ',id_playlist=id_playlist)
    videos = []
    if(len(videos_ids) >= 1):
        for video_id in videos_ids:
            print('id: ',video_id)
            video_name = db.execute('SELECT name FROM videos WHERE id=:video_id',video_id=video_id['video_id'])[0]
            print('name ',video_name)
            videos.append(video_name)
    
    if request.method == "POST":
        video = request.form.get("video")
        image = request.form.get("image")
        category = request.form.get("category")
        name = request.form.get("name")

        if not name:
            return render_template("update_playlist.html",
            message_error="You must provide a name",playlist=playlist,categories=categories,videos=videos)

        elif not category:
            return render_template("update_playlist.html",
            message_error="You must provide a category",playlist=playlist,categories=categories,videos=videos)

        elif not image:
            return render_template("update_playlist.html",
            message_error="You must provide a link",playlist=playlist,categories=categories,videos=videos)
        
        db.execute('UPDATE playlists SET name=:name,category=:category,image=:image WHERE id=:id_playlist',
            category=category,name=name,image=image,id_playlist=id_playlist)

        if video != '':
            video_db = db.execute('SELECT id,name FROM videos where name = :video_name',video_name=video)[0]
            video_id = video_db['id']
            video_name = video_db['name']
            db.execute('INSERT INTO videos_playlists(video_id,playlist_id) VALUES (:video_id,:playlist_id)'
            ,video_id=video_id,playlist_id=id_playlist)
            session['messageOfIndexPage'] = f"Você inseriu o vídeo {video_name[:20]}... na Playlist {playlist['name'][:20]}..."
        else:
            session['messageOfIndexPage'] = f"Você alterou a playlist {playlist['name'][:20]}..."
        return redirect('/')
    else:
        verifyAndUpdateLevel()
        return render_template("update_playlist.html"
        ,playlist=playlist,categories=categories,videos=videos)

@app.route("/explore/playlist/<id_playlist>")
@login_required
def view_playlist(id_playlist):
    playlist = db.execute('SELECT * FROM playlists WHERE id=:id_playlist',id_playlist=id_playlist)
    videos_ids = db.execute('SELECT video_id FROM videos_playlists WHERE playlist_id = :id_playlist',id_playlist=id_playlist)
    videos = []
    for video_id in videos_ids:
        video = db.execute('SELECT * FROM videos WHERE id = :video_id',video_id=video_id['video_id'])
        videos.append(video)
    user_id = playlist[0]['user_id']
    user = db.execute('SELECT * FROM users WHERE id = :user_id',user_id=user_id)
    verifyAndUpdateLevel()
    return render_template("view_playlist.html",playlist=playlist[0],videos=videos,user=user[0])

def verifyAndUpdateLevel():
    atualLevel = int(db.execute('SELECT level FROM users WHERE id = :user_id',user_id=session['user_id'])[0]['level'])
    categoriesCreatedByUser = db.execute('SELECT Count(name) FROM categories WHERE user_id = :user_id',user_id=session['user_id'])[0]['Count(name)']
    playlistsCreatedByUser = db.execute('SELECT Count(name) FROM playlists WHERE user_id = :user_id',user_id=session['user_id'])[0]['Count(name)']
    videosCreatedByUser = db.execute('SELECT Count(name) FROM videos WHERE user_id = :user_id',user_id=session['user_id'])[0]['Count(name)']
    categoriaPoint = categoriesCreatedByUser * 2
    videoPoint = videosCreatedByUser * 3
    playlistPoint = playlistsCreatedByUser * 4
    total = playlistPoint + categoriaPoint + videoPoint
    score = int(total / 6)
    if(atualLevel != score):
        db.execute('UPDATE users SET level = :level WHERE id = :user_id',level=score,user_id=session['user_id'])
        session['messageOfIndexPage'] = f'Your level is now:{score}'
    return None

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)