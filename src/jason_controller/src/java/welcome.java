import jason.asSyntax.*;
import jason.environment.*;

import java.util.logging.*;
import ros.Publisher;
import ros.RosBridge;
import ros.RosListenDelegate;
import ros.SubscriptionRequestMsg;
import ros.msgs.std_msgs.PrimitiveMsg;
import ros.tools.MessageUnpacker;
import com.fasterxml.jackson.databind.JsonNode;

import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import javax.json.*;
import java.io.StringReader;
import java.util.StringTokenizer;

public class welcome extends Environment {

    public static Visitor visitor = Visitor.NULL;
    public static Rooms plumberDesiredRoom = Rooms.NULL;
    private static Boolean doorbellSounded = false;

    public static enum Visitor {
        DR_KIMBLE, POSTMAN, DELIMAN, PLUMBER, UNKNOWN, NULL
    };

    private static enum Rooms {
        KITCHEN, BATHROOM, NULL
    };

    // Asynchronous subscriber that will allow code to continue. The belief is
    // directly updated in the callback function to deal with the asynchronous
    // nature.
    public void isDoorbellRingingASync() {
        AtomicReference<Boolean> status = new AtomicReference<>(false);
        bdiEnvironment.bridge.subscribe(SubscriptionRequestMsg.generate("/doorbell").setType("std_msgs/Bool")
                .setThrottleRate(1).setQueueLength(1), new RosListenDelegate() {

                    public void receive(JsonNode data, String stringRep) {
                        MessageUnpacker<PrimitiveMsg<String>> unpacker = new MessageUnpacker<PrimitiveMsg<String>>(
                                PrimitiveMsg.class);
                        PrimitiveMsg<String> msg = unpacker.unpackRosMessage(data);
                        if ((data.get("msg").get("data").asInt() > 0) ? true : false) {
                            addPercept(Literal.parseLiteral("doorbellSounded"));
                            bdiEnvironment.logger.info("Doorbell sounded");
                        }
                    }
                });
    }

    public static void waitForBell() {
        bdiEnvironment.logger.info("Waiting for doorbell...");
        String rawStatus = bdiEnvironment.subscribeSync("/jason/welcome/doorbell", "std_msgs/Bool");
        doorbellSounded = rawStatus == "true" ? true : false;
    }

    public static void scanFace() {
        
        bdiEnvironment.logger.info("Scanning face");
		bdiEnvironment.publish("/jason/detect_face", "std_msgs/String", "");
		String resp = bdiEnvironment.subscribeSync("/cv/face/personIs", "std_msgs/String");
        
        switch (resp) {
            case "simulated":
                visitor=Visitor.DR_KIMBLE;
                bdiEnvironment.say("Hello Doctor Kimble");
                break;
            case "postman":
                visitor=Visitor.POSTMAN;
                bdiEnvironment.say("Hello Postman");
                break;
            default:
                visitor=visitor.UNKNOWN;
                break;
        }
        

        bdiEnvironment.logger.info("Face scan returned " + visitor.toString().toLowerCase());
    }

    public static void interrogate() {
        bdiEnvironment.logger.info("Interrogating to determine if Deliman or Plumber...");
        bdiEnvironment.say("Sorry, I don't know you. Who are you?");
        bdiEnvironment.publish("/hri/greet_input","std_msgs/String","");
        String resp = bdiEnvironment.subscribeSync("/hri/greet_output","std_msgs/String");
        System.out.println(resp);
        switch (resp.toLowerCase()) {
            case "deli man":
                visitor=Visitor.DELIMAN;
                break;
            case "plumber":
                visitor=Visitor.PLUMBER;
                break;
            case "doctor kimble":
                visitor=Visitor.DR_KIMBLE;
                break;
            case "postman":
                visitor=Visitor.POSTMAN;
                break;
            default:
                visitor=visitor.UNKNOWN;
                break;
        }        // Publish to HRI stack
        // Sync Subscriber to await response.
        System.out.println(visitor);
    }

    public static void waitUntilVisitorDone() {
        bdiEnvironment.logger.info("Waiting until visitor is done...");
        bdiEnvironment.subscribeSync("/jason/welcome/visitorDone", "std_msgs/Bool");
        bdiEnvironment.logger.info("Visitor is done");
    }

    public static void waitUntilVisitorLeft() {
        bdiEnvironment.logger.info("Waiting until visitor has left..");
        //bdiEnvironment.subscribeSync("/jason/welcome/visitorLeft", "std_msgs/Bool");
        bdiEnvironment.logger.info("Visitor has left");
    }

    public static void acceptMail() {
        bdiEnvironment.logger.info("Accepting mail from postman.");
    }

    public static void deliverMail() {
        bdiEnvironment.logger.info("Giving Granny Annie the mail.");
    }

    public static void complain() {
        bdiEnvironment.logger.info("Visitor out of bounds, complaining!");
    }

    public static void askToLeaveBreakfast() {
        bdiEnvironment.logger.info("Asking deliman to leave breakfast");
    }

    public static void askPlumberDesiredRoom() {

        bdiEnvironment.logger.info("Asking plumber where he wants to visit");
        bdiEnvironment.say("Hello Plumber, can you please tell me where you would like to visit? I am only permitted to let you access the the kitchen or bathroom.");

        bdiEnvironment.publish("/hri/location_input", "std_msgs/String", "");
        String desiredRoom = bdiEnvironment.subscribeSync("/hri/location_output", "std_msgs/String");



        switch (desiredRoom.toLowerCase()) {
            case "kitchen":
                plumberDesiredRoom = Rooms.KITCHEN;
                break;
            case "bathroom":
                plumberDesiredRoom = Rooms.BATHROOM;
                break;
            default:
                break;
        }        // Publish to HRI stack

        bdiEnvironment.logger.info(plumberDesiredRoom.toString());

    }

    public static LinkedList<Literal> getWelcomeHomePercepts() {

        LinkedList<Literal> percepts = new LinkedList<Literal>();
        if (visitor != Visitor.NULL) {
            percepts.add(Literal.parseLiteral("personIs(" + visitor.toString().toLowerCase() + ")"));
        }
        if (doorbellSounded) {
            percepts.add(Literal.parseLiteral("doorbellSounded"));
        }
        if (plumberDesiredRoom != Rooms.NULL) {
            percepts.add(
                    Literal.parseLiteral("plumberDesiredRoomIs(" + plumberDesiredRoom.toString().toLowerCase() + ")"));
        }

        return percepts;
    }
}
