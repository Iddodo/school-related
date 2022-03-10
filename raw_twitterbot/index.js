const cron = require('node-cron');
const Twitter = require('./simple-twitter-parser');
const jsonfile = require('jsonfile');
const axios = require('axios');
const TelegramBotURL = 'https://api.telegram.org/botXXXX:XXXX/sendMessage';
// ----
const JSONFilename = 'twitter-profiles.json';
// do promises


function HandleLastStatus(statusID, profileName) {
	let profilesLastTweet = jsonfile.readFileSync(JSONFilename);
	if (profilesLastTweet[profileName] != statusID) {
		profilesLastTweet[profileName] = statusID;
		console.log('New status found for ' + profileName + ': ' + statusID);
		axios.post(TelegramBotURL, {
			chat_id: '-XXXX',
			text: Twitter.URLFormats.Status(profileName, statusID)
		});
		jsonfile.writeFileSync(JSONFilename, profilesLastTweet);
	}
}

function FindNewStatuses() {
	jsonfile.readFile(JSONFilename, (err, profiles) => {
		for (var pr in profiles) {
			let profile = new Twitter.TwitterProfileParser(Twitter.URLFormats.Profile(pr));
			profile.GetLatest(HandleLastStatus);
		}
	});
}

FindNewStatuses();
cron.schedule('*/2 * * * *', FindNewStatuses);
// ----
