
import requests, bs4, json
import sys
import threading
from multiprocessing import cpu_count

document=__file__+".json"
continue_parse=False
url = "https://habr.com/post/"
BeautifulSoup = bs4.BeautifulSoup(requests.get("https://habr.com/all/").text, "html.parser")

# Here we are gettting first ".post__title a" href(BeautifulSoup.select(".post__title a")[0]["href"]), then getting last_post_num(str(..).split("/")[-2])
last_post_num = int(str(BeautifulSoup.select(".post__title a")[0]["href"]).split("/")[-2])
print("Total Posts: ", last_post_num)
# getting num of posts for every thread
pages_for_threads = []
posts_for_thread = int(round(last_post_num/(cpu_count()* 2) ))
z = 1
# making list of range of posts num
for a in range(cpu_count()*2):
    pages_for_threads += [[z, z+posts_for_thread-1]]
    z += posts_for_thread
print("Range of pages for every thread ", pages_for_threads)


class SummingThread(threading.Thread):
     def __init__(self,min,max, name):
         super(SummingThread, self).__init__()
         self.min=min
         self.name=name
         self.max=max
         self.bytes=0
         self.parsed_pages=0
         self.num=0

     def run(self):

       for self.num in range(self.min,self.max):

         try:

             self.parsed_pages+=1
             total_parsed_pages=sum(c.parsed_pages for c in threads)
             # saving parse_data  to continue next time
             with open(document,"w") as w:
                parse_data=[ i.num for i in threads]
                w.write(json.dumps({"data":parse_data,"parsp":total_parsed_pages,"continue":True}))

             BeautifulSoup = bs4.BeautifulSoup(requests.get(url + str(self.num),timeout=30).text, "html.parser")
             post_text = BeautifulSoup.select(".post__text")

             try:
                 self.bytes += sys.getsizeof(post_text[0].text)

             except IndexError:
                pass
             # to print information only from one thread
             if self.name == "thread1":
                 print("Pages completed: %s from %s" % (total_parsed_pages, last_post_num))
                 print(" TOTAl SIZE=", sum(c.bytes for c in threads))
         except:
            pass

       return self.bytes
try:
 with open(document, "r") as r:
        data = json.load(r)
        if data["continue"]:
            print("You have unfinished parsing. Continue?(y/n)")
            p=input()
            if p=="y":
                continue_parse=True
            else:
                continue_parse=False

except FileNotFoundError:
    continue_parse=False

threads=[]

if not continue_parse:

    for i in range(cpu_count()*2):
      thread=SummingThread(pages_for_threads[i][0],pages_for_threads[i][1],"thread"+str(i))
      threads.append(thread)

else:

    with open(document,"r") as r:
     data=json.load(r)
    for i in range(cpu_count() * 2):
        threads.append(SummingThread(data["data"][0], pages_for_threads[i][1], "thread"+str(i)))
    # adding num of parsed pages last time
    threads[0].parsed_pages = data["parsp"]


for thread in threads:thread.start()
for thread in threads:thread.join()
# At this point, both threads have completed

result=0
for thread in threads: result+=thread.bytes
print (result)
