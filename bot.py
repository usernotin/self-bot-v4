import discord
import asyncio
import random
import os
import gc
import aiohttp
import psutil
import json
from datetime import datetime, timezone, timedelta
from threading import Thread
import time as time_module
from io import BytesIO
from flask import Flask
import logging

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- KEEPALIVE SERVER (for Railway) ---
app = Flask('')
@app.route('/')
def home():
    return "REX QTY CORE ACTIVE"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- TOKENS FROM ENVIRONMENT ---
TOKENS = os.environ.get("TOKENS", "").split(",")
TOKENS = [t.strip() for t in TOKENS if t.strip() and "TOKEN" not in t]

if not TOKENS:
    try:
        with open("tokens.json", "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                TOKENS = [t for t in data if t and "TOKEN" not in t]
    except:
        pass

if not TOKENS:
    logger.error("⚠ No tokens found! Set TOKENS environment variable.")
    logger.error("Format: TOKENS=token1,token2,token3")

SUDO_USERS = [1442911002130907146]  # Your user ID
PREFIX = "!"

# --- PERSISTENCE FILES ---
TOKENS_FILE = "tokens.json"
PROFILES_FILE = "profiles.json"

def load_json(filename, default=None):
    if default is None:
        default = {}
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def save_tokens(tokens):
    save_json(TOKENS_FILE, tokens)

def load_profiles():
    return load_json(PROFILES_FILE, default={"original": {}, "saved": {}})

def save_profiles(profiles):
    save_json(PROFILES_FILE, profiles)

# --- SWIPE LISTS ---
LONGSWIPE_LINES = [
    "Teri kutia ma ki tang kaat ke usse danda banaunga fir ussi danda se teri ma ki chut mein daal dunga itni zor se uska pet phat jayega 🤣🤸🏿‍♀️",
    "Teri ma ki zubaan kaat ke usse strap banaunga fir ussi strap se teri ma ki chut band kar dunga 🧤",
    "Teri bhn ki cut mein tezaab daalunga fir woh tezaab andar hi andar uski phudi ko jala dunga itna ki uski chekhein sunke tery ma mrjgy",
    "Teri ma ki maa ko bhi nahi codunga uski bhi cut phaad ke usse rassi banaunga fir ussi rassi se teri rndi behen ka bsdm krdunga",
    "Teri ma ki fuddi ka gosht kaat kaat ke usse kabab banaunga fir woh kabab tere baap ko khilaaunga aur tu bhi khayega nhi khayega toh tere mu pr mukke marke khilaunga 🤪🥊",
    "teri ma co presure cooker me daal ke usse soup bnaunga fir whi soup tere baap co pilunga cutiye ny pieyaga to muh tod ke ghusaunga",
    "teri ma ke daant tod ke usse necklace banaunga fir wohi necklace teri ma ke gale me daal ke usse ghot dunga us kaly rndy ki",
    "teri kutia ma ki dono aankh nikal ce usse banta sode me ghusake bechdunga fir ussi goli se tmkc pe nisane marunga",
    "tery rndi ma ki gardan me mukke marke marod dunga usse ghumaunga fir ghuma ghuma ke patak dunga rndyce",
    "tery ma ki bahein tod ke usse hockey stick banaunga fir ussi stick se teri ma ko ek haath se hockey khilaunga dusre haat se lun pkdaunga",
    "teri ma ki tang tod ke usse cricket bat banaunga fir ussi bat se teri ma ki cut fod dunga",
    "tery ma ki cut me bhar bhar ke danda daalunga fir usse kheench ke bahar nikalunga itni zor se uski aatein bahar aa jayengi rndyki",
    "tery ma ki naak kaat ke usse whistle bana ke bajau aur usko laat marke pichka du rndyce",
    "teri rndi ma ka bosda cheer kr usse bag bnake rakhunga",
    "teri ma ki jibh kheech kr usse jump rope khelu rndyk bcche 🤸🏿‍♀️🛹",
    "teri ma ki ungli todkr usse ludo khelenge smjha rndyk",
    "teri kutiya ma ke baal pkd ke diwar pr marunga fir uski jeeb se flood pr poncha lagwaunga",
    "teri v ma ky bosdi bahar aa teri ma ke tange cheer dunga andr tk teri ma saaans ny le payegi",
    "Tu peda he loda chusne ke liye hua he baki chizo me obv imperfect hoga",
    "teri ma ke cut pe lagake antina teri bhen ke bhosde pe karenge taki uski chudai ka live pradarshan apni niche wale kale hoto se dekh paye",
    "teri ma ki cut locked🔒please enter password to continue",
    "Teri ma ko codu ghachar ghachar 🙏🏼🤣🗿",
    "Teri maa chudte time roti h aur ghr Jake soti h😂🩷🔥",
    "rndike bche jis bosde se nikla h usi me ghusa kr pack krdunga"
]

TERISWIPE_LINES = [
    "Teri ma randi","Teri ma kutti","Teri ma rakhel","Teri ma chinar","Teri ma hathi","Teri ma plate","Teri ma Oyo",
    "Teri ma Japan","Teri ma acid","Teri ma battery","Teri ma chaddar","Teri ma tawa","Teri ma kettle","Teri ma helicopter",
    "Teri ma missile","Teri ma rocket","Teri ma bullet","Teri ma cycle","Teri ma rikshaw","Teri ma auto","Teri ma train",
    "Teri ma plane","Teri ma ship","Teri ma submarine","Teri ma tank","Teri ma gun","Teri ma bomb","Teri ma knife",
    "Teri ma sword","Teri ma axe","Teri ma hammer","Teri ma screwdriver","Teri ma pliers","Teri ma needle","Teri ma thread",
    "Teri ma button","Teri ma zipper","Teri ma shoe","Teri ma sock","Teri ma cap","Teri ma jacket","Teri ma jeans",
    "Teri ma shirt","Teri ma tie","Teri ma belt","Teri ma watch","Teri ma ring","Teri ma chain","Teri ma bangle",
    "Teri ma earring","Teri ma nose pin","Teri ma anklet","Teri ma comb","Teri ma brush","Teri ma soap","Teri ma shampoo",
    "Teri ma conditioner","Teri ma lotion","Teri ma cream","Teri ma powder","Teri ma kajal","Teri ma mascara",
    "Teri ma eyeliner","Teri ma lip balm","Teri ma nail polish","Teri ma mehndi","Teri ma sindoor","Teri ma bindi",
    "Teri ma dupatta","Teri ma ghagra","Teri ma lehenga","Teri ma saree","Teri ma salwar","Teri ma kameez","Teri ma burqa",
    "Teri ma hijab","Teri ma turban","Teri ma crown","Teri ma tiara","Teri ma goggles","Teri ma umbrella","Teri ma ladder",
    "Teri ma rope","Teri ma lock","Teri ma key","Teri ma door","Teri ma window","Teri ma roof","Teri ma wall","Teri ma floor",
    "Teri ma stairs","Teri ma lift","Teri ma escalator","Teri ma slide","Teri ma swing","Teri ma see saw",
    "Teri ma merry go round","Teri ma roller coaster","Teri ma Ferris wheel","Teri ma bumper car","Teri ma water slide",
    "Teri ma trampoline","Teri ma tyre","Teri ma tube","Teri ma pipe","Teri ma tap","Teri ma bucket","Teri ma mug",
    "Teri ma glass","Teri ma cup","Teri ma plate","Teri ma bowl","Teri ma spoon","Teri ma fork","Teri ma knife",
    "Teri ma chopper","Teri ma grinder","Teri ma mixer","Teri ma oven","Teri ma microwave","Teri ma toaster",
    "Teri ma sandwich maker","Teri ma juicer","Teri ma blender","Teri ma pan","Teri ma kadhai","Teri ma pressure cooker",
    "Teri ma steamer","Teri ma strainer","Teri ma rolling pin","Teri ma spatula","Teri ma ladle","Teri ma whisk",
    "Teri masala dabba","Teri ma fridge","Teri ma freezer","Teri ma dishwasher","Teri ma washing machine",
    "Teri ma dryer","Teri ma iron","Teri ma vacuum cleaner","Teri ma broom","Teri ma mop","Teri ma dustpan",
    "Teri ma garbage bag","Teri ma dustbin","Teri ma toilet","Teri ma shower","Teri ma bathtub","Teri ma sink",
    "Teri ma basin","Teri ma mirror","Teri ma towel","Teri ma toothbrush","Teri ma toothpaste","Teri ma floss",
    "Teri ma mouthwash","Teri ma nail cutter","Teri ma tweezer","Teri ma razor","Teri ma trimmer","Teri ma hair dryer",
    "Teri ma straightener","Teri ma curler","Teri ma hair band","Teri ma hair clip","Teri ma hair pin","Teri ma hair tie",
    "Teri ma comb","Teri ma brush","Teri ma shampoo","Teri ma conditioner","Teri ma soap","Teri ma body wash",
    "Teri ma scrub","Teri ma mask","Teri ma sunscreen","Teri ma moisturizer","Teri ma serum","Teri ma toner",
    "Teri ma face wash","Teri ma face pack","Teri ma scrubber","Teri ma loofah","Teri ma sponge","Teri ma cloth",
    "Teri ma napkin","Teri ma tissue","Teri ma paper","Teri ma pen","Teri ma pencil","Teri ma eraser","Teri ma sharpener",
    "Teri ma ruler","Teri ma compass","Teri ma protractor","Teri ma geometry box","Teri ma notebook","Teri ma diary",
    "Teri ma calendar","Teri ma clock","Teri ma timer","Teri ma stopwatch","Teri ma thermometer","Teri ma weighing scale",
    "Teri ma measuring tape","Teri ma scissors","Teri ma stapler","Teri ma punch machine","Teri ma hole puncher",
    "Teri ma binder","Teri ma folder","Teri ma envelope","Teri ma stamp","Teri ma glue","Teri ma tape","Teri ma thread",
    "Teri ma needle","Teri ma thimble","Teri ma button","Teri ma zipper","Teri ma hook","Teri ma Velcro","Teri ma elastic",
    "Teri ma lace","Teri ma ribbon","Teri ma string","Teri ma rope","Teri ma cable","Teri ma wire","Teri ma plug",
    "Teri ma socket","Teri ma switch","Teri ma bulb","Teri ma tube light","Teri ma LED","Teri ma fan","Teri ma cooler",
    "Teri ma AC","Teri ma heater","Teri ma geyser","Teri ma motor","Teri ma pump","Teri ma filter","Teri ma purifier",
    "Teri ma tap","Teri ma nozzle","Teri ma hose","Teri ma pipe","Teri ma gutter","Teri ma drain","Teri ma manhole",
    "Teri ma speed breaker","Teri ma traffic light","Teri ma parking meter","Teri ma toll booth","Teri ma ticket machine",
    "Teri ma escalator","Teri ma elevator","Teri ma crane","Teri ma bulldozer","Teri ma excavator","Teri ma tractor",
    "Teri ma harvester","Teri ma thresher","Teri ma plough","Teri ma hoe","Teri ma sickle","Teri ma axe","Teri ma saw",
    "Teri ma chainsaw","Teri ma drill","Teri ma grinder","Teri ma sander","Teri ma polisher","Teri ma buffer",
    "Teri ma sprayer","Teri ma blower","Teri ma heater","Teri ma boiler","Teri ma generator","Teri ma transformer",
    "Teri ma battery","Teri ma solar panel","Teri ma windmill","Teri ma dam","Teri ma canal","Teri ma bridge",
    "Teri ma tunnel","Teri ma flyover","Teri ma roundabout","Teri ma streetlight","Teri ma billboard","Teri ma kachra",
    "Teri ma kooda","Teri ma bakwas","Teri ma bekaar","Teri ma zero","Teri ma khali","Teri ma bhuki","Teri ma nangi",
    "Teri ma beghairat","Teri ma chudail","Teri ma daayan","Teri ma khabis","Teri ma laanat","Teri ma dhokebaaz",
    "Teri ma jhoothi","Teri ma thagi","Teri ma gandi","Teri ma maili","Teri ma fitrat","Teri ma aadat","Teri ma shakal",
    "Teri ma soorat","Teri ma haddi","Teri ma chamdi","Teri ma khoon","Teri ma murgi","Teri ma billi","Teri ma bhains",
    "Teri ma gadhi","Teri ma suwar","Teri ma kachra","Teri ma kooda","Teri ma bakwas","Teri ma faltu","Teri ma zero",
    "Teri ma khaali","Teri ma bekaar","Teri ma nikammi","Teri ma aawara","Teri ma lanti","Teri ma patli","Teri ma moti",
    "teri ma fridge","teri ma wifi","teri ma charger","teri ma swimming pool","teri ma merry go round","tri ma torch",
    "teri ma popcorn","teri ma map"
]

TMKCSWIPE_LINES = [
    "tmkc me piano","tmkc me giant hamla krenge","tmkc me hockey","tmkc me mukke","tmkc me laat du","tmkc me chair",
    "tmkc pe aalu","tmkc me guitar","tmkc me trumpet","tmkc me dhol","tmkc me tabla","tmkc me violin","tmkc me flute",
    "tmkc me saxophone","tmkc me drum set","tmkc me microphone","tmkc me speaker","tmkc me amplifier","tmkc me headphone",
    "tmkc me usb cable","tmkc me charger","tmkc me laptop","tmkc me keyboard","tmkc me mouse","tmkc me monitor",
    "tmkc me printer","tmkc me scanner","tmkc me projector","tmkc me camera","tmkc me tripod","tmkc me drone",
    "tmkc me remote","tmkc me antenna","tmkc me radar","tmkc me satellite","tmkc me telescope","tmkc me microscope",
    "tmkc me stethoscope","tmkc me thermometer","tmkc me barometer","tmkc me speedometer","tmkc me odometer",
    "tmkc me compass box","tmkc me chalk","tmkc me duster","tmkc me whiteboard","tmkc me blackboard","tmkc me pointer",
    "tmkc me glue stick","tmkc me sketch pen","tmkc me highlighter","tmkc me marker","tmkc me crayon","tmkc me paint brush",
    "tmkc me canvas","tmkc me easel","tmkc me palette","tmkc me clay","tmkc me pottery wheel","tmkc me kiln",
    "tmkc me welding machine","tmkc me blowtorch","tmkc me fire extinguisher","tmkc me smoke detector","tmkc me cctv",
    "tmkc me alarm system","tmkc me keypad","tmkc me fingerprint scanner","tmkc me biometric machine","tmkc me turnstile",
    "tmkc me gate","tmkc me fence","tmkc me barbed wire","tmkc me security camera","tmkc me spotlight","tmkc me flash light",
    "tmkc me torch","tmkc me lantern","tmkc me candle","tmkc me matchstick","tmkc me lighter","tmkc me gas stove",
    "tmkc me induction","tmkc me chimney","tmkc me exhaust fan","tmkc me water purifier","tmkc me water tank",
    "tmkc me water pump","tmkc me sprinkler","tmkc me watering can","tmkc me gardening shovel","tmkc me pruning shears",
    "tmkc me lawn mower","tmkc me hedge trimmer","tmkc me leaf blower","tmkc me snow shovel","tmkc me ice scraper",
    "tmkc me snow blower","tmkc me generator","tmkc me extension cord","tmkc me voltage stabilizer","tmkc me inverter",
    "tmkc me ups","tmkc me surge protector","tmkc me fuse","tmkc me circuit breaker","tmkc me panel board",
    "tmkc me meter box","tmkc me solar panel","tmkc me wind turbine","tmkc me water wheel","tmkc me steam engine",
    "tmkc me pulley","tmkc me lever","tmkc me wedge","tmkc me inclined plane","tmkc me wheel and axle","tmkc me gear",
    "tmkc me chain","tmkc me belt","tmkc me bearing","tmkc me motor","tmkc me engine","tmkc me carburetor","tmkc me piston",
    "tmkc me cylinder","tmkc me valve","tmkc me spring","tmkc me nut","tmkc me bolt","tmkc me washer","tmkc me screw",
    "tmkc me nail","tmkc me rivet","tmkc me dowel","tmkc me peg","tmkc me rod","tmkc me pipe cleaner","tmkc me plunger",
    "tmkc me snake","tmkc me mop","tmkc me sponge","tmkc me scrub","tmkc me broom","tmkc me dustpan","tmkc me vacuum cleaner",
    "tmkc me carpet cleaner","tmkc me upholstery cleaner","tmkc me stain remover","tmkc me bleach","tmkc me disinfectant",
    "tmkc me sanitizer","tmkc me soap dispenser","tmkc me paper towel","tmkc me toilet paper","tmkc me sanitary pad",
    "tmkc me diaper","tmkc me baby powder","tmkc me diaper rash cream","tmkc me baby oil","tmkc me baby lotion",
    "tmkc me baby soap","tmkc me feeding bottle","tmkc me pacifier","tmkc me teether","tmkc me bib","tmkc me stroller",
    "tmkc me cradle","tmkc me crib","tmkc me bouncer","tmkc me high chair","tmkc me playpen","tmkc me toy","tmkc me ball",
    "tmkc me bat","tmkc me wicket","tmkc me stumps","tmkc me boundary rope","tmkc me helmet","tmkc me pads","tmkc me gloves",
    "tmkc me thigh guard","tmkc me arm guard","tmkc me abdomen guard","tmkc me cricket bag","tmkc me foot pump",
    "tmkc me whistle","tmkc me stopwatch","tmkc me scoreboard","tmkc me pitch roller","tmkc me sight screen",
    "tmkc me trampoline","tmkc me climbing rope","tmkc me karate belt","tmkc me boxing bag","tmkc me punching mitts",
    "tmkc me skipping rope","tmkc me kettlebell","tmkc me dumbbell","tmkc me barbell","tmkc me weight plate",
    "tmkc me resistance band","tmkc me yoga mat","tmkc me foam roller","tmkc me massage gun","tmkc me ice pack",
    "tmkc me heating pad","tmkc me bandage","tmkc me band aid","tmkc me gauze","tmkc me adhesive tape",
    "tmkc me antiseptic cream","tmkc me pain relief spray","tmkc me wound cleaner","tmkc me splint","tmkc me sling",
    "tmkc me neck brace","tmkc me knee cap","tmkc me elbow support","tmkc me wrist band","tmkc me ankle support",
    "tmkc me compression socks","tmkc me oxygen mask","tmkc me ventilator","tmkc me ambulance siren","tmkc me stretcher",
    "tmkc me wheelchair","tmkc me walker","tmkc me crutches","tmkc me hearing aid","tmkc me glasses","tmkc me contact lens",
    "tmkc me eye drops","tmkc me nasal spray","tmkc me inhaler","tmkc me glucose monitor","tmkc me thermometer",
    "tmkc me blood pressure machine","tmkc me weighing scale","tmkc me height scale","tmkc me chart paper",
    "tmkc me pin board","tmkc me magnetic board","tmkc me white board marker","tmkc me eraser board","tmkc me spray bottle",
    "tmkc me mist fan","tmkc me cooler pad","tmkc me desert cooler","tmkc me room heater","tmkc me blower",
    "tmkc me air curtain","tmkc me air purifier","tmkc me dehumidifier","tmkc me humidifier","tmkc me aromatherapy diffuser",
    "tmkc me aroma oil","tmkc me tea bag","tmkc me coffee mug","tmkc me saucer","tmkc me tray","tmkc me napkin ring",
    "tmkc me table cloth","tmkc me placemat","tmkc me serving bowl","tmkc me salad spinner","tmkc me cheese grater",
    "tmkc me garlic press","tmkc me potato masher","tmkc me meat tenderizer","tmkc me rolling pin","tmkc me pastry brush",
    "tmkc me measuring cup","tmkc me measuring spoon","tmkc me weighing scale","tmkc me timer","tmkc me oven glove",
    "tmkc me kitchen towel","tmkc me dish rack","tmkc me sink strainer","tmkc me garbage disposal","tmkc me compost bin",
    "tmkc me garden hose","tmkc me spray nozzle","tmkc me fertilizer","tmkc me seed tray","tmkc me garden fork",
    "tmkc me hand trowel","tmkc me bulb planter","tmkc me potting bench","tmkc me greenhouse","tmkc me fleece",
    "tmkc me fleece jacket","tmkc me raincoat","tmkc me gumboots","tmkc me sunscreen","tmkc me insect repellent",
    "tmkc me mosquito net","tmkc me fly swatter","tmkc me rodent trap","tmkc me rat poison","tmkc me cockroach spray",
    "tmkc me termite shield","tmkc me door mat","tmkc me door stopper","tmkc me door knob","tmkc me door chain",
    "tmkc me peephole","tmkc me doorbell","tmkc me security chain","tmkc me deadbolt","tmkc me window grills",
    "tmkc me window curtain","tmkc me blackout curtain","tmkc me sheer curtain","tmkc me curtain rod","tmkc me hook",
    "tmkc me eyelet","tmkc me zip","tmkc me button","tmkc me stud","tmkc me rivet","tmkc me grommet","tmkc me string",
    "tmkc me ribbon","tmkc me lace","tmkc me elastic band","tmkc me velcro strip","tmkc me magnet","tmkc me clips",
    "tmkc me binder clip","tmkc me paper clip","tmkc me staple","tmkc me staple remover","tmkc me pin","tmkc me safety pin",
    "tmkc me drawing pin","tmkc me thumbtack","tmkc me pushpin","tmkc me sticky note","tmkc me post it",
    "tmkc me page marker","tmkc me bookmark","tmkc me index card","tmkc me flashcard","tmkc me alphabet toy",
    "tmkc me puzzle","tmkc me board game","tmkc me chess board","tmkc me chess pieces","tmkc me dice","tmkc me playing cards",
    "tmkc me joker","tmkc me domino","tmkc me ludo","tmkc me snake and ladder","tmkc me carrom board",
    "tmkc me carrom striker","tmkc me carrom powder","tmkc me pool table","tmkc me pool cue","tmkc me billiard ball",
    "tmkc me triangle rack","tmkc me chalk cube","tmkc me scoring stick","tmkc me bingo machine","tmkc me tambola ticket",
    "tmkc me roulette wheel","tmkc me poker chips","tmkc me blackjack table","tmkc me slot machine","tmkc me prize cup",
    "tmkc me medal","tmkc me trophy","tmkc me certificate","tmkc me degree","tmkc me transcript","tmkc me result sheet",
    "tmkc me mark sheet","tmkc me question paper","tmkc me answer sheet","tmkc me admit card","tmkc me identity card",
    "tmkc me passport","tmkc me visa","tmkc me ticket","tmkc me boarding pass","tmkc me luggage tag","tmkc me baggage claim",
    "tmkc me trolley","tmkc me suitcase","tmkc me backpack","tmkc me duffel bag","tmkc me pouch","tmkc me wallet",
    "tmkc me coin purse","tmkc me credit card","tmkc me debit card","tmkc me atm card","tmkc me pan card",
    "tmkc me aadhar card","tmkc me voter id","tmkc me driving license","tmkc me registration certificate",
    "tmkc me insurance policy","tmkc me health card","tmkc me ration card","tmkc me gas card","tmkc me metro card",
    "tmkc me bus pass","tmkc me train ticket","tmkc me platform ticket","tmkc me seat number","tmkc me coach number",
    "tmkc me compartment","tmkc me pantry car","tmkc me sleeper berth","tmkc me ac coach","tmkc me unreserved",
    "tmkc me waiting list","tmkc me confirm ticket","tmkc me cancel ticket","tmkc me refund","tmkc me counter",
    "tmkc me queue","tmkc me token","tmkc me coupon","tmkc me voucher","tmkc me offer","tmkc me discount",
    "tmkc me haggling","tmkc me bargain","tmkc me free sample","tmkc me trial pack","tmkc me demo piece",
    "tmkc me showroom piece","tmkc me display model","tmkc me warehouse stock","tmkc me clearance sale",
    "tmkc me festive offer","tmkc me combo pack","tmkc me family pack","tmkc me economy pack","tmkc me premium pack",
    "tmkc me luxury edition","tmkc me limited edition","tmkc me collectors item","tmkc me unboxing video",
    "tmkc me review video","tmkc me reaction video","tmkc me funny clip","tmkc me viral meme","tmkc me troll post",
    "tmkc me roast message","tmkc me savage reply","tmkc me ultimate gaali","tmkc me final violation",
    "tmkc me tera kya hoga","tmkc me tu rotega","tmkc me susu","tmkc me potty","tmkc me L","tmkc me teri ma",
    "tmkc me hasna","tmkc me rona","tmkc me scrubber","tmkc me ac","tmkc me tent","tmkc me clutch","tmkc me dua",
    "tmkc me tie","tmkc me tree","tmkc me keede","tmkc pe aalu","tmkc me blue light","tmkc me red light","tmkc me dino"
]

# --- GLOBALS FOR NEW SYSTEMS ---
swipe_loops = {}  # user_id -> {'stopped': False, 'lines': list, 'message_id': int, 'channel_id': int}
lock_data = {}    # user_id -> True (global lock)
clock_data = {}   # user_id -> custom_message

original_profile = {}
saved_profiles = {}
current_profile_name = None

# --- ORIGINAL BOT MANAGEMENT GLOBALS ---
SELF_REACT_EMOJI = None
lock_targets = {}          # channel_id -> user_id
lock_messages = {}         # channel_id -> custom message
react_targets = {}
active_bots = {}
locked_pfp = {}
start_time = None
global_react_target = None  # (user_id, emoji)
copycat_mode = set()        # channel IDs where echo is enabled
purge_from_ids = {}

# --- REX LISTS (unchanged) ---
REX_LIST = [
    "चुदाई Kha 😂❤️", "उठक बैठक लगा 😏🔥", "तेरी माँ चोदू 😍😍", "ओय कमजोर 🤢🤢", 
    "लंड चूस 🥱🤍➿", "पिल्लै 🐕‍", "😱 arey 😉 ye 🤡 kaise 😋 kiya 😏 re 😁 teri 😊 maa 😍 randy 😭100% 😂",
    "कमजोर टट्टा", "👈🏻👆🏻🖖🏻👇🏻🤲🏻👉🏻🤏🏻 Idr Udr Jidr Bhi Dekhega Teri Randi Maa Dikhegi",
    " 𝘽𝙀𝙏𝘼 🤢᭄᭄᭄᭄ 🌟 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝙎 🤪᭄᭄", "मदरचोद 🤮🤮", "ro 🤣🤣", "रंडी", "चुप tmr 😒😂",
    "Acha Beta ? Koi Na Mai Teri माँ Coduga 😹💥💯", "चुदकड़", "कमजोर पिल्ले 🤮👞", "Chup Rndyce ⁉", 
    "Tmkc Mein Mist Breathing ☁", "Teri माँ margyi 😂😂😂", "Teri Maa चोदू If Yes Then Reply To My Message 😂😂💯💯",
    "चल तेरी माँ की चुत 🥵🥵", "Tera बाप Rex 🗿🌙💯💯", "Chal Tmkb Me Ghuss Ke Nanga Kruuu 🦈🦈",
    "🔥ꪻꫀ᥅ﺃ ꪑꪖꪖ ꪗꪖꫝꪖ ᥴꪊᦔꪻﺃ ꫝꫀꫀ 💢", "🧬Tmkc random 🤢🤢🖕🏻🖕🏻🖕🏻🧬",
    "𝘼𝙕 𝙉𝙄𝘾𝐇𝙀 𝙍𝙔𝙉𝘿𝙔 𝙆𝙀 𝘽𝘾𝘾𝐇𝐄 🗞️🗞️", "Itna codunga ki 10 din tak tryma hag bhi nhi payegi rndice 🤢🤢🔥🔥🔥",
    "(👑) 𝐁𝐎𝐋 𝐑𝐄𝐗 𝐆𝐀𝐖𝐃 𝐊𝐈 𝐉𝐀𝐈 𝐇𝐎 (👑)", "🔥Likhna sikh low lvl rndy ᛕꪊꪻꪻﺃ ᛕꫀꫀ ᜣﺃꪶꪶꫀ ꪻꪑᛕᥴ 🤢👞👞🔥",
    "Dekh tyri ma sod ke bhgta hua main 🙄😁 👉🏻🏃🏃🏃🏃🏃🏃🏃", "tyri ma chamiya gulaati mrke dikha 🤢🔥😂",
    "Are beta sun पंखा chalu kar तेरी maa ne पाद मारी 🫢🔥😝😦", "song bejhkr tyri maike bosrey mey disco krega cya😅",
    "𝑚𝑎𝑟𝑘𝑒𝑡 𝑠𝑒 𝑙𝑎𝑦𝑎 𝑝𝑎𝑝ི𝑡𝑎 ⚢︎𝒕𝒆𝒓𝒊 𝒎𝒂 𝒌𝒊 𝒄𝒖𝒕 𝒎𝒂𝒓𝒂 𝒄𝒉𝒊𝒕𝒂 🤪🫏💢🎀", "आवाज नीचे कर pille औकात अनुसार बोला kar 🤢🤢🔥",
    "tery buddhi ma ce mu pr mukke mrke गूंगी bnake sodunga 🤢👊🏿💔", "tery ma sudce switch off hogyiss 😈 balle balle 😝✌🔥",
    "tery ma takly भंगी rdy 🤲🔥🤲🔥🤲", "𝘈𝘣𝘦 𝘙𝘥𝘺 𝘒𝘦 पिल्ले 𝘈𝘱𝘯𝘪 𝘔𝘢 𝘒𝘰 𝘎𝘢𝘭𝘪𝘺𝘢 𝘏𝘪 𝘒𝘩𝘪𝘭𝘷𝘢𝘵𝘢 𝘙𝘢𝘩𝘦𝘨𝘢 𝘊𝘺𝘢 𝘏𝘶𝘮𝘴𝘩𝘢 ✌🏻🤢🤣😂💯🔥",
    "tery ma potty pessab🔥😖🔥ᴀɪ✯", "𝘊𝘩𝘢ʟ 𝘵𝘦𝘳𝘪 𝘣𝘩𝘯 𝘬𝘢𝘢 𝘣𝘰𝘴𝘥𝘢 😝🤢✌🏿", "𝘛𝘌𝘙𝘐 𝘔𝘈 𝘒𝘙𝘌 𝘊𝘏𝘈𝘐𝘠𝘈 𝘊𝘏𝘈𝘐𝘠𝘈 🤢👌🏿",
    "𝘾𝙃𝘼𝙇 𝙆𝙐𝙏𝙄𝙔𝙀 𝙎𝘼𝙇𝘼𝙈𝙄 𝙏𝙃𝙊𝙆 👏🏿🔥👏🏿🔥", "❤️𝘛𝘦𝘳𝘪🩵 𝘮𝘢𝘢 🧡𝘬𝘰💚 𝘦𝘴𝘦 🖤𝘤𝘰𝘥𝑎🖤 𝘵𝘩𝑎🖤 𝘥𝑒𝑘𝘩💜 𝘪𝘥𝘩𝘢𝘳 🤍𝘣𝘩𝘦𝘯𝘨𝘦🩷",
    "𝘾𝙃𝘼𝙇 𝙍𝙉𝘿𝙄𝙆𝙀 𝙐𝙏𝙃𝘼𝙆 𝘽𝙀𝙏𝙃𝘼𝙆 𝙇𝘼𝙂𝘼😁🔥"
]

ENG_LIST = [
    "𝘽𝘼𝙇𝘿 𝙉𝙄𝙂𝙂𝘼", "𝙏𝙐𝙁𝙁", "𝙎𝙔𝘽𝘼𝙐", "𝘾𝙍𝙔 𝙈𝙊𝙍𝙀",
    "𝙁𝙐𝘾𝙆 𝙐𝙍 𝙈𝙊𝙈𝙎 𝙂𝙍𝘼𝙑𝙀", "𝙉𝙄𝙂𝙂𝘼", "𝘽𝙄𝙏𝘾𝙃 𝘼𝙎𝙎 𝙐𝙋",
    "𝘼𝙐𝙏𝙄𝙎𝙈 𝙈𝙊𝙉𝙆𝙀𝙔", "𝙐𝙍 𝙎𝙄𝙎 𝘽𝙄𝙏𝘾𝙃", "𝙏𝙃𝙄𝙉 𝘼𝙎𝙎",
    "𝙒𝙀𝙄𝙍𝘿 𝘼𝙎𝙎", "𝘾𝙍𝙀𝙀𝙋 𝙉𝙄𝙂𝙂𝘼", "𝙆𝙔𝙎 𝙐𝙉𝘾",
    "𝙎𝙔𝙁𝙈", "𝙈𝙊𝙏𝙃𝙀𝙍𝙁𝘾𝙆𝙍", "𝙎𝙇𝙐𝙏𝙏𝙔 𝘼𝙎𝙎",
    "𝘼 𝙏𝙍𝘼𝙎𝙃 𝙄𝙎 𝙈𝙊𝙍𝙀 𝙐𝙎𝙀𝙁𝙐𝙇 𝙏𝙃𝘼𝙉 𝙐", "𝘿𝙍𝙄𝙉𝙆 𝙐𝙍𝙄𝙉𝙀 𝙏𝙒𝙄𝙉", "𝙇𝙊𝙒 𝙎𝙋𝙀𝘾𝙄𝙀𝙎"
]

REX_SPAM_LIST = ["𑁍ࠬܓ<🩷>ʟᴀɴᴅ ᴄʜᴏᴏꜱ ɴᴏʀᴍɪᴇ ℘✩₊˚.⋆🕸️", "𑁍ࠬܓ<💜>ᴄʜᴜᴅ ᴊᴀ ɴᴏʀᴍɪᴇ ℘✩₊˚.⋆👾", "𑁍ࠬܓ<💕>ᴛᴇʀɪ ᴍᴀ ᴘᴏᴛᴛʏ ᴘᴇsᴀʙ😖🔥ᴀɪ✯", "𑁍ࠬܓ<🩵>ᴛᴇʀɪ ᴍᴀ ᴄᴜᴅɪ ʀᴇx अब्बू sᴇ"]

REX_SWIPE_LIST = ["Tʀꪗ Bʜɴ तक्ली -😂🤟🏻💕", "𝐓ʀʏ 𝐌ᴀ 𝐂ʏ 𝐂ᴜᴛ 𝐏ʀ चप्पल Mᴀʀᴜɴɢα 🤪᭄🩴🔥", "𝐂ʜαʟ 𝐇αʀᴍ𝐳α𝐝𝐈 𝐊ᴇ लड़के 🤍☁🍃", "Nɪʟᴇ Dᴏʀᴇαᴍᴏɴ Kʏ Sʜᴋ𝐋 Kᴇ लड़के Cʜᴜᴘ Hᴏᴊα 🩴"]

NAME_LIST = [
    "{name} !⭒˚.⋆Lᴜɴ Lᴇ 🤸🏻👐🏻 ִֶָ𓂃 ࣪˖ ִֶָ🦋་༘࿐", "{name} !⭒˚.⋆की बेहन 𝗧𝗔𝗞ＬＩ 🙆🏻",
    "{name} !⭒˚.⋆ki mom ne ᴄʜᴜᴅᴋᴇ ʀᴇx ᴋᴏ ʙᴀᴀᴩ ʙɴᴀ ʟɪʏᴀ 😉🔥", "{name} !⭒˚.⋆ᴩɪʟʟᴇ ᴋɪ ᴍᴀᴀ ᴍᴀʀɪ 👻",
    "{name} !⭒˚.⋆ki mom got 𝗙𝗨𝗖ＫＥＤ 🥀", "{name} !⭒˚.⋆ʀɳडीᴋe idr ꜱᴇ ᴜᴅʜʀ ᴛᴋ ᴄʜᴜᴅ 😂🔥",
    "{name} !⭒˚.⋆Sᴀʏ Rᴇx 𝘥ꪖ𝘥𝘥ꪗ 🪽", "{name} !⭒˚.⋆𝗕𝗛𝗔𝗚 🏃🏻💨", "{name} !⭒˚.⋆𝗚𝗨ΛΑΑΜ 🐕",
    "{name} !⭒˚.⋆ᴋɪᴛɴα ᴄʜᴜᴅᴇɢα ɢαʀɪʙ? 😧😧💔", "{name} !⭒˚.⋆𝗧𝗠ＫＣ 🤢", "{name} !⭒˚.⋆𝐑ɳडीᴋ𝐄 🦶🏻",
    "{name} !⭒˚.⋆Wʜᴏ🇷ᴇ 😜", "{name} !⭒˚.⋆Rɴᴅɪ 😏", "{name} !⭒˚.⋆Cᴠ🇷 𝗞🇷 👞",
    "{name} !⭒˚.⋆Pɪʟ 🤫", "{name} !⭒˚.⋆MɪSᴛʀɪ Kᴇ Lᴀᴅᴋᴇ 🧑🏻‍🔧⛏️",
    "{name} !⭒˚.⋆Try mom stride mh sudi? 🔥🖕🏿🎀🖕🏿", "{name} !⭒˚.⋆uth kuposhit rndyce 🦸‍😂🔥",
    "{name} !⭒˚.⋆𝘾𝙃𝘼𝙇 𝙍𝙉𝘿𝙄𝙆𝙀 𝙐𝙏𝙃𝘼𝙆 𝘽𝙀𝙏𝙃𝘼𝙆 𝙇𝘼𝙂𝘼😁🔥", "{name} !⭒˚.⋆Aʙᴇ Fᴜɴɴʏ Pɪʟʟᴇ JᴏＫER Tʜɪ Kʏᴀ Tᴇʀɪ Mᴀ🔥😂",
    "{name} !⭒˚.⋆Nɪʟᴇ DᴏRᴇ𝐀ＭＯＮ Kʏ Sʜᴋ𝐋 Kᴇ लड़के Cʜᴜ𝐏 Hᴏᴊ𝐀 🩵🩷", "{name} !⭒˚.⋆𝘾𝙮 𝙈𝙖 𝘾𝙤 𝘾𝙮𝙙𝑙𝑒 𝘾𝙝𝙖𝙡𝙖𝙠eke 𝘾𝙤𝘿𝙪𝙣𝐠𝘢 ¡?😁🚴🔥",
    "{name} !⭒˚.⋆oye kutiya k bache", "{name} !⭒˚.⋆Kzmor h dam laga tu"
]

EMO_LIST_1 = ["𓂃६ৎ 𓆩💖𓆪","𓂃६ৎ𓆩💗𓆪","𓂃६ৎ𓆩❤️𓆪"]
EMO_LIST_2 = ["🎐𓍼ֶָ֢⊹ ࣪ ˖","✨𓍼ֶָ֢⊹ ࣪ ˖","🍂𓍼ֶָ֢⊹ ࣪ ˖"]

BASE_LONG_PATTERNS = [
    "➵⤷⤷❤️⤷⤷🤍⤷⤷🖤⤷⤷❤⤷⤷🤍⤷⤷🖤⤷⤷❤️⤷⤷🖤⤷⤷🤍⤷⤷❤️⤷⤷🤍⤷⤷🖤⤷⤷❤️⤷⤷🤍⤷⤷🖤 ",
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫",
    "𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍",
    "✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜",
    "⊹❤️⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹❤️⊹💛⊹❤️⊹🧡⊹💛⊹",
    "彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🖤彡🤍彡🩶彡🖤彡 彡🤍彡",
    "◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈💙◈🩷◈🩵",
    "❋🧡❋💛❋💚❋🧡❋💛❋💚❋🧡❋💛❋💚❋💛❋💚❋🧡❋💛❋💚❋🧡❋💛❋💚❋🧡❋💚❋🧡❋💛❋💚❋🧡❋💛❋💚❋🧡",
    "✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜"
]

TARGET_LENGTH = len("彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🖤彡🤍彡🩶彡🖤彡 彡🤍彡")

def make_long_pattern(base):
    if not base: return ""
    times = (TARGET_LENGTH // len(base)) + 1
    return (base * times)[:TARGET_LENGTH]

LONGNC_PATTERNS = [make_long_pattern(b) for b in BASE_LONG_PATTERNS]

SPAMNC_PATTERN = "ƇӇƲƤ ƦƝƊƳƘƎ 𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫"
HEART_CYCLE = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🩷", "🩵", "🤍", "🖤"]

HOUR_CLOCKS = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
HALF_CLOCKS = ["🕧", "🕜", "🕝", "🕞", "🕟", "🕠", "🕡", "🕢", "🕣", "🕤", "🕥", "🕦"]

def get_clock_emoji(hour, minute):
    idx = hour % 12
    return HALF_CLOCKS[idx] if minute >= 30 else HOUR_CLOCKS[idx]

# ========== MAIN BOT CLASS ==========
class RexMasterBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, self_bot=True)
        self.active_loops = {}
        self.msg_delay = 0.8
        self.nc_delay = 2.5
        self.heart_index = {}
        self.bypass_mode = True
        self.pending_tasks = {}
        self.swipe_tasks = {}  # user_id -> asyncio.Task

    # --- SWIPE LOOP ---
    async def run_swipe_loop(self, target_user_id, message_id, channel_id, lines, swipe_type):
        index = 0
        channel = self.get_channel(channel_id)
        if not channel:
            return
        try:
            target_msg = await channel.fetch_message(message_id)
        except:
            return

        while True:
            if target_user_id not in swipe_loops:
                break
            if swipe_loops[target_user_id].get('stopped', False):
                break

            try:
                if index >= len(lines):
                    index = 0
                reply_text = lines[index]
                index += 1

                sent = await target_msg.reply(reply_text, mention_author=False)
                await sent.add_reaction("🤣")
                await asyncio.sleep(self.msg_delay)

            except discord.errors.NotFound:
                break
            except Exception as e:
                logger.error(f"Swipe loop error: {e}")
                await asyncio.sleep(1)

        swipe_loops.pop(target_user_id, None)

    # --- ATTACK LOOP (NC / SPAM) ---
    async def run_attack(self, cid, cmd, args):
        is_nc = cmd in ["nc", "ncc", "rexnc", "enc", "longnc", "baapnc", "timenc", "spmnc"]
        loop_type = "nc" if is_nc else "spam"

        if cid in self.active_loops and self.active_loops[cid].get(loop_type, False):
            return

        if cid not in self.active_loops:
            self.active_loops[cid] = {"spam": False, "nc": False}
            self.heart_index[cid] = 0
        self.active_loops[cid][loop_type] = True

        self.pending_tasks[cid] = (cmd, args)

        channel = self.get_channel(cid)
        if not channel: return

        burst_count = 0
        if self.bypass_mode and is_nc:
            burst_size = random.randint(12, 15)
            burst_pause = random.randint(3, 5)
        else:
            burst_size = 999999
            burst_pause = 0

        while self.active_loops.get(cid, {}).get(loop_type, False):
            try:
                if self.bypass_mode and is_nc:
                    burst_count += 1
                    if burst_count >= burst_size:
                        await asyncio.sleep(burst_pause)
                        burst_count = 0
                        burst_size = random.randint(12, 15)
                        burst_pause = random.randint(3, 5)

                if cmd == "espam": line = f"{args} {random.choice(ENG_LIST)}"
                elif cmd == "rexspam": line = f"{args} {random.choice(REX_SPAM_LIST)}"
                elif cmd == "cspam": line = args
                elif cmd in ["spam", "chudai"]: line = f"{args} {random.choice(REX_LIST)}"
                elif cmd in ["rexswipe", "eswipe", "cswipe", "target", "targetslide"]:
                    if cmd == "eswipe": line = f"{args} {random.choice(ENG_LIST)}"
                    elif cmd == "cswipe": line = args
                    else: line = f"{args} {random.choice(REX_SWIPE_LIST if cmd=='rexswipe' else REX_LIST)}"
                    async for m in channel.history(limit=1): await m.reply(line, mention_author=False)
                    await asyncio.sleep(self.msg_delay); continue
                elif is_nc:
                    if cmd == "ncc": new_name = f"{random.choice(EMO_LIST_2)} {args} {random.choice(EMO_LIST_1)}"
                    elif cmd == "enc": new_name = f"{args} {random.choice(ENG_LIST)}"[:100]
                    elif cmd == "longnc": new_name = f"{args} {random.choice(LONGNC_PATTERNS)}"
                    elif cmd == "baapnc": new_name = f"{args} {random.choice(LONGNC_PATTERNS)} 𝙏𝙀𝙍𝘼 𝘽𝘼𝘼𝙋 𝙍𝙀𝙓"
                    elif cmd == "spmnc":
                        heart = HEART_CYCLE[self.heart_index[cid] % len(HEART_CYCLE)]
                        self.heart_index[cid] += 1
                        new_name = f"{args} {SPAMNC_PATTERN} {heart}"
                    elif cmd == "timenc":
                        now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                        time_str = now.strftime("%H:%M:%S")
                        clock_emoji = get_clock_emoji(now.hour, now.minute)
                        new_name = f"{args} 𝐃ᴇ𝐊ʜ 𝐓ᴇʀɪ 𝐌ᴀ 𝐊ɪ 𝐂ᴜᴅᴀɪ 𝐊ᴀ 𝐓ɪᴍᴇ 𝐇ᴏɢʏᴀ {time_str} {clock_emoji}"
                    else: new_name = random.choice(NAME_LIST).format(name=args)
                    await channel.edit(name=new_name[:100])
                    await asyncio.sleep(self.nc_delay); continue
                await channel.send(line)
                await asyncio.sleep(self.msg_delay)
            except:
                await asyncio.sleep(2)

        self.pending_tasks.pop(cid, None)

    # --- ON MESSAGE (ALL COMMANDS) ---
    async def on_message(self, message):
        global SELF_REACT_EMOJI, global_react_target
        global swipe_loops, lock_data, clock_data, original_profile, saved_profiles, current_profile_name

        is_sudo = message.author.id in SUDO_USERS
        is_self = message.author.id == self.user.id

        if message.content.startswith(PREFIX):
            if not is_sudo and not is_self:
                await message.reply("𝙆𝙃𝘼𝘿𝙀 𝙃𝙊 𝘾𝙃𝘼𝙈𝘼𝙍 𝙎𝙐𝘿𝙊 𝙆𝙀 𝙇𝙄𝙔𝙀 𝙂𝙐𝙍𝙐 𝘿𝘼𝙆𝙎𝙃𝙄𝙉𝘼 𝙈𝙀 𝙈𝙀𝙍𝘼 𝙇𝙐𝙉𝘿 𝙋𝘼𝙆𝘼𝘿")
                return

            parts = message.content[len(PREFIX):].split()
            cmd = parts[0].lower()
            args = " ".join(parts[1:]) if len(parts) > 1 else ""
            cid = message.channel.id

            # ---------- HELP MENU (FULL) ----------
            if cmd in ["help", "menu"]:
                menu_text = (
                    "```yaml\n"
                    "╔══════════════════════════════════════╗\n"
                    "║    ⛩️  REX QTY MASTER MENU  ⛩️    ║\n"
                    "║     「 GAWD EDITION 」               ║\n"
                    "╚══════════════════════════════════════╝\n"
                    "```\n"
                    "**▸ SYSTEM**\n"
                    "`!status` `!ping` `!refresh` `!spamdelay` `!ncdelay` `!uptime`\n\n"
                    "**▸ NC ENGINE**\n"
                    "`!nc` `!ncc` `!enc` `!rexnc` `!longnc` `!baapnc` `!timenc` `!spmnc`\n"
                    "`!dnc` `!dlongnc` `!dbaapnc` `!dtimenc` `!dspmnc`\n\n"
                    "**▸ SPAM ENGINE**\n"
                    "`!spam` `!espam` `!rexspam` `!cspam` `!chudai`\n"
                    "`!rexswipe` `!eswipe` `!cswipe` `!target` `!targetslide` `!picspm`\n"
                    "`!dspam` `!dswipe` `!dtarget`\n\n"
                    "**▸ SWIPE SYSTEMS**\n"
                    "`!longswipe` (reply) `!teriswipe` (reply) `!tmkcswipe` (reply) `!stopswipe` (reply)\n\n"
                    "**▸ LOCK & CLOCK**\n"
                    "`!lock @user` `!unlock @user`\n"
                    "`!clock <msg>` (reply) `!stopclock` (reply)\n\n"
                    "**▸ PROFILE CLONING**\n"
                    "`!clone` (reply) `!normal` `!saveprf <name>` `!loadprf <name>` `!listsaveprf`\n\n"
                    "**▸ TARGET MODULES**\n"
                    "`!target` `!targetslide`\n\n"
                    "**▸ SUDO CONTROL**\n"
                    "`!addsudo` `!delsudo`\n\n"
                    "**▸ BOT MANAGEMENT**\n"
                    "`!minereact` `!dminereact` `!react` `!dreact`\n"
                    "`!tts` (echo) `!dtts` `!activebots` `!leave`\n"
                    "`!gcpfp` (reply) `!dgcpfp` `!lockgcpfp` `!dlockgcpfp`\n"
                    "`!addbottoken` `!removebottoken`\n"
                    "`!purge <num>` `!purgefrom` `!purgehere` `!joingc` `!invgc`\n"
                    "`!bypassflood`\n\n"
                    "**▸ KILL SWITCHES**\n"
                    "`!stop`\n\n"
                    "```fix\n"
                    "⚡ REX QTY CORE ACTIVE ⚡\n"
                    "```"
                )
                await message.channel.send(menu_text)
                return

            # ---------- STOP ALL ----------
            elif cmd == "stop":
                if cid in self.active_loops:
                    self.active_loops[cid]["spam"] = False
                    self.active_loops[cid]["nc"] = False
                lock_targets.pop(cid, None)
                lock_messages.pop(cid, None)
                copycat_mode.discard(cid)
                global_react_target = None
                self.pending_tasks.pop(cid, None)
                for uid in list(swipe_loops.keys()):
                    swipe_loops[uid]['stopped'] = True
                await message.channel.send("🛑 **ALL LOOPS & FEATURES KILLED**")
                return

            # ---------- NC / SPAM STOP ----------
            elif cmd == "dnc":
                if cid in self.active_loops: self.active_loops[cid]["nc"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **NC LOOP STOPPED**")
                return
            elif cmd == "dspam":
                if cid in self.active_loops: self.active_loops[cid]["spam"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **SPAM LOOP STOPPED**")
                return
            elif cmd in ["dswipe", "dtarget"]:
                if cid in self.active_loops: self.active_loops[cid]["spam"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **SWIPE/TARGET LOOP STOPPED**")
                return
            elif cmd == "dtts":
                copycat_mode.discard(cid)
                await message.channel.send("🔁 Echo mode OFF")
                return

            # ---------- STATUS / UPTIME / PING ----------
            elif cmd == "status":
                latency_ms = round(self.latency * 1000)
                active_nc = sum(1 for v in self.active_loops.values() if v.get("nc"))
                active_spam = sum(1 for v in self.active_loops.values() if v.get("spam"))
                memory = psutil.Process(os.getpid()).memory_info().rss // 1024 // 1024
                guilds = len(self.guilds)
                status_text = (
                    f"**Bot Health Status**\n"
                    f"• Latency: `{latency_ms}ms`\n"
                    f"• Active NC loops: `{active_nc} channels`\n"
                    f"• Active spam loops: `{active_spam} channels`\n"
                    f"• Active swipes: `{len(swipe_loops)}`\n"
                    f"• Memory usage: `{memory} MB`\n"
                    f"• Servers: `{guilds}`"
                )
                await message.channel.send(status_text)
                return
            elif cmd == "uptime":
                if not start_time:
                    await message.channel.send("Uptime not available yet.")
                else:
                    delta = datetime.utcnow() - start_time
                    hours, remainder = divmod(int(delta.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    await message.channel.send(f"⏱️ Uptime: `{hours}h {minutes}m {seconds}s`")
                return
            elif cmd == "ping":
                latency = round(self.latency * 1000)
                await message.channel.send(f"🏓 **Pong!** `{latency}ms`")
                return
            elif cmd == "refresh":
                if cid in self.active_loops:
                    self.active_loops[cid]["spam"] = False
                    self.active_loops[cid]["nc"] = False
                gc.collect()
                await message.channel.send("🔄 **Bot refreshed & optimised. Speed tuned.**")
                return

            # ---------- DELAY SET ----------
            elif cmd == "spamdelay":
                ms = float(args) if args else 800
                self.msg_delay = ms / 1000
                await message.channel.send(f"spam delay set {int(ms)}ms")
                return
            elif cmd == "ncdelay":
                ms = float(args) if args else 2500
                self.nc_delay = ms / 1000
                await message.channel.send(f"NC delay set {int(ms)}ms")
                return

            # ---------- STOP SPECIFIC NC ----------
            elif cmd in ["dlongnc", "dbaapnc", "dtimenc", "dspmnc"]:
                if cid in self.active_loops: self.active_loops[cid]["nc"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send(f"🛑 **{cmd.upper()} STOPPED**")
                return

            # ---------- SUDO ----------
            elif cmd == "addsudo" and is_self:
                for u in message.mentions:
                    if u.id not in SUDO_USERS: SUDO_USERS.append(u.id)
                await message.channel.send("👑 **SUDO USERS ADDED**")
                return
            elif cmd == "delsudo" and is_self:
                for u in message.mentions:
                    if u.id in SUDO_USERS: SUDO_USERS.remove(u.id)
                await message.channel.send("👑 **SUDO USERS REMOVED**")
                return

            # ---------- REACT / MINEREACT ----------
            elif cmd == "dreact":
                global_react_target = None
                await message.channel.send("🔴 **Global react removed**")
                return
            elif cmd == "dminereact":
                SELF_REACT_EMOJI = None
                await message.channel.send("🔕 **Self-react emoji disabled.**")
                return
            elif cmd == "react":
                if not message.mentions or not args:
                    await message.channel.send("Usage: `!react :emoji: @user`")
                    return
                user = message.mentions[0]
                emoji = args.split(" ")[0]
                global_react_target = (user.id, emoji)
                await message.channel.send(f"🎯 Will react to **{user.display_name}** messages with {emoji}")
                return
            elif cmd == "minereact":
                if not args:
                    await message.channel.send("Usage: `!minereact :emoji:`")
                    return
                SELF_REACT_EMOJI = args.strip()
                await message.channel.send(f"✅ Self-react emoji set to {SELF_REACT_EMOJI}")
                return

            # ---------- OLD LOCK / CLOCK (channel-based) ----------
            elif cmd == "dlock":
                if cid in lock_targets:
                    del lock_targets[cid]
                    lock_messages.pop(cid, None)
                    await message.channel.send("🔓 **Lock removed.**")
                else:
                    await message.channel.send("No lock active in this channel.")
                return
            elif cmd == "lock":
                if not message.mentions:
                    await message.channel.send("Usage: `!lock @user`")
                    return
                user = message.mentions[0]
                lock_targets[cid] = user.id
                lock_messages.pop(cid, None)
                await message.channel.send(f"🔒 **{user.display_name}** locked – auto-replying with random REX.")
                return
            elif cmd == "clock":
                if not message.mentions:
                    if cid in lock_targets:
                        del lock_targets[cid]
                        lock_messages.pop(cid, None)
                        await message.channel.send("🔓 Lock removed.")
                    else:
                        await message.channel.send("No lock active in this channel.")
                    return
                user = message.mentions[0]
                lock_msg = " ".join(parts[2:]) if len(parts) > 2 else random.choice(REX_LIST)
                lock_targets[cid] = user.id
                lock_messages[cid] = lock_msg
                await message.channel.send(f"🔒 **{user.display_name}** locked – custom reply set.")
                return

            # ---------- ECHO TOGGLE (TTS) ----------
            elif cmd == "tts":
                if not args:
                    if cid in copycat_mode:
                        copycat_mode.discard(cid)
                        await message.channel.send("🔁 Copycat mode OFF")
                    else:
                        copycat_mode.add(cid)
                        await message.channel.send("🔁 Copycat mode ON – I'll mirror your messages instantly.")
                    return
                await message.channel.send(f"[TTS DISABLED] {args}")
                return

            # ---------- ACTIVE BOTS ----------
            elif cmd == "activebots":
                if not active_bots:
                    await message.channel.send("No active bots recorded yet.")
                else:
                    lines = [f"• **{data['name']}** – {data['status']}" for uid, data in active_bots.items()]
                    await message.channel.send("**Active Bots:**\n" + "\n".join(lines))
                return

            # ---------- LEAVE ----------
            elif cmd == "leave":
                if message.guild:
                    await message.channel.send("👋 Leaving server...")
                    await message.guild.leave()
                elif isinstance(message.channel, discord.GroupChannel):
                    await message.channel.send("👋 Leaving group...")
                    await message.channel.leave()
                else:
                    await message.channel.send("This command can only be used in a server or group DM.")
                return

            # ---------- ICON LOCK / UNLOCK ----------
            elif cmd == "gcpfp":
                if not message.reference:
                    await message.channel.send("Reply to an image with `!gcpfp` to set & lock the server/group icon.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    if ref_msg.attachments:
                        img_url = ref_msg.attachments[0].url
                        async with aiohttp.ClientSession() as session:
                            async with session.get(img_url) as resp: img_bytes = await resp.read()
                        if message.guild:
                            await message.guild.edit(icon=img_bytes)
                            locked_pfp[message.guild.id] = img_bytes
                            await message.channel.send("✅ Server icon updated & locked.")
                        elif isinstance(message.channel, discord.GroupChannel):
                            await message.channel.edit(icon=img_bytes)
                            locked_pfp[message.channel.id] = img_bytes
                            await message.channel.send("✅ Group icon updated & locked.")
                        else:
                            await message.channel.send("This command can only be used in a server or group DM.")
                    else:
                        await message.channel.send("No image found in the replied message.")
                except Exception as e:
                    await message.channel.send(f"Failed to change icon: {e}")
                return
            elif cmd == "dgcpfp":
                if not message.guild: return await message.channel.send("This command only works in a server.")
                try: await message.guild.edit(icon=None); await message.channel.send("🗑️ **Server icon removed.**")
                except Exception as e: await message.channel.send(f"Failed to remove icon: {e}")
                return
            elif cmd == "lockgcpfp":
                if not message.guild: return await message.channel.send("This command only works in a server.")
                try:
                    if message.guild.icon:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(message.guild.icon.url) as resp: img_bytes = await resp.read()
                        locked_pfp[message.guild.id] = img_bytes
                        await message.channel.send("🔒 **Server icon locked.** Any changes will be reverted.")
                    else: await message.channel.send("Server has no icon to lock.")
                except Exception as e: await message.channel.send(f"Failed to lock icon: {e}")
                return
            elif cmd == "dlockgcpfp":
                if message.guild and message.guild.id in locked_pfp:
                    del locked_pfp[message.guild.id]; await message.channel.send("🔓 **Server icon lock removed.**")
                else: await message.channel.send("No icon lock active or not in server.")
                return

            # ---------- TOKEN MANAGEMENT ----------
            elif cmd == "addbottoken" and is_self:
                if not args: await message.channel.send("Usage: `!addbottoken <token>`"); return
                token = args.strip()
                if token not in TOKENS:
                    TOKENS.append(token)
                    save_tokens(TOKENS)
                    Thread(target=start_bot, args=(token,), daemon=True).start()
                    await message.channel.send("✅ Token added and bot started.")
                else: await message.channel.send("Token already exists.")
                return
            elif cmd == "removebottoken" and is_self:
                if not args: await message.channel.send("Usage: `!removebottoken <token>`"); return
                token = args.strip()
                if token in TOKENS:
                    TOKENS.remove(token)
                    save_tokens(TOKENS)
                    await message.channel.send("✅ Token removed (bot may still run until restart).")
                else: await message.channel.send("Token not found.")
                return

            # ---------- PURGE ----------
            elif cmd == "purge":
                if not args.isdigit():
                    await message.channel.send("Usage: `!purge <amount>`")
                    return
                amount = int(args)
                async for msg in message.channel.history(limit=amount+1):
                    try: await msg.delete()
                    except: pass
                    await asyncio.sleep(0.5)
                return
            elif cmd == "purgefrom":
                if not message.reference:
                    await message.channel.send("Reply to the **start** message with `!purgefrom`")
                    return
                purge_from_ids[cid] = message.reference.message_id
                await message.channel.send("✅ Start message saved. Now reply to the **end** message with `!purgehere`")
                return
            elif cmd == "purgehere":
                if not message.reference or cid not in purge_from_ids:
                    await message.channel.send("You must first set a start message with `!purgefrom` (reply to it), then reply to the end message with `!purgehere`")
                    return
                from_id = purge_from_ids.pop(cid)
                to_id = message.reference.message_id
                after = await message.channel.fetch_message(from_id)
                before = await message.channel.fetch_message(to_id)
                async for msg in message.channel.history(limit=100, before=before, after=after):
                    try: await msg.delete()
                    except: pass
                    await asyncio.sleep(0.5)
                try: await after.delete()
                except: pass
                try: await before.delete()
                except: pass
                return

            # ---------- PICTURE SPAM ----------
            elif cmd == "picspm":
                if not message.reference:
                    await message.channel.send("Reply to an image with `!picspm` to spam it.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    if not ref_msg.attachments:
                        await message.channel.send("No image in the replied message.")
                        return
                    img_url = ref_msg.attachments[0].url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(img_url) as resp:
                            img_bytes = await resp.read()
                    file = discord.File(BytesIO(img_bytes), filename="spam.png")
                    if cid not in self.active_loops:
                        self.active_loops[cid] = {"spam": False, "nc": False}
                    self.active_loops[cid]["spam"] = True
                    self.pending_tasks[cid] = ("picspm", args)
                    channel = self.get_channel(cid)
                    if not channel: return
                    while self.active_loops[cid]["spam"]:
                        try:
                            await channel.send(file=file)
                            file = discord.File(BytesIO(img_bytes), filename="spam.png")
                            await asyncio.sleep(self.msg_delay)
                        except:
                            await asyncio.sleep(2)
                except Exception as e:
                    await message.channel.send(f"Failed: {e}")
                return

            # ---------- JOIN / INVITE GROUP ----------
            elif cmd == "joingc":
                invite_link = args
                if not invite_link:
                    await message.channel.send("Provide an invite link: `!joingc https://discord.gg/...`")
                    return
                try:
                    invite = await self.fetch_invite(invite_link)
                    await invite.accept()
                    await message.channel.send("✅ Joined the group/channel.")
                except Exception as e:
                    await message.channel.send(f"Failed to join: {e}")
                return
            elif cmd == "invgc":
                if not message.mentions:
                    await message.channel.send("Mention users to create a group with them.")
                    return
                try:
                    group = await self.create_group(message.mentions)
                    await message.channel.send(f"✅ Group created: {group.name} (ID: {group.id})")
                except Exception as e:
                    await message.channel.send(f"Failed to create group: {e}")
                return

            # ---------- BYPASS FLOOD ----------
            elif cmd == "bypassflood":
                self.bypass_mode = not self.bypass_mode
                state = "ON (burst mode – faster NC)" if self.bypass_mode else "OFF (old‑school safe continuous)"
                await message.channel.send(f"🔥 Bypass mode: {state}")
                return

            # ---------- ATTACK COMMANDS ----------
            elif cmd in ["spam", "espam", "rexspam", "cspam", "rexswipe", "eswipe", "cswipe", "chudai", "target", "targetslide",
                         "nc", "ncc", "rexnc", "enc", "longnc", "baapnc", "timenc", "spmnc"]:
                asyncio.create_task(self.run_attack(cid, cmd, args))
                return

            # ========== NEW USER‑BASED LOCK & CLOCK (for global auto‑reply) ==========
            elif cmd == "lockuser":
                if not message.mentions:
                    await message.channel.send("❌ Mention the user to lock: `!lockuser @user`")
                    return
                target = message.mentions[0]
                lock_data[target.id] = True
                if target.id in swipe_loops:
                    swipe_loops[target.id]['stopped'] = True
                    self.swipe_tasks.pop(target.id, None)
                await message.channel.send(f"🔒 **{target.display_name}** locked globally (REX replies).")
                return

            elif cmd == "unlockuser":
                if not message.mentions:
                    await message.channel.send("❌ Mention the user to unlock: `!unlockuser @user`")
                    return
                target = message.mentions[0]
                if target.id in lock_data:
                    del lock_data[target.id]
                    await message.channel.send(f"🔓 **{target.display_name}** unlocked.")
                else:
                    await message.channel.send(f"❌ {target.display_name} is not locked.")
                return

            elif cmd == "clockuser":
                if not message.reference:
                    await message.channel.send("❌ You need to reply to a user's message to set a clock.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    target = ref_msg.author
                except:
                    await message.channel.send("❌ Could not fetch the replied message.")
                    return
                if args.strip():
                    clock_data[target.id] = args.strip()
                    if target.id in swipe_loops:
                        swipe_loops[target.id]['stopped'] = True
                        self.swipe_tasks.pop(target.id, None)
                    lock_data.pop(target.id, None)
                    await message.channel.send(f"⏰ Clock set for {target.display_name}: `{args.strip()}`")
                else:
                    if target.id in clock_data:
                        del clock_data[target.id]
                        await message.channel.send(f"⏰ Clock cleared for {target.display_name}.")
                    else:
                        await message.channel.send(f"❌ No clock set for {target.display_name}.")
                return

            elif cmd == "stopclockuser":
                if not message.reference:
                    await message.channel.send("❌ Reply to the user whose clock you want to stop.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    target = ref_msg.author
                except:
                    await message.channel.send("❌ Could not fetch the replied message.")
                    return
                if target.id in clock_data:
                    del clock_data[target.id]
                    await message.channel.send(f"⏰ Clock stopped for {target.display_name}.")
                else:
                    await message.channel.send(f"❌ No clock active for {target.display_name}.")
                return

            # ========== SWIPE COMMANDS (new) ==========
            elif cmd in ["longswipe", "teriswipe", "tmkcswipe"]:
                if not message.reference:
                    await message.channel.send("❌ You need to reply to a user's message to use this command.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    target = ref_msg.author
                    target_msg = ref_msg
                except:
                    await message.channel.send("❌ Could not fetch the replied message.")
                    return

                if target.id in swipe_loops:
                    swipe_loops[target.id]['stopped'] = True
                    await asyncio.sleep(0.5)

                if cmd == "longswipe":
                    lines = LONGSWIPE_LINES
                elif cmd == "teriswipe":
                    lines = TERISWIPE_LINES
                else:
                    lines = TMKCSWIPE_LINES

                swipe_loops[target.id] = {
                    'stopped': False,
                    'lines': lines,
                    'message_id': target_msg.id,
                    'channel_id': target_msg.channel.id
                }
                task = asyncio.create_task(
                    self.run_swipe_loop(
                        target.id,
                        target_msg.id,
                        target_msg.channel.id,
                        lines,
                        cmd
                    )
                )
                self.swipe_tasks[target.id] = task
                await message.channel.send(f"✅ **{cmd.upper()}** activated for {target.display_name}.")
                return

            elif cmd == "stopswipe":
                if not message.reference:
                    await message.channel.send("❌ Reply to the user whose swipe you want to stop.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    target = ref_msg.author
                except:
                    await message.channel.send("❌ Could not fetch the replied message.")
                    return

                if target.id in swipe_loops:
                    swipe_loops[target.id]['stopped'] = True
                    self.swipe_tasks.pop(target.id, None)
                    await message.channel.send(f"✅ Stopped swipe for {target.display_name}.")
                else:
                    await message.channel.send(f"❌ No active swipe for {target.display_name}.")
                return

            # ========== PROFILE CLONING ==========
            elif cmd == "clone":
                if not message.reference:
                    await message.channel.send("❌ Reply to the user whose profile you want to clone.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    target = ref_msg.author
                except:
                    await message.channel.send("❌ Could not fetch the replied message.")
                    return

                new_display_name = target.display_name
                avatar_url = target.display_avatar.url
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(avatar_url) as resp:
                            avatar_bytes = await resp.read()
                except:
                    await message.channel.send("❌ Failed to download avatar.")
                    return

                try:
                    await self.user.edit(username=new_display_name)
                except Exception as e:
                    logger.warning(f"Could not change username: {e}")

                if message.guild:
                    try:
                        await message.guild.me.edit(nick=new_display_name)
                    except Exception as e:
                        logger.warning(f"Could not change nickname: {e}")

                try:
                    await self.user.edit(avatar=avatar_bytes)
                except Exception as e:
                    await message.channel.send(f"❌ Failed to change avatar: {e}")
                    return

                if not original_profile:
                    orig_name = self.user.display_name
                    orig_avatar = self.user.display_avatar.url
                    original_profile = {
                        "name": orig_name,
                        "avatar_url": orig_avatar,
                        "bio": ""
                    }
                    profiles = load_profiles()
                    profiles["original"] = original_profile
                    save_profiles(profiles)

                await message.channel.send(f"✅ Cloned profile of **{target.display_name}**.")
                return

            elif cmd == "normal":
                if not original_profile:
                    await message.channel.send("❌ No original profile saved. Use `!clone` first.")
                    return

                try:
                    await self.user.edit(username=original_profile["name"])
                except Exception as e:
                    logger.warning(f"Could not restore username: {e}")

                if message.guild:
                    try:
                        await message.guild.me.edit(nick=original_profile["name"])
                    except Exception as e:
                        logger.warning(f"Could not restore nickname: {e}")

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(original_profile["avatar_url"]) as resp:
                            avatar_bytes = await resp.read()
                    await self.user.edit(avatar=avatar_bytes)
                except Exception as e:
                    await message.channel.send(f"❌ Failed to restore avatar: {e}")
                    return

                current_profile_name = None
                await message.channel.send("✅ Restored original profile.")
                return

            elif cmd == "saveprf":
                if not args:
                    await message.channel.send("❌ Provide a name: `!saveprf <name>`")
                    return
                if not message.guild:
                    await message.channel.send("❌ This command can only be used in a server (to get nickname).")
                    return
                current_name = message.guild.me.display_name
                current_avatar_url = self.user.display_avatar.url
                profiles = load_profiles()
                if "saved" not in profiles:
                    profiles["saved"] = {}
                profiles["saved"][args] = {
                    "name": current_name,
                    "avatar_url": current_avatar_url,
                    "bio": ""
                }
                save_profiles(profiles)
                await message.channel.send(f"✅ Profile saved as **{args}**.")
                return

            elif cmd == "listsaveprf":
                profiles = load_profiles()
                saved = profiles.get("saved", {})
                if not saved:
                    await message.channel.send("❌ No saved profiles.")
                else:
                    names = ", ".join(saved.keys())
                    await message.channel.send(f"**Saved profiles:** {names}")
                return

            elif cmd == "loadprf":
                if not args:
                    await message.channel.send("❌ Provide a name: `!loadprf <name>`")
                    return
                profiles = load_profiles()
                saved = profiles.get("saved", {})
                if args not in saved:
                    await message.channel.send(f"❌ Profile `{args}` not found.")
                    return
                prof = saved[args]
                try:
                    await self.user.edit(username=prof["name"])
                except Exception as e:
                    logger.warning(f"Could not change username: {e}")
                if message.guild:
                    try:
                        await message.guild.me.edit(nick=prof["name"])
                    except Exception as e:
                        logger.warning(f"Could not change nickname: {e}")
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(prof["avatar_url"]) as resp:
                            avatar_bytes = await resp.read()
                    await self.user.edit(avatar=avatar_bytes)
                except Exception as e:
                    await message.channel.send(f"❌ Failed to load avatar: {e}")
                    return
                current_profile_name = args
                await message.channel.send(f"✅ Loaded profile **{args}**.")
                return

            else:
                await message.channel.send(f"❌ Unknown command: `{cmd}`. Use `!help`.")

        # ========== NON-COMMAND MESSAGES (AUTO-REPLY SYSTEMS) ==========
        if is_self:
            return

        author = message.author
        cid = message.channel.id

        # --- NEW USER-BASED SYSTEMS (Priority: Clock > Lock > Swipe) ---
        if author.id in clock_data:
            try:
                await message.reply(clock_data[author.id], mention_author=False)
            except:
                pass
            return

        if author.id in lock_data:
            try:
                reply_text = random.choice(REX_LIST)
                await message.reply(reply_text, mention_author=False)
            except:
                pass
            return

        # Swipe is handled by the dedicated loop – nothing here.

        # --- OLD CHANNEL-BASED LOCK (for compatibility) ---
        if is_sudo:
            if cid in lock_targets and message.author.id == lock_targets[cid]:
                reply_text = lock_messages.get(cid, random.choice(REX_LIST))
                try:
                    await message.reply(reply_text, mention_author=False)
                except:
                    pass

        # --- GLOBAL REACT (works for any user) ---
        if global_react_target and message.author.id == global_react_target[0]:
            try:
                await message.add_reaction(global_react_target[1])
            except:
                pass

        # --- COPYCAT (only sudo users) ---
        if is_sudo:
            if cid in copycat_mode:
                if message.reference:
                    try:
                        ref_msg = await message.channel.fetch_message(message.reference.message_id)
                        if ref_msg:
                            await ref_msg.reply(message.content, mention_author=False)
                    except:
                        pass
                else:
                    await message.channel.send(message.content)

    # --- ON_CONNECT, ON_DISCONNECT, ON_READY ---
    async def on_connect(self):
        global start_time
        start_time = datetime.utcnow()
        active_bots[self.user.id] = {"name": str(self.user), "status": "online"}

    async def on_disconnect(self):
        if self.user.id in active_bots:
            active_bots[self.user.id]["status"] = "offline"

    async def on_ready(self):
        global start_time
        start_time = datetime.utcnow()
        print(f"⛩️ CORE ONLINE: {self.user.name}")
        logger.info(f"✅ Bot online: {self.user.name} (ID: {self.user.id})")
        logger.info(f"✅ Connected to {len(self.guilds)} servers")
        active_bots[self.user.id] = {"name": str(self.user), "status": "online"}

        for cid, (cmd, args) in list(self.pending_tasks.items()):
            asyncio.create_task(self.run_attack(cid, cmd, args))

    async def on_guild_update(self, before, after):
        if after.id in locked_pfp and before.icon != after.icon:
            try: await after.edit(icon=locked_pfp[after.id])
            except: pass

def start_bot(token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            bot = RexMasterBot()
            bot.run(token)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            time_module.sleep(5)

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()

    if not TOKENS:
        try:
            with open("tokens.json", "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    TOKENS = [t for t in data if t and "TOKEN" not in t]
        except:
            pass

    if not TOKENS:
        logger.error("⚠ No tokens found! Set TOKENS environment variable.")
        logger.error("Format: TOKENS=token1,token2,token3")
        while True:
            time_module.sleep(1)

    for t in TOKENS:
        Thread(target=start_bot, args=(t,), daemon=True).start()
        time_module.sleep(2)

    while True:
        time_module.sleep(1)
