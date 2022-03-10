const cheerio = require('cheerio');
const request = require('request');
var regexes = {
	twitterProfileAddress: /^https?:\/\/twitter.com\/(\w{1,15})\/?$/i,
	twitterStatusAddress: /^https?:\/\/twitter.com\/(\w{1,15})\/status\/(\d{18})\/?$/
};

var URLFormats = {
	Status: (profileName, statusID) => {
		return 'https://twitter.com/' + profileName + '/status/' + statusID;
	},
	Profile: (profileName) => {
		return "https://twitter.com/" + profileName;
	}
};
function TwitterProfileParser(url) {
	let regexResult = url.match(regexes.twitterProfileAddress);
	if (!regexResult) {
		return false; // trigger error later
	}
	this.Name = regexResult[1];
	this.URL = url;
	this.GetLatest = function(callback) {
		request(url, (error, response, rawHTML) => {
			if (error) {
				console.log("Error: ", error);
				return false; // trigger error leater
			}
			let $ = cheerio.load(rawHTML);
			callback($('.ProfileTimeline > .stream-container').attr('data-max-position'), this.Name);
		});
	};
	return false; // just in case
}

function TwitterStatusParser(profileName, statusID) {
	if ((profileName == null || statusID == null) || ((profileName == '' || profileName > 16) || (isNaN(statusID)))) {
		return false;
	}
	this.profileName = profileName;
	this.ID = statusID;
	this.URL = URLFormats.Status(profileName, statusID);
	this.GetTweetData = function(callback) {
		request(this.URL, (error, response, rawHTML) => {
			if (error) {
				console.log("Error: ", error);
				return false;
			}
			let $ = cheerio.load(rawHTML);
			callback({
				message: $('.js-tweet-text-container > p').html().replace(/<\/?[^>]+(>|$)/g, ""),
				date: (() => {
					let rawDate = $('.client-and-actions > span > span').html();
					let seperate = rawDate.split(' - ');
					let time = seperate[0];
					let rawHour = time.length - 3 == 4 ? time[0] : time.slice(0, 2);
					let minutes = time.slice(-5, -3);
					let ampm = time.slice(-2);
					return new Date(seperate[1] + ' ' + [ampm == 'AM' ? rawHour : (rawHour == '12' ? '00' : parseInt(rawHour) + 12), minutes].join(':'));
				})()
			});
		});
	};
	return this;
}

/*var profile = new TwitterProfileParser('https://twitter.com/MacroScope17');
profile.GetLatest(function(id) {
	let latest = new TwitterStatusParser(profile.Name, id);
	console.log(latest);
	latest.GetTweetData(function(data) {
		console.log(data); // QuoteTweet-innerContainer for quotes
	});
});*/

module.exports = { 
	TwitterProfileParser: TwitterProfileParser,
	URLFormats: URLFormats
};