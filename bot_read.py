import praw
import os
import bs4 as bs 
import urllib.request
import re
import time
req = urllib.request.Request('https://www.itconnected.tech/sitemap.xml', headers={'User-Agent' : "Magic Browser"}) 
con = urllib.request.urlopen(req)
soup = bs.BeautifulSoup(con, 'xml')
compatlookup = {}
for url in soup.find_all("loc"):
	message = ""
	if "blog" in url.text:
		req = urllib.request.Request(url.text, headers={'User-Agent' : "Magic Browser"}) 
		con = urllib.request.urlopen(req)
		soup = bs.BeautifulSoup(con, 'lxml')
		try:
			partnumber = soup.h1.text
			parse = soup.find('div', class_="parsedata")
			parse = parse.text.splitlines()
			
		except:
			print("div class not found")
			continue
		try:
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
			else:
				data = split
				if data == "":
					continue
				else:
					try:
						message = message + category+ " (Continued)" + "|" + data +  "\n"
					except:
						print("data could not be appended")
			print(message)

		compatlookup[partnumber] = message


if not os.path.isfile("comments_replied_to.txt"):
	comments_replied_to = []
else:
	with open("comments_replied_to.txt", "r") as f:
	   comments_replied_to = f.read()
	   comments_replied_to = comments_replied_to.split("\n")
	   comments_replied_to = list(filter(None, comments_replied_to))
reddit = praw.Reddit(client_id='K_aWyydKQt1VZw' , 
client_secret='a0B1U3-brxPH8SwOcDodkuVYZFE',
username='ryches',
password='uY1IFTMv81Cm',
user_agent = 'compatibilitybot.1')
subreddit = reddit.subreddit("pythonforengineers")
partnumber = []
for submission in subreddit.new(limit=5):
	print("Title: ", submission.title)
	print("---------------------------------\n")
	submission.comments.replace_more(limit=0)
	for comment in submission.comments.list():
		if comment.id not in comments_replied_to:
			if comment.author != "ryches":
				for key in compatlookup:
					lookupwords = key.split()
					if re.search(lookupwords[-1], str(comment.body), re.IGNORECASE):
						print(comment.body)
						comment.reply(compatlookup[key])
						comments_replied_to.append(comment.id)
						with open("comments_replied_to.txt", "w") as f:
							for comments_id in comments_replied_to:
								f.write(comments_id + "\n")
			
