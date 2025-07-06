import re
from flask import Blueprint, jsonify, request, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user, LoginManager,login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User
import sqlalchemy as sa
from marshmallow import ValidationError  # using
from sqlalchemy import and_, select

from flask_httpauth import HTTPTokenAuth
from app import db
from app.models import User, Request, Result,SubResult
from threading import Thread
import threading
import time
from datetime import datetime, timedelta,timezone
#from app.api.errors import error_response

auth_bp = Blueprint('auth', __name__)
token_auth = HTTPTokenAuth()






@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None



@auth_bp.route('/login', methods=['POST','GET'])
def login():
    if token_auth.current_user():
        return jsonify({"message": "Already logged in"}), 200
    
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Missing email or password"}), 400
        user = db.session.scalar(sa.select(User).where(User.email == data['email']))

        if user is None or not check_password_hash(user.password_hash, data['password']):
            return jsonify({"error": "Invalid email or password"}), 401
        print(user.token)
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "token":user.get_token()
        }), 200


    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred {e}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_auth.login_required
def logout():
    #logout_user()
    token_auth.current_user().revoke_token()
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route('/check', methods=['POST'])
@token_auth.login_required
def check():
    #logout_user()
    #token_auth.current_user().revoke_token()
    return jsonify({"message": "logged in"}), 200


@auth_bp.route('/edit_user',methods=['PUT'])
@token_auth.login_required
def edit_user():
    try:
        data = request.get_json()
        if token_auth.current_user().id != data["id"]:
            return jsonify({"message": "enter your id"}), 403
        user = db.session.scalar(sa.select(User).where(and_(User.username == data['username'] , User.id != data['id'])))
        if user is not None:
            return jsonify({"error": "Please use a different username."}), 401


        user = db.session.scalar(sa.select(User).where(and_(User.email == data['email'] , User.id != data['id'])))
        if user is not None:
            return jsonify({"error": "Please use a different email address."}), 401

        if 'phone_number' in data :
            user = db.session.scalar(sa.select(User).where(and_(User.phone_number == data['phone_number'] , User.id != data['id'])))
            if user is not None:
                return jsonify({"error": "Please use a different phone number"}), 401


        import re

        email_pattern =  r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_number_pattern = r'^01(0|1|2|5)\d{8}$'

        if not re.match(email_pattern,data['email']):
            return jsonify({"error": "Please enter a valid mail"}), 401
        if 'phone_number' in data and not re.match(phone_number_pattern,data['phone_number']):
            return jsonify({"error": "Please enter a valid phone_number"}), 401

        user = db.get_or_404(User, data['id'])
        for field, value in data.items():
            if field in {'username', 'email', 'phone_number'}:
                setattr(user, field, value)

        db.session.commit()

        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred {e}'}), 500




@auth_bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return jsonify({"message": "Already logged in"}), 200
    try:
        data = request.get_json()
        user = db.session.scalar(sa.select(User).where(User.username == data['username']))
        if user is not None:
            return jsonify({"error": "Please use a different username."}), 401


        user = db.session.scalar(sa.select(User).where(User.email == data['email']))
        if user is not None:
            return jsonify({"error": "Please use a different email address."}), 401

        if 'phone_number' in data :
            user = db.session.scalar(sa.select(User).where(User.phone_number == data['phone_number']))
            if user is not None:
                return jsonify({"error": "Please use a different phone number"}), 401


        import re

        email_pattern =  r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_number_pattern = r'^01(0|1|2|5)\d{8}$'

        if not re.match(email_pattern,data['email']):
            return jsonify({"error": "Please enter a valid mail"}), 401
        if data['password'] != data['password2']:
            return jsonify({"error": "passwords do not match"}), 401
        if 'phone_number' in data and not re.match(phone_number_pattern,data['phone_number']):
            return jsonify({"error": "Please enter a valid phone_number"}), 401
            


        user = User(
            username = data['username'],
            email = data['email'],
            password_hash = generate_password_hash(data['password'])
        )
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully!",
            "user": user.to_dict()
        }), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def proccess_requests(app):
        
    with app.app_context():
        while True:
            print('proccess_requests:-')
            subq = select(Result.request_id)
            rows = db.session.execute(sa.select(Request.request_id,Request.start_date,Request.end_date,Request.query, Request.number_of_tweets,Request.number_of_posts,Request.x_twitter,Request.facebook).where(~Request.request_id.in_(subq)).order_by(Request.request_date.asc()))
            from app.real_dirc.run_me import run_all_scripts as run_twitter
            from app.real_dirc_facebook.run_me import run_facebook
            for row in rows:
                result = Result(request_id = row[0])
                db.session.add(result)
                db.session.flush()
                print(f'row = {row}')
                if row[6]:
                    (data,tmp) = run_twitter(row[3],row[1].isoformat(),row[2].isoformat(),row[0],row[4]) if row[4] else run_twitter(row[3],row[1].isoformat(),row[2].isoformat(),row[0])
                    print(f'data from twitter = {data}')

                
                    for subData in data:
                        print(f'subData : {subData}\n_________________\n')
                        user = subData.get('user', {})

                        try:
                            subresult = SubResult(
                                result_id=result.result_id,
                                tweet_id=subData.get('tweet_id'),
                                creation_date= None if subData.get('creation_date') is None else datetime.strptime(subData.get('creation_date'),"%a %b %d %H:%M:%S %z %Y").date(),
                                text=subData.get('text', ''),
                                language=subData.get('language'),
                                favorite_count=subData.get('favorite_count'),
                                retweet_count=subData.get('retweet_count'),
                                reply_count=subData.get('reply_count'),
                                quote_count=subData.get('quote_count'),
                                views_count=subData.get('views'),
                                source=subData.get('source'),
                                sentiment=subData.get('sentiment'),

                                user_creation_date= None if user.get('creation_date') is None else datetime.strptime(user.get('creation_date'),"%a %b %d %H:%M:%S %z %Y").date(),
                                user_id=user.get('user_id'),
                                user_username=user.get('username'),
                                user_name=user.get('name'),
                                user_follower_count=user.get('follower_count'),
                                user_following_count=user.get('following_count'),
                                user_is_verified=user.get('is_verified'),
                                user_blue_is_verified=user.get('is_blue_verified'),
                                user_location=user.get('location'),
                                user_description=user.get('description'),
                                user_number_of_tweets=user.get('number_of_tweets'),
                                user_bot=user.get('bot')
                            )
                            db.session.add(subresult)
                        except Exception as e:
                            db.session.rollback()
                            traceback.print_exc()


                if row[7]:
                    (data,tmp) = run_facebook(row[3],row[1].isoformat(),row[2].isoformat(),row[0],row[4]) if row[5] else run_facebook(row[3],row[1].isoformat(),row[2].isoformat(),row[0])
                    print(f'data from facebook = {data}')

                
                    for subData in data:
                        print(f'subData : {subData}\n_________________\n')

                        try:
                            subresult = SubResult(
                                result_id=result.result_id,
                                tweet_id=subData.get('post_id'),
                                creation_date= None if subData.get('timestamp') is None else datetime.strptime(subData.get('timestamp'),"%d/%m/%Y").date(),
                                text=subData.get('message', ''),
                                favorite_count=subData.get('reactions_count'),
                                retweet_count=subData.get('reshare_count'),
                                reply_count=subData.get('comments_count'),
                                source='facebook',
                                sentiment='positive' if subData.get('predicted_sentiment') == "Positive" else
                                          'negative' if subData.get('predicted_sentiment') == "Negative" else
                                          'neutral',
                                user_id=subData.get('author_id'),
                                user_name=subData.get('author_name'),
                            )
                            db.session.add(subresult)
                        except Exception as e:
                            db.session.rollback()
                            traceback.print_exc()


                db.session.commit()
                time.sleep(10)
            time.sleep(10)

background_thread_started = False
background_thread_lock = threading.Lock()

@auth_bp.route('/send_request',methods=['POST'])
@token_auth.login_required
def send_request():
    global background_thread_started
    try:
        data = request.get_json()
        if not data['platforms']['facebook'] and not data['platforms']['x_twitter']:
            return jsonify({"error": "Please select a platforms"}), 401
        # check for fields : not null with right limits
        print(data)
        from datetime import datetime
        req= Request(
            request_description = data['request_description'],
            start_date = datetime.strptime(data['start_date'], "%d/%m/%Y").date(), 
            end_date = datetime.strptime(data.get('end_date'), "%d/%m/%Y").date() if data.get('end_date') 
            else datetime.now(timezone.utc) ,
            query = data['request_name'],
            facebook = data['platforms']['facebook'],
            x_twitter = data['platforms']['x_twitter'],
            number_of_tweets = data.get('number_of_tweets'),
            number_of_posts = data.get('number_of_posts'),
            user_id = token_auth.current_user().id,
        )
        db.session.add(req)
        db.session.commit()
        with background_thread_lock:
            if not background_thread_started:
                app = current_app._get_current_object()
                thread = threading.Thread(target=proccess_requests, args=(app,), daemon=True)
                thread.start()
                background_thread_started = True
        return jsonify({
            "message": "request sent successfully!",
            "request": req.to_dict()
        }), 200


    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred {e}'}), 500

@auth_bp.route('/profile',methods=['POST'])
@token_auth.login_required
def get_profile():
    try:
        user_id = token_auth.current_user().id
        data = request.get_json()
        rows = db.session.execute(sa.select(Result.request_id).where(Request.user_id == user_id).where(Request.request_id == Result.request_id))
        answered_requests_ids = set()
        for row in rows:
            answered_requests_ids.add(row[0])
        print(f'answered_requests_ids = {answered_requests_ids}')
        rows = db.session.execute(sa.select(Request).where(Request.user_id == user_id))

        requests_done = []
        requests_in_queue = []
        for row in rows:
            rs = row[0].__dict__
            rs = {k:v for k,v in rs.items() if k not in {
                    '_sa_instance_state'
                }}
            print(rs)
            if rs['request_id'] in answered_requests_ids:
                requests_done.append(rs)
                #requests_done.append({'name':row[1],'details':row[2]})
            else:
                requests_in_queue.append(rs)
                #requests_in_queue.append({'name':row[1],'details':row[2]})
        
        return jsonify({
            "message": "request sent successfully!",
            "requests_done": requests_done,
            "requests_in_queue": requests_in_queue
        }), 200



    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred {e}'}), 500
    

@auth_bp.route('/dashboard',methods=['POST'])
@token_auth.login_required
def dashboard(): 
    try:
        user_id = token_auth.current_user().id
        data = request.get_json()
        result_list = []

        resId_query = db.session.execute(sa.select(Result.result_id, Request).where(Request.user_id == user_id).where(Request.request_id == Result.request_id))
        for id_query in resId_query:

            req = id_query[1].__dict__
            req = {k:v for k,v in req.items() if k not in {
                '_sa_instance_state'
            }}
            print(f'req = {req}')

            sentiments = {'positive':'', 'negative':'','neutral':''}
            for sentiment in sentiments:
                filters = [SubResult.result_id == id_query[0],
                           SubResult.sentiment == sentiment]
                if data.get('creation_date'):
                    filters.append(SubResult.creation_date >= sa.literal(data['creation_date']))
                if data.get('end_date'):
                    filters.append(SubResult.creation_date <= sa.literal(data['end_date']))
                if data.get('language'):
                    filters.append(SubResult.language == sa.literal(data['language']))
                if data.get('favorite_count'):
                    filters.append(SubResult.favorite_count >= sa.literal(data['favorite_count']))
                if data.get('retweet_count'):
                    filters.append(SubResult.retweet_count >= sa.literal(data['retweet_count']))
                if data.get('reply_count'):
                    filters.append(SubResult.reply_count >= sa.literal(data['reply_count']))
                if data.get('quote_count'):
                    filters.append(SubResult.quote_count >= sa.literal(data['quote_count']))
                if data.get('views_count'):
                    filters.append(SubResult.views_count >= sa.literal(data['views_count']))
                if data.get('source') and data.get('source') != 'twitter':
                    filters.append(SubResult.source == sa.literal(data['source']))
                if data.get('user_creation_date'):
                    filters.append(SubResult.user_creation_date >= sa.literal(data['user_creation_date']))
                if data.get('user_follower_count'):
                    filters.append(SubResult.user_follower_count >= sa.literal(data['user_follower_count']))
                if data.get('user_following_count'):
                    filters.append(SubResult.user_following_count >= sa.literal(data['user_following_count']))
                if data.get('user_blue_is_verified'):
                    filters.append(SubResult.user_blue_is_verified == sa.literal(data['user_blue_is_verified']))
                if data.get('user_location'):
                    filters.append(SubResult.user_location == sa.literal(data['user_location']))
                if data.get('user_number_of_tweets'):
                    filters.append(SubResult.user_number_of_tweets >= sa.literal(data['user_number_of_tweets']))
                if data.get('user_bot'):
                    filters.append(SubResult.user_bot == sa.literal(data['user_bot']))



                rows = db.session.execute(sa.select(SubResult).where(sa.and_(*filters)).order_by(SubResult.views_count.desc()))
                if data.get('sort_by') == 'views_count':
                    rows = db.session.execute(sa.select(SubResult).where(sa.and_(*filters)).order_by(SubResult.views_count.desc())
                  )
                if data.get('sort_by') == 'favorite_count':
                    rows = db.session.execute(sa.select(SubResult).where(sa.and_(*filters)).order_by(SubResult.favorite_count.desc())
                  )
                if data.get('sort_by') == 'reply_count':
                    rows = db.session.execute(sa.select(SubResult).where(sa.and_(*filters)).order_by(SubResult.reply_count.desc())
                  )
                if data.get('sort_by') == 'follower_count':
                    rows = db.session.execute(sa.select(SubResult).where(sa.and_(*filters)).order_by(SubResult.user_follower_count.desc())
                  )
                if data.get('sort_by') == 'retweet_count':
                    rows = db.session.execute(sa.select(SubResult).where(sa.and_(*filters)).order_by(SubResult.retweet_count.desc())
                  )
                count_twitter = 0
                count_facebook = 0
                important_posts_twitter = []
                important_posts_facebook = []
                for row in rows:
                    rs = row[0].__dict__
                    rs = {k:v for k,v in rs.items() if k not in {
                    '_sa_instance_state'
                }}
                    print(f'rs = {rs}')
                    if rs.get('source') == 'facebook':
                        if data.get("source") != 'twitter':
                            count_facebook+=1
                            if count_facebook <=500000:
                                important_posts_facebook.append(rs)
                    else:
                        count_twitter+=1
                        if count_twitter <=500000:
                            important_posts_twitter.append(rs)

                sentiments[sentiment]={
                                        "count":count_twitter,
                                        "posts":important_posts_twitter,
                                        "count_facebook":count_facebook,
                                        "posts_from_facebook":important_posts_facebook
                                     }
            result_list.append({
                    "id":id_query[0],
                    "dashboard":sentiments,
                    "request":req
        })

        print(result_list)
        return jsonify({
            "message": "dashboard is done",
            'result':result_list
        }), 200



    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred {e}'}), 500
