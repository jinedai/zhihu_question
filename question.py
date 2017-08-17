#LAST_VISITcoding=utf-8
import MySQLdb
from bs4 import BeautifulSoup
import json
import re
import time
from math import ceil
import logging
import threading
import Queue
import ConfigParser

from util import get_content


class UpdateOneQuestion(threading.Thread):
    def __init__(self,queue):
        self.queue = queue
        threading.Thread.__init__(self)

        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        
        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
        
    def run(self):
        while not self.queue.empty():
            parameters = self.queue.get()
            link_id = parameters[0]
            count_id = parameters[1]
            self.update(link_id,count_id)
            print "link_id: " + str(link_id) + "     count_id: " + str(count_id)
            time.sleep(10)

    def update(self,link_id,count_id):
        print "it go"
        time_now = int(time.time())
        questionUrl = 'http://www.zhihu.com/question/' + link_id

        content = get_content(questionUrl,count_id)
        if content == "FAIL":
            sql = "UPDATE QUESTION SET LAST_VISIT = %s WHERE LINK_ID = %s"
            self.cursor.execute(sql,(time_now,link_id))
            return

        soup = BeautifulSoup(content, 'lxml')

        questions = soup.find('div',attrs={'class':'NumberBoard-value'})

        # Find out how many people focus this question.
        if questions == None:
            return
        else:
            focus_amount = questions.get_text()

        print "focus_amount: " + str(focus_amount)

        # Find out how many people answered this question.
        answer_amount = soup.find('h4',attrs={'class':'List-headerText'})
        if answer_amount != None:
            answer_amount = answer_amount.find('span').get_text().replace(u' 个回答','')
        else:
            answer_amount = u'0'

        print "answer_amount: " + str(answer_amount)

        # Find out the top answer's vote amount.
        top_answer = soup.findAll('span',attrs={'class':'Voters'})
        if top_answer == []:
            top_answer_votes = 0
        else:
            top_answer_votes = 0
            for t in top_answer:
                t = t.find('button').get_text()
                t = t.replace(u' 人赞同了该回答','')
                t = t.replace('K','000')
                t = int(t)
                if t > top_answer_votes:
                    top_answer_votes = t

        # print it to check if everything is good.
        if count_id % 1 == 0:
            print str(count_id) + " , " + self.getName() + " Update QUESTION set FOCUS = " + focus_amount + " , ANSWER = " + answer_amount + ", LAST_VISIT = " + str(time_now) + ", TOP_ANSWER_NUMBER = " + str(top_answer_votes) + " where LINK_ID = " + link_id
        #print str(count_id) + " , " + self.getName() + " Update QUESTION set FOCUS = " + focus_amount + " , ANSWER = " + answer_amount + ", LAST_VISIT = " + str(time_now) + ", TOP_ANSWER_NUMBER = " + str(top_answer_votes) + " where LINK_ID = " + link_id
        
        # Update this question
        sql = "UPDATE QUESTION SET FOCUS = %s , ANSWER = %s, LAST_VISIT = %s, TOP_ANSWER_NUMBER = %s WHERE LINK_ID = %s"
        self.cursor.execute(sql,(focus_amount,answer_amount,time_now,top_answer_votes,link_id))

        # Find out the topics related to this question
        topics = soup.findAll('a',attrs={'class':'zm-item-tag'})
        if questions != None:
            sql_str = "INSERT IGNORE INTO TOPIC (NAME, LAST_VISIT, LINK_ID, ADD_TIME) VALUES (%s, %s, %s, %s)"
            topicList = []
            for topic in topics:
                topicName = topic.get_text().replace('\n','')
                topicUrl = topic.get('href').replace('/topic/','')
                #sql_str = sql_str + "('" + topicName + "',0," + topicUrl + "," + str(time_now) + "),"
                topicList = topicList + [(topicName, 0, topicUrl, time_now)]
            
            self.cursor.executemany(sql_str,topicList)


class UpdateQuestions:
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        
        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.question_thread_amount = int(cf.get("question_thread_amount","question_thread_amount"))

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()

    def run(self):
        queue = Queue.Queue()
        threads = []

        time_now = int(time.time())
#        before_last_visit_time = time_now - 12*3600
#        after_add_time = time_now - 24*3600*14

#        sql = "SELECT LINK_ID from QUESTION WHERE LAST_VISIT < %s AND ADD_TIME > %s AND ANSWER < 50 AND TOP_ANSWER_NUMBER < 50 ORDER BY LAST_VISIT"
        sql = "SELECT LINK_ID from QUESTION WHERE FOCUS = 0 AND ANSWER = 0 ORDER BY LAST_VISIT"
#        self.cursor.execute(sql,(before_last_visit_time,after_add_time))
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        
        i = 0
        
        for row in results:
            link_id = str(row[0])

            queue.put([link_id, i])
            i = i + 1

        thread_amount = self.question_thread_amount

        for i in range(thread_amount):
            threads.append(UpdateOneQuestion(queue))

        for i in range(thread_amount):
            threads[i].start()

        for i in range(thread_amount):
            threads[i].join()

        self.db.close()

        print 'All task done'


if __name__ == '__main__':
    question_spider = UpdateQuestions()
    question_spider.run()
