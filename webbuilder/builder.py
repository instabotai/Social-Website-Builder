import time
from mtcnn.mtcnn import MTCNN
import cv2
from instabotai import ai
import shutil
from tiktokapi import downloader
import numpy as np
import json
import MySQLdb
import pdb
import os
import re
from tqdm import tqdm
import tensorflow as tf
import multiprocessing
from multiprocessing import Process
import timeit
tf.config.threading.set_intra_op_parallelism_threads(24)

ig_username = ""
ig_password = ""
ig_username2 = ""
ig_password2 = ""
ig_username3 = ""
ig_password3 = ""

COOKIES = {}


#bot = ai.Bot(do_logout=True)
bot = ai.Bot()
bot.api.login(username=ig_username, password=ig_password, is_threaded=True, use_cookie=True)
#time.sleep(2)

class Ai(object):
    def __init__(self):
        pass

    def face_detection_photo(self, path):

        start = time.time()
        path = str(path)
#        img = cv2.imread(path)
        img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        scale_percent = 10 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        detector = MTCNN()
        detected = detector.detect_faces(img)
        end = time.time()
        print(f"Runtime of the program is {end - start}")
        return detected

    def face_detection_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        success, image = cap.read()
        count = 0
        frame = 0
        while success:
            for frame in range(1):
                try:
                    cv2.imwrite("frame%d.jpg" % count, image)# save frame as JPEG file
                    success, image = cap.read()
                    print('Read a new frame: ', success)
                    img_file = "frame" + str(count) + ".jpg"
                    img = cv2.cvtColor(cv2.imread(img_file), cv2.COLOR_BGR2RGB)
                    detector = MTCNN()
                    detected = detector.detect_faces(img)
                    shutil.os.remove(img_file)
                    count += 1
                    frame += 1
                except Exception as e:
                    print(e)

            return detected

    def ig_video_scraper_and_face_detector(self, username):
        scraper = Scraper()
        videos = scraper.instagram_videos_scraper(username)
        for video in videos:
            video_path = profiles + "/0_" + profiles + "_" + str(video) + ".mp4"
            try:
                Ai.face_detection_video(video_path)
            except Exception as e:
                print(e)
                pass

    def tiktok_video_scraper_and_face_detector(self, username):
        scraper = Scraper()
        videos = scraper.tiktok_videos_scraper(username)
        for video in videos:
            video_path = profiles + "/0_" + profiles + "_" + str(video) + ".mp4"
            try:
                Ai.face_detection_video(video_path)
            except Exception as e:
                print(e)

class Scraper(object):
    def __init__(self):
        all_profiles = []
        user_videos_with_face = []
        self.all_profiles = all_profiles

    def tiktok_videos_scraper(self, user):
        tiktok = downloader.Downloader()
        videos = tiktok.download_user_videos(user)
        return videos

    def instagram_photos_scraper(self, user):
        medias = bot.get_total_user_medias(user)
        for media in medias:
            try:
                print(media)
                bot.download_photo(media, folder=user)
                path_file = "./" + user + "/" + user + "_" + str(media) + ".jpg"
                ai = Ai()
                detect = ai.face_detection_photo(path_file)
                print(detect)
                if not detect:
                    print("no face detected")
                    shutil.os.remove(path_file)
                elif detect:
                    print("face detected")
            except Exception as e:
                print(e)

    def instagram_videos_scraper(self, user):
        user_id = bot.get_user_id_from_username(user)
        time.sleep(1)
        user_medias = bot.get_total_user_medias(user_id)
        for media_id in user_medias:
            bot.api.media_info(media_id)
            json = bot.api.last_json
            media_type = json["items"][0]["media_type"]
            if media_type == 2:
                print("Downloading Video")
                bot.download_video(media_id, folder=user)
                self.all_profiles.append(str(media_id))
                print(self.all_profiles)
            else:
                print("Not a video")
        return self.all_profiles

    def get_user_profile_picture(self, user):
        pass

    def get_ig_followers_count(self, user_id):
        user_info = bot.get_user_info(user_id)
        followers = user_info["follower_count"]
        return followers

class Database(object):

    def __init__(self, host, username, password, db):
        # Test if it works
        host = self.host
        username = self.username
        password = self.password
        db = self.db
        db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.db)
        self.db = db


    def create_profile(self, user):
        try:
            db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.db)
            user_id = bot.get_user_id_from_username(user)
            ig_url = "http://www.instagram.com/@" + user
            user_info = bot.get_user_info(user_id)
            try:
                full_name = user_info["full_name"]
            except:
                full_name = None
            if full_name is None:
                full_name = ""
            print(user_info)
            profile_pic_url = user_info["profile_pic_url"]
            followers_count = user_info["follower_count"]
            following_count = user_info["following_count"]
            try:
                city = user_info["city_name"]
            except:
                city = None
            if city is None:
                city = ""
#            profile_pic_url = str(profile_pic_url)
#            profile_pic_url = profile_pic_url.split("?_nc")
#            profile_pic_url = profile_pic_url[0]
#            print(profile_pic_url)
#            db = self.db
            cur = db.cursor()
            isert = cur.execute("""INSERT INTO Models (user_id, username, full_name,
                                tiktok_url, instagram_profile, profile_pic_url,
                                ig_followers, ig_following, city) VALUES('"""+user_id+"""','"""+user+"""',
                                '"""+str(full_name)+"""', 'tiktok_url', '
                                """+str(ig_url)+"""', '"""+str(profile_pic_url)+"""',
                                '"""+str(followers_count)+"""',
                                '"""+str(following_count)+"""', '"""+str(city)+
                                """')""")
            print(isert)
            db.commit()
            db.close()
        except Exception as e:
            print(e)

    def post_video(self, user, path, likes):
        db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.db)
        cur = db.cursor()
        user_id = bot.get_user_id_from_username(user)
        user = str(user)
        photo_url = str(path)
        likes = str(likes)
        isert = cur.execute("""INSERT INTO Videos (user_id, username, video_url,
                            likes) VALUES('"""+user_id+"""', '"""+user+"""',
                            '"""+photo_url+"""', '"""+likes+"""')""")
#        isert = cur.execute("""UPDATE Photos set ig_videos = '"""+path+"""' WHERE username = '"""+user+"""'""")
        db.commit()
#        time.sleep(5)
        print(isert)
        db.close()

        pass

    def post_photo(self, user, path, likes):
        try:
            db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.db)
            cur = db.cursor()
            user_id = bot.get_user_id_from_username(user)
            user = str(user)
            photo_url = str(path)
            likes = str(likes)
            isert = cur.execute("""INSERT INTO Photos (user_id, username, photo_url,
                                likes) VALUES('"""+user_id+"""', '"""+user+"""',
                                '"""+photo_url+"""', '"""+likes+"""')""")
#            isert = cur.execute("""UPDATE Photos set ig_videos = '"""+path+"""' WHERE username = '"""+user+"""'""")
            db.commit()
#            time.sleep(5)
            print(isert)
            db.close()
        except Exception as e:
            print(e)

    def connect_to_db(self):
        db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.db)
        cur = db.cursor()
        return cur

    def get_profile_pic(self, user):
        db_connect = self.connect_to_db()
        isert = db_connect.execute("""SELECT FROM * in Models""")
        print(isert)
        db_connect.close()

    def get_all_profile_pic(self):
        db_connect = self.connect_to_db()
        isert = db_connect.execute("""SELECT FROM * in Models""")
        print(isert)
        db_connect.close()

Ai = Ai()
database = Database()

def ig_photo_and_video_scraper(user):
    try:
        os.system("instagram-scraper " + "'"+user+"'" + " --media-metadata --maximum 200 --retry-forever")
        time.sleep(1)
        with open(user + "/" + user + ".json") as json_file:
            data = json.load(json_file)
            for p in tqdm(data['GraphImages']):
                try:
                    display_url = p['display_url']
                    urls = p['urls']
                    is_video = p['is_video']
                    likes = p['edge_media_preview_like']['count']
                    likes = str(likes)
                    display_url = str(display_url)
                    urls = str(urls)
                    urls = urls.replace("['", "")
                    urls = urls.replace("']", "")
                    if is_video == True:
                        print("this is a video")
                        display_url = re.sub(r'(.*?)/', '', urls)
                        display_url = display_url.split("?")
                        display_url = display_url[0]
                        file_path = user + "/" + display_url
                        print(file_path)
                        try:
                            database.post_video(user, urls, likes)
                        except:
                            pass
                except:
                    pass
#
#                    try:
#                        detect = Ai.face_detection_video(file_path)
#                    except:
#                        pass
#                    try:
#                        if not detect:
#                            print("no face detected")
#                            shutil.os.remove(file_path)
#                        elif detect:
#                            print(user)
#                            print(urls)
#                            print(likes)
#                            try:
#                                database.post_video(user, urls, likes)
#                            except Exception as e:
#                                print(e)
#                            shutil.os.remove(file_path)
#                            print("face detected")
#                    except:
#                        pass

                if is_video == False:
                    print("not a video")
                    display_url = re.sub(r'(.*?)/', '', display_url)
                    display_url = display_url.split("?")
                    display_url = display_url[0]
                    file_path = user + "/" + display_url
                    file_path = str(file_path)
                    print(file_path)
                    try:
                        database.post_photo(user, urls, likes)
                    except:
                        pass
#                    try:
#                        detect = Ai.face_detection_photo(file_path)
#                    except:
#                        pass
#                    try:
#                        if not detect:
#                            print("no face detected")
#                            shutil.os.remove(file_path)
#                        elif detect:
#                            print(user)
#                            print(urls)
#                            print(likes)
#                            try:
#                                database.post_photo(user, urls, likes)
#                            except Exception as e:
#                                print(e)
#                            shutil.os.remove(file_path)
#                            print("face detected")
#
#                    except:
#                        pass
#                    print(is_video)
#                    print(likes)
    except Exception as e:
        print(e)
profiles = ["lakerbabes"]

scraper = Scraper()


def start(profile):
    ig_photo_and_video_scraper(profile)
    database.create_profile(profile)


for profile in profiles:
    try:
        user_id = bot.get_user_id_from_username(profile)
        followers = bot.get_user_following(user_id)
        for follower in followers:
            follow_count = scraper.get_ig_followers_count(follower)
            follow_count = int(follow_count)
            time.sleep(2)
            if follow_count > 500:
                print("it's over 10.000")
                print(str(follow_count))
                user = bot.get_username_from_user_id(follower)
                start(user)
            else:
                print("not over 5000")
                print(str(follow_count))
    except Exception as e:
        print(e)
