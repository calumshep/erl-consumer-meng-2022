#!/usr/bin/python
import spacy
import json
import numpy as np
import rospy
from std_msgs.msg import String, Empty
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.lang.en import English
from hri.srv import SpeechToText
import rospkg

class Spacy_Test:

    def __init__(self):
        rospy.init_node('Spacy_Test')
        self.objectFilePath = rospkg.RosPack().get_path('hri')+"/res/objectFile.json"

    #def get_text(self):
     #   text = "go to the kitchen and get a can of coke for Doctor Kimble"
      #  return text

    def subscribe_jason(self):
        jason_subscriber = rospy.Subscriber('/hri/getGrannyAnnieRequest', String,self.jason_callback)
    
    def jason_callback(self, msg):
        #parse text and execute main code
        self.text = msg.data

        rospy.wait_for_service('speechInput')
        getSpeechInput =rospy.ServiceProxy('speechInput',SpeechToText)

        resp = getSpeechInput()
        print("Received input from service:")
        print(resp.rawText.data)
        self.text = resp.rawText.data
        
        dictMsg={}
        dictMsg["action"]=self.check_action()
        if(self.return_objects() is not None):
            dictMsg["object"]=self.return_objects().text
        if(self.return_rooms() is not None):
            dictMsg["room"]=self.return_rooms().text
        if(self.return_people() is not None):
            dictMsg["person"]=self.return_people().text

        dictWrapper=[dictMsg] #eg. dictWrapper=[dictMsg,dictMsg] for multiple actions
        jsonStr = json.dumps(dictWrapper)
        print(jsonStr)
        output_pub = rospy.Publisher('/hri/cloud_output', String, queue_size=1,latch=True)
        output_pub.publish(jsonStr) #Publish what the component sees for debugging (as there is a delay due to system performance)


    def pub_output(self,msg,args):
        output_pub = rospy.Publisher('/hri/cloud_output', String,self.jason_callback, queue_size=1)
        output_pub.publish(msg) #Publish what the component sees for debugging (as there is a delay due to system performance)


    def string_to_obj(self, string):
        return json.dumps(string)
    
    def obj_to_string(self, obj):
        return json.loads(obj)

    def return_verbs(self):

        nlp = spacy.load("en_core_web_sm")

        print(spacy.__version__)
        doc = nlp(self.text)

        matcher = Matcher(nlp.vocab)
    # Create a pattern matching two tokens: "locate" and a proper noun. This means that the robot knows that it has to complete the 'locate' task and which person to complete the task on
        pattern1 = [{"POS": "VERB"}]
        pattern2 = [{"LEMMA": "be"}]
        pattern3 = [{"LEMMA": "get"}]
        allVerbs = ""
    # Add the pattern to the matcher
        matcher.add("VERBS",[pattern1, pattern2, pattern3])


        for match_id, start, end in matcher(doc):
            allVerbs += (doc[start:end].text)
        return allVerbs

    def get_verbs(self):

        nlp = spacy.load("en_core_web_sm")

        doc = nlp(self.text)

        matcher = Matcher(nlp.vocab)

    # Create a pattern matching two tokens: "locate" and a proper noun. This means that the robot knows that it has to complete the 'locate' task and which person to complete the task on
        pattern1 = [{"POS": "VERB"}]
        pattern2 = [{"LEMMA": "be"}]
        pattern3 = [{"LEMMA": "get"}]

    # Add the pattern to the matcher
        matcher.add("VERBS", None, pattern1, pattern2, pattern3)


        for match_id, start, end in matcher(doc):
            print(doc[start:end].text)
    #print([doc[start:end].text for match_id, start, end in matches])

    def return_rooms(self):

        nlp = spacy.load("en_core_web_sm")

        doc = nlp(self.text)


        rooms = ["kitchen", "bedroom", "bathroom", "hallway", "living room"]
        room_patterns = list(nlp.pipe(rooms))
        roomMatcher = PhraseMatcher(nlp.vocab)
        roomMatcher.add("ROOM", [*room_patterns])

        for match_id, start, end in roomMatcher(doc):
            # Create a Span with the label for "GPE"
            roomSpan = Span(doc, start, end, label="ROOM")
            
            return roomSpan
            


    def return_objects(self):

        nlp = spacy.load("en_core_web_sm")

        doc = nlp(self.text)

        objectJson = open(self.objectFilePath, "r")
        objects = json.loads(objectJson.read())
        object_patterns = list(nlp.pipe(objects))
        objectMatcher = PhraseMatcher(nlp.vocab)
        objectMatcher.add("OBJECTS", [*object_patterns])


        for match_id, start, end in objectMatcher(doc):

            objectSpan = Span(doc, start, end, label="OBJECTS")

            return objectSpan


    def return_people(self):

        nlp = spacy.load("en_core_web_sm")

        doc = nlp(self.text)


        people = ["Doctor Kimble", "Postman", "Deli Man", "Plumber"]
        people_patterns = list(nlp.pipe(people))
        peopleMatcher = PhraseMatcher(nlp.vocab)
        peopleMatcher.add("PEOPLE", [*people_patterns])

        for match_id, start, end in peopleMatcher(doc):

            peopleSpan = Span(doc, start, end, label="PEOPLE")

            return peopleSpan


    def check_action(self):
        if "follow" in self.return_verbs():
            return "follow"
        if (("find" or "get" or "fetch" or "bring" in self.return_verbs()) and (self.return_objects() is not None)):
            return "fetch"
        if (("get" or "guide" in self.return_verbs()) and (self.return_people() is not None)):
            return "guide"

spacy_test = Spacy_Test()
spacy_test.subscribe_jason()
rospy.spin()