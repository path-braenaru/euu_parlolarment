#!/usr/bin/env python3

import argparse
import os
import json
import requests


class data_engine:
	def __init__(self, cc, year):
		dirs = ["countries", "parties"]
		for dir in dirs:
			if not os.path.exists(dir):
				os.mkdir(dir)
		self.country = cc
		self.year_vote = year
		self.year_session = year + 5
		self.previous_vote = year - 5
		self.questions = {"turnout": self.turnout, "votes": self.votes}
		try:
			with open('turnout.json','r') as turnout_file:
				self.turnout_data = json.loads(turnout_file.read())
		except:
			print("[+] Fetching turnout data [+]")
			r = requests.get("https://www.election-results.eu/data-sheets/json/turnout.json")
			with open('turnout.json','w+') as turnout_file:
				turnout_file.write(str(r.text))
			self.turnout_data = json.loads(r.text)

		self.current, self.c_parties = self.getdata(self.year_vote, self.year_session, "current")
		self.previous, self.p_parties = self.getdata(self.previous_vote, self.year_vote, "previous")


	def getdata(self, year1, year2, stage):
		try:
			with open('countries/{0}_{1}_{2}.json'.format(self.country, str(year1), str(year2)), 'r') as jsonfile:
				data = json.loads(jsonfile.read())
			with open("parties/{0}_{1}.json".format(str(year1), str(year2)), 'r') as partyfile:
				parties = json.loads(partyfile.read())
		except:
			print("[+] Fetching {0} {1} vote data [+]".format(stage, self.country))
			r = requests.get("https://www.election-results.eu/data-sheets/json/{0}-{1}/election-results/{2}.json".format(
					year1, year2, self.country.lower()))
			if not r.status_code == 200:
				print("\nNo election data for {0}!\n".format(year1))
				exit(0)
			with open('countries/{0}_{1}_{2}.json'.format(self.country, year1, year2), 'w+') as jsonfile:
				jsonfile.write(r.text)
			data = json.loads(r.text)
		try:
			with open("parties/{0}_{1}.json".format(str(year1), str(year2)), 'r') as partyfile:
				eu_parties = json.loads(partyfile.read())
		except:
			print("[+] Fetching {0} parties data [+]".format(stage))
			r = requests.get("https://www.election-results.eu/data-sheets/json/{0}-{1}/election-results/parties.json".format(
				year1, year2))
			with open("parties/{0}_{1}.json".format(str(year1), str(year2)), 'w+') as partyfile:
				partyfile.write(r.text)
			eu_parties = json.loads(r.text)
		parties = {}
		for country in eu_parties["countries"]:
			if country["countryId"] == self.country.upper():
				for party in country["candidates"]:
					parties[party["candidateId"]] = {
						"name": party["candidateLongName"],
						"acronym": party["candidateAcronym"]}
		return data, parties


	def turnout(self):
		report = "\n[+] Turnout stats [+]\n\n"
		cc = self.country.upper()
		for item in self.turnout_data["years"]:
			if item["yearId"] == str(self.year_vote):
				target_year = item["turnoutByYear"]
				break
		try:
			report += "Year: {0}\n\nTotal EU turnout: {1}%\n".format(
				self.year_vote, str(target_year["turnoutEU"]["percent"]))
			for entry in target_year["turnoutByCountry"]:
				if entry["countryId"] == cc:
					report += "Total {0} turnout: {1}%\n".format(
						cc, str(entry["percent"]))
					break
		except:
			report += "No EU election held in {0}!\n".format(self.year_vote)
		print(report)

	def votes(self):
		output = "[+] {0} results [+]\n\n".format(self.country)
		for entry in self.current["partySummary"]["seatsByParty"]:
			self.c_parties[entry["id"]]["result"] = entry["votesPercent"]
		for entry in self.previous["partySummary"]["seatsByParty"]:
			self.p_parties[entry["id"]]["result"] = entry["votesPercent"]
		sortedvals =  sorted(self.c_parties.keys(), key=lambda x: self.c_parties[x]["result"], reverse=True)
		for entry in sortedvals:
			output += "{0}: {1}%".format(
				self.c_parties[entry]["name"], self.c_parties[entry]["result"])
			for old in self.p_parties:
				if self.p_parties[old]["name"] == self.c_parties[entry]["name"]:
					output += " (previous: {0}%, change: ".format(str(self.p_parties[old]["result"]))
					try:
						if self.p_parties[old]["result"] > self.c_parties[entry]["result"]:
							output += "-{0:.2f}%)".format(
								self.p_parties[old]["result"] - self.c_parties[entry]["result"])
						else:
							output += "+{0:.2f}%)".format(
								self.c_parties[entry]["result"] - self.p_parties[entry]["result"])
					except:
						output += "Broken Datatypes)"
					self.p_parties[old]["status"] = "existing"
					break
			output += "\n"
		output += "\n\n[-] {0} parties unlisted (or indexing/naming change) in {1} election (no order) [-]:\n\n".format(
			str(self.previous_vote), str(self.year_vote))
		for entry in self.p_parties:
			try:
				status = self.p_parties[entry]["status"]
			except:
				try:
					output += "{0}: {1}%\n".format(
						self.p_parties[entry]["name"], self.p_parties[entry]["result"])
				except:
					output += "{0}: No data\n".format(
						self.p_parties[entry]["name"])

		print(output)			

def begin(cc, q, year):
	d = data_engine(cc, year)
	if q in d.questions:
		d.questions[q]()
	else:
		print("\nAvailable terms for '-q':\n\t- turnout (default)\n\t- votes")

if __name__ == "__main__":
	a = argparse.ArgumentParser()
	a.add_argument("-c", "--country", default="UK")
	a.add_argument("-q", "--question", default="turnout")
	a.add_argument("-y", "--year", default="2019")
	p = a.parse_args()
	year = int(p.year)
	if not p.question == "turnout":
		if year <=2009:
			if year == 2009:
				print("[WARNING]\n\nPartial data breaks occur for 2009 records (arbitrary schema changes)\n")
			else:
				print("[FATAL]\n\nData from pre-2009 contains mixed schema and breaks tooling! Exiting...\n")
				exit(0)
	begin(p.country, p.question, year)
