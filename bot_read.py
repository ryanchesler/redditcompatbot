import praw
import os
import bs4 as bs 
import urllib.request
import re
import time
#request sitemap in order to gather pages
req = urllib.request.Request('https://www.itconnected.tech/sitemap.xml', headers={'User-Agent' : "Magic Browser"}) 
con = urllib.request.urlopen(req)
#parse with beautiful soup
soup = bs.BeautifulSoup(con, 'xml')
#create empty dictionary for model numbers and compatibility charts
compatlookup = {}
#check each url in the sitemap
for url in soup.find_all("loc"):
	#reset compatibility chart
	message = ""
	#check if blog
	if "blog" in url.text:
		req = urllib.request.Request(url.text, headers={'User-Agent' : "Magic Browser"}) 
		con = urllib.request.urlopen(req)
		soup = bs.BeautifulSoup(con, 'lxml')
		try:
			#grab title of post and use as dict key
			partnumber = soup.h1.text
			parse = soup.find('div', class_="parsedata")
			parse = parse.text.splitlines()
			
		except:
			print("div class not found")
			continue
		try:
			#put message in markdown to make chart
			message = partnumber + "|" + "Compatibility" + "\n" + "|:-|:-:|" + "\n"
		except:
			continue
		for split in parse:
			category = ""
			data = ""
			if ":" in split:
				split = split.split(":", 1)
				category = split[0]
				data = split[1]
				message = message + category + "|" + data +  "\n"
			#handle data that spills over one line
			else:
				data = split
				if data == "":
					continue
				else:
					try:
						message = message + category+ " (Continued)" + "|" + data +  "\n"
					except:
						print("data could not be appended")
			#assign message to part number in the dict
		compatlookup[partnumber] = message

#check if file present with comments replied to. If not, start one
if not os.path.isfile("comments_replied_to.txt"):
	comments_replied_to = []	
#read comments replied if present
else:
	with open("comments_replied_to.txt", "r") as f:
	   comments_replied_to = f.read()
	   comments_replied_to = comments_replied_to.split("\n")
	   comments_replied_to = list(filter(None, comments_replied_to))
#make reddit request using praw
reddit = praw.Reddit(client_id='K_aWyydKQt1VZw' , 
client_secret='a0B1U3-brxPH8SwOcDodkuVYZFE',
username='ryches',
password='',
user_agent = 'compatibilitybot.1')
subreddit = reddit.subreddit("pythonforengineers")
partnumber = []
#check 5 most recent posts in subreddit
for submission in subreddit.new(limit=5):
	print("Title: ", submission.title)
	print("---------------------------------\n")
	submission.comments.replace_more(limit=0)
	#check all comments from threads
	for comment in submission.comments.list():
		#if comment hasnt already been replied too
		if comment.id not in comments_replied_to:
			#make sure not replying to self and putting in loop
			if comment.author != "ryches":
				#check against each part number parsed from website
				for key in compatlookup:
					lookupwords = key.split()
					#check if any of the comments match keys
					if re.search(lookupwords[-1] + " Compatibility", str(comment.body), re.IGNORECASE):
						print(comment.body)
						#reply to comment with the message of the matched key
						comment.reply(compatlookup[key])
						comments_replied_to.append(comment.id)
						#write the id of the comment matched to prevent double response
						with open("comments_replied_to.txt", "w") as f:
							for comments_id in comments_replied_to:
								f.write(comments_id + "\n")
			
