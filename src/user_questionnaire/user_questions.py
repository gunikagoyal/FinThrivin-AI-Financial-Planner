questions = {
	"Hi my name Robert. Welcome to FinThrivin. How are you doing?": {"follow-up-questions":["I would like to as you some security questions to identify who you are and better assist you. Can you please give me your first Name?"],
							"store-information":False,
							"decision":False,
							"function_call":None,
              "table_info":[]
              
	},
	"I would like to as you some security questions to identify who you are and better assist you. Can you please give me your first Name?": {"follow-up-questions":["what is your last name?"],
								"store-information":False,
								"decision":False,
								"function_call":"primary",
                "table_info":["user","first_name"]

	},
	"what is your last name?":{"follow-up-questions":["what is your date of birth(enter in mm/dd/yyyy format)"],
								"store-information":False,
								"decision":False,
								"function_call":"primary",
                "table_info":["user","last_name"]

	},
    "what is your date of birth(enter in mm/dd/yyyy format)":{"follow-up-questions":["Thank you,let me verify your information"],
								"store-information":False,
								"decision":False,
								"function_call":"primary",
                "table_info":["user","date_of_birth"]
							},
    "Thank you,let me verify your information":{"follow-up-questions":["seems like you are new user. would you like to spend 10 min in helping me in creating profile?", 
                                                                       "we found your records as per your information.your user id will be displayed on the right side of the page."],
								"store-information":False,
								"decision":True,
								"function_call":"verify_user",
                "table_info":[]
							},
    
	"we found your records as per your information.your user id will be displayed on the right side of the page.":{"follow-up-questions":["Please allow me to check if any missing information in our database."],
								"store-information":False,
								"decision":False,
								"function_call":None,
                "table_info":[]
	},
 "seems like you are new user. would you like to spend 10 min in helping me in creating profile?":{"follow-up-questions":["please wait for a moment,Let me start creating profile for you.","exit"],
								"store-information":False,
								"decision":True,
								"function_call":"sentiment_analysis",
                "table_info":[]
 },
 "please wait for a moment,Let me start creating profile for you.":{"follow-up-questions":["what is your Profession?"],
								"store-information":False,
								"decision":False,
								"function_call":"create_profile",
                "table_info":[]
	},
 "what is your Profession?":{"follow-up-questions":["Do you have any income souce?"],
								"store-information":True,
								"decision":False,
								"function_call":None,
                "table_info":["user","profession"]
 },
 
 
}
