import json
import logging
from dictReader import informalKeywords, formalKeywords
import re, urllib2,urllib
from google.appengine.api import urlfetch
import oauth2
import time
import nltk
import contextIOUtils
try:
    import endpoints
    from CXIO.contextIO2 import ContextIO,Contact,Account
except KeyError:
    pass
interjections={'ayup': 0, 'pardon': 0, 'ciao': 0, 'hell no': 0, 'whoops': 0, 'kick ass': 0, 'derp': 0, 'ta-ra': 0, 'great Scott': 0, 'hell or high water': 0, 'ayuh': 0, 'thwok': 0, 'sorry': 0, 'thwop': 0, 'kerflop': 0, 'jeepers creepers': 0, "don't go there": 0, 'anend': 0, 'yikes': 0, 'a-ha': 0, 'whish': 0, 'humph': 0, 'humpity': 0, 'red alert': 0, 'hot damn': 0, 'oh my Goddess': 0, 'man alive': 0, 'oooh': 0, 'more power to your elbow': 0, 'whist': 0, 'aaaaagh': 0, 'oh my gods': 0, 'as you wish': 0, 'dang it': 0, 'gee willikers': 0, 'whaddayamean': 0, 'evil laugh': 0, 'nee': 0, 'cockshit': 0, 'ner': 0, 'meh': 0, 'here': 0, 'ching': 0, 'bloody hell': 0, "what's cooking": 0, 'on your marks': 0, 'no fear': 0, 'goddamnit': 0, 'crazysauce': 0, 'ooh arrh': 0, 'mazeltov': 0, 'welcs': 0, 'glhf': 0, 'brr': 0, 'gee willickers': 0, 'what in the world': 0, 'schwing': 0, 'couis': 0, 'AIUI': 0, 'tsk-tsk': 0, 'alley oop': 0, 'hardy har har': 0, 'mush': 0, 'haha': 0, 'yahoo': 0, 'gee up': 0, 'oh no': 0, 'crimenetly': 0, 'goddammit': 0, 'hola': 0, 'shoot': 0, 'shoop': 0, 'mm': 0, 'righty': 0, 'mu': 0, 'erm': 0, 'righto': 0, 'my': 0, 'God in heaven': 0, 'ching chong': 0, 'now, now': 0, "'sfoot": 0, 'hoa': 0, 'no worries': 0, 'hoo': 0, 'nuts': 0, 'uh huh': 0, 'how': 0, 'no shit, Sherlock': 0, 'omigosh': 0, 'fair dos': 0, 'hoy': 0, 'cor blimey': 0, 'beauty': 0, 'go wonder': 0, 'thankyou': 0, "for God's sake": 0, 'law': 0, 'God willing': 0, 'bon appetit': 0, 'fee-fi-fo-fum': 0, 'goodbye': 0, 'hosanna': 0, 'bleurgh': 0, 'alack': 0, "'zackly": 0, 'mwah ha ha': 0, 'over': 0, 'eish': 0, 'holy moley': 0, 'crumbs': 0, 'right-ho': 0, 'aargh': 0, 'bread-and-butter': 0, 'get lost': 0, 'lawks': 0, 'doggone': 0, 'howdy': 0, 'Christ on a bike': 0, 'fough': 0, 'fie': 0, 'cheese and rice': 0, 'your mother': 0, 'nenikikamen': 0, 'prithee': 0, 'ROTFLMAO': 0, 'ba-dum ching': 0, 'tick tock': 0, 'bang': 0, 'grumpity': 0, 'ba da bing ba da boom': 0, 'fnord': 0, 'oh really': 0, 'wirra': 0, 'goshdang': 0, 'nyuk': 0, 'cheery-bye': 0, 'abracadabra': 0, 'lamesauce': 0, 'fairy snuff': 0, 'hot diggety': 0, 'zoinks': 0, "a'right": 0, 'heylow': 0, 'see ya': 0, 'nerts': 0, 'no can do': 0, 'brrm': 0, 'ahchoo': 0, 'suffering cats': 0, 'whammo': 0, 'brrr': 0, 'dickfuck': 0, 'so there': 0, 'yeah-huh': 0, 'dammit': 0, 'dayum': 0, 'suck it': 0, 'goldurn': 0, 'kapwing': 0, 'Christ on a cracker': 0, 'wowee': 0, 'shough': 0, 'get away': 0, 'ho hum': 0, 'hold the phone': 0, 'tsktsk': 0, 'nanu-nanu': 0, 'chupse': 0, 'fol-de-rol': 0, 'big deal': 0, 'howzit': 0, 'mox nix': 0, 'get real': 0, 'hiya': 0, 'ta-ta for now': 0, 'trick or treat': 0, 'bzzzt': 0, 'have it your way': 0, 'wassat': 0, 'Uhuru': 0, 'hoowee': 0, 'yowch': 0, 'begone': 0, 'geeminy': 0, "'ere": 0, "yes'm": 0, 'whoomp': 0, 'shit the bed': 0, 'about sledge': 0, 'zounds': 0, 'amidships': 0, 'you betcha': 0, 'mooch ass grassy ass': 0, 'endquote': 0, 'ka-ching': 0, 'rah': 0, 'hushabye': 0, 'fuhgeddaboudit': 0, 'in your face': 0, 'so what': 0, 'yoo hoo': 0, 'what': 0, 'damn your hide': 0, 'rumble': 0, 'crimony': 0, 'God forbid': 0, 'doh': 0, 'doo': 0, 'oh em gee': 0, 'tallyho': 0, 'wotcher': 0, 'musha': 0, 'some people': 0, 'ullo': 0, 'oo-er': 0, 'U cont.': 0, "hell's bells": 0, 'dagnammit': 0, 'sage': 0, 'bugger': 0, 'queep': 0, 'oh my days': 0, 'och': 0, 'ock': 0, 'what the': 0, 'sies': 0, 'OKDK': 0, 'sugar': 0, 'hrm': 0, 'Template:en-interj': 0, 'geez': 0, 'nyet': 0, 'Appendix:Farscape/yotza': 0, 'bumpity': 0, 'no shit': 0, 'helluv': 0, 'my word': 0, 'fooey': 0, 'jiminy cricket': 0, 'baccare': 0, 'mamma mia': 0, 'I cont.': 0, 'NVRM': 0, 'bah': 0, 'och aye': 0, 'mafeesh': 0, 'nee-naw': 0, 'nudge nudge wink wink': 0, 'faix': 0, 'result': 0, 'nuh': 0, 'pardie': 0, 'goshdangit': 0, 'bleh': 0, 'fiddlesticks': 0, 'capiche': 0, 'not even': 0, 'pfff': 0, 'tee hee': 0, 'mum': 0, 'pfft': 0, 'bada bing bada boom': 0, 'wo': 0, 'bosh': 0, 'ai yah': 0, 'egads': 0, 'pity': 0, 'cor': 0, 'my giddy aunt': 0, 'lookit': 0, 'mew': 0, 'sweet mother of Jesus': 0, 'shiver me timbers': 0, 'unf': 0, 'snakes alive': 0, 'giddyup': 0, 'coo': 0, 'thwap': 0, 'tough': 0, 'alleluia': 0, 'nosuh': 0, 'yeugh': 0, 'heigho': 0, 'tilly-fally': 0, 'uhhuh': 0, 'damn straight': 0, 'bingo': 0, 'on your horse, amigo': 0, 'sure thing': 0, 'furrfu': 0, 'you bet': 0, 'what it do': 0, 'jossa': 0, 'areet': 0, 'uh-oh': 0, 'oh man': 0, 'oopsie': 0, 'thank heavens': 0, 'chur': 0, 'yippee': 0, 'fuckity': 0, 'pocketa-queep': 0, 'wickup': 0, 'Judas Priest': 0, 'gracious': 0, 'gracias': 0, 'is it': 0, 'zindabad': 0, 'yippee skippy': 0, 'LOL': 0, 'shame': 0, 'alakazam': 0, 'io': 0, 'by Jove': 0, 'rest his soul': 0, 'rat-tat-tat': 0, 'yeeha': 0, 'fair enough': 0, 'honk': 0, 'giddy up': 0, 'egad': 0, 'ello': 0, 'ayoo': 0, 'righty-ho': 0, 'hot diggity': 0, 'wye aye': 0, 'kiss my arse': 0, 'shizzle': 0, 'hot diggety dog': 0, 'itshay': 0, 'K cont.': 0, 'bejeezus': 0, 'presto': 0, 'Y cont.': 0, 'my Lord': 0, 'jeah': 0, 'whaddayathink': 0, 'yeh': 0, 'salaam': 0, 'booyah': 0, 'halloo': 0, 'thwonk': 0, 'yea': 0, 'halloa': 0, 'yo mama': 0, 'yey': 0, 'psych': 0, 'thanks': 0, 'yes': 0, 'kerching': 0, 'hah': 0, 'dearie me': 0, 'bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk': 0, 'wahey': 0, 'how rude': 0, 'ooooh': 0, 'yech': 0, 'hillo': 0, 'har': 0, "'ave it": 0, 'haw': 0, 'baruch HaShem': 0, 'uh uh': 0, 'good now': 0, 'wellaway': 0, 'opa': 0, 'och aye the noo': 0, 'husstenhasstencaffincoffintussemtossemdamandamnacosaghcusaghhobixhatouxpeswchbechoscashlcarcarcaract': 0, 'skoal': 0, 'good job': 0, 'H cont.': 0, 'big whoop': 0, 'right': 0, 'chuck you Farley': 0, 'be careful': 0, 'Goddy': 0, 'who writes this stuff': 0, 'ick': 0, 'get on': 0, 'pip pip': 0, 'umm': 0, 'HALGI': 0, 'foo': 0, 'foh': 0, 'kerboom': 0, 'I should coco': 0, 'urgh': 0, 'night': 0, 'phew': 0, 'goo goo ga ga': 0, 'dayee': 0, 'napoo': 0, 'meow': 0, 'oh my heck': 0, 'kerblam': 0, 'fuck me': 0, 'no chance': 0, 'God bless you': 0, 'aha': 0, 'sod': 0, 'ahh': 0, 'yanno': 0, 'chimo': 0, 'crivvens': 0, 'tant mieux': 0, 'ole': 0, 'hallo': 0, 'hamana-hamana-hamana': 0, 'wah': 0, 'shoot me': 0, 'dear me': 0, 'way': 0, 'hear ye': 0, "'snails": 0, 'whaddayasay': 0, 'teehee': 0, 'bleargh': 0, 'unh-uh': 0, 'fore': 0, 'phwoar': 0, 'kowabunga': 0, 'gadzooks': 0, 'oh-oh': 0, 'viva': 0, 'congratulations': 0, 'hear, hear': 0, 'gesundheit': 0, 'take care': 0, 'zark': 0, 'attagal': 0, "j'adoube": 0, 'my ass': 0, 'thunk': 0, 'thiam': 0, 'shit': 0, 'holla': 0, 'whee': 0, 'na': 0, 'fancy that': 0, 'hollo': 0, 'whew': 0, 'fair suck of the sav': 0, 'nu': 0, 'heyday': 0, 'what the fuck': 0, 'good gracious': 0, 'get stuffed': 0, 'lackaday': 0, 'fiddledeedee': 0, 'tut tut': 0, 'good grief': 0, 'criminently': 0, "'i": 0, 'eff all': 0, 'mwahaha': 0, 'time': 0, 'smeg': 0, 'ouch': 0, 'bostin': 0, 'sleep tight': 0, 'Allahu akbar': 0, 'holy smoke': 0, 'O RLY': 0, 'achoo': 0, 'suffering succotash': 0, 'yummo': 0, 'tush': 0, 'yert': 0, 'point taken': 0, 'ReHi': 0, 'thank God': 0, 'C cont.': 0, 'blimey': 0, 'goodness gracious me': 0, 'see you soon': 0, 'word': 0, 'blast': 0, 'w00t': 0, 'hoorah': 0, 'get out of here': 0, 'brother': 0, 'hooray': 0, 'ptooie': 0, 'holy kamoley': 0, 'lovely jubbly': 0, 'buck up': 0, 'in sha Allah': 0, 'ay up': 0, 'bravo': 0, 'tnx': 0, 'hip hip hooray': 0, 'bleeding heck': 0, 'yoohoo': 0, 'thank you': 0, 'havoc': 0, 'geroff': 0, 'N cont.': 0, 'send her down Hughie': 0, 'sod it': 0, 'just shoot me': 0, 'knock knock': 0, "for cryin' out loud": 0, 'boy': 0, 'too much information': 0, 'Jesus H. Christ': 0, 'ptui': 0, 'blooming heck': 0, 'get bent': 0, 'ta ta for now': 0, 'bok': 0, 'boo': 0, "h'lo": 0, 'giddap': 0, 'yiff': 0, 'nice one': 0, 'gidday': 0, 'wazzat': 0, 'roll up': 0, 'iunno': 0, 'dadgum': 0, 'pfaugh': 0, 'giddyap': 0, 'sodding hell': 0, 'ayo': 0, 'lumme': 0, 'handbags': 0, 'aye': 0, 'phht': 0, 'lummy': 0, 'oof': 0, 'clum': 0, 'look here': 0, 'ooh': 0, 'ook': 0, 'avaunt': 0, 'goshdurn': 0, 'mmhmm': 0, 'thumpity': 0, 'I like pie': 0, 'get out': 0, 'heaven forfend': 0, 'lordy': 0, 'fuck': 0, 'chit': 0, 'how now': 0, 'upsadaisy': 0, 'good going': 0, 'shazbot': 0, 'outasight': 0, 'bada boom bada bing': 0, 'blow me': 0, 'hmph': 0, 'my bad': 0, 'maa': 0, 'goldurnit': 0, 'Goddidit': 0, 'boo-ya': 0, 'man': 0, 'fuck-a-doodle-doo': 0, 'frick': 0, 'blow me down': 0, 'st': 0, 'sh': 0, 'so': 0, 'harch': 0, 'god forbid': 0, 'yee-haw': 0, 'Mississippi': 0, 'indeed': 0, 'namaste': 0, 'blarg': 0, 'Abyssinia': 0, 'au revoir': 0, 'hoo man': 0, 'P U': 0, 'hey ho': 0, 'thanx': 0, 'criminetly': 0, 'holy crap on a cracker': 0, 'Holy Mother of God': 0, 'bacaw': 0, 'nom': 0, "who's a pretty boy then": 0, 'ta ta': 0, 'yeowch': 0, 'srsly': 0, 'halleluja': 0, 'de nada': 0, 'pip-pip': 0, 'now': 0, 'bullshit': 0, 'thank god': 0, 'bloody Nora': 0, 'kersplat': 0, 'yes way': 0, 'yayness': 0, 'eh': 0, 'horsefeathers': 0, 'my sainted uncle': 0, 'ee': 0, 'yeah': 0, 'uffda': 0, 'yo-ho-ho': 0, 'farewell': 0, "you'll never guess": 0, 'ew': 0, 'toodle-oo': 0, 'uhuh': 0, 'er': 0, 'now then': 0, 'phut': 0, 'fu': 0, 'all hands on deck': 0, 'cripes': 0, "don't I know it": 0, 'wayleway': 0, 'quite': 0, 'argh': 0, 'carn': 0, 'day-ee': 0, 'bejesus': 0, 'yesh': 0, 'heaven forbid': 0, 'yuk': 0, 'yum': 0, 'toodeloo': 0, 'cheese': 0, 'zam': 0, 'ecky thump': 0, 'mem.': 0, 'pillaloo': 0, 'uh oh': 0, 'bumpsadaisy': 0, "'sdeath": 0, 'GDGD': 0, 'zap': 0, 'stop the lights': 0, 'nee nor': 0, 'heave-ho': 0, 'gorry': 0, 'get in': 0, 'yo momma': 0, 'bottoms up': 0, 'thanks for coming': 0, 'hum': 0, 'huh': 0, 'alas': 0, 'hup': 0, "g'day": 0, 'yoo-hoo': 0, 'ohmmm': 0, 'Jesus Harold Christ': 0, 'gee whiz': 0, 'oorah': 0, 'yaroo': 0, 'yallo': 0, 'dash': 0, 'woah': 0, 'say': 0, 'Bueller': 0, 'boo hoo': 0, 'cloop': 0, 'nigga please': 0, 'hey presto': 0, 'well, I never': 0, 'ah-choo': 0, 'criminy': 0, 'yaba daba doo': 0, 'zot': 0, 'T cont.': 0, 'sure': 0, 'holy fuck': 0, 'blooey': 0, 'there ya go': 0, 'hey rube': 0, 'lawl': 0, 'wagwan': 0, 'aarrghh': 0, 'holy guacamole': 0, 'atishoo': 0, 'tra-la-la': 0, 'omigod': 0, 'touche': 0, 'soho': 0, 'uncle': 0, 'shop': 0, 'shot': 0, 'mirabile dictu': 0, 'shoo': 0, 'woot': 0, 'gulp': 0, 'woof': 0, 'neato': 0, 'what you saying': 0, 'tally ho': 0, 'horse hockey': 0, 'gee': 0, 'lots of love': 0, 'no prob': 0, 'Ichabod': 0, 'holy mackerel': 0, 'todah rabah': 0, 'roger': 0, 'tatty bye': 0, 'very well': 0, 'bismillah': 0, 'godsdamn': 0, 'fiddlefart': 0, 'good for you': 0, 'strewth': 0, 'megstie': 0, 'hist': 0, 'diddly': 0, 'yessirree': 0, 'uh': 0, 'haway': 0, 'tut': 0, 'cool beans': 0, 'fuhgedaboutit': 0, 'jinkies': 0, 'far out': 0, 'jumping Jesus': 0, 'nuh-uh': 0, 'bwahaha': 0, "'struth": 0, 'backare': 0, 'chin up': 0, 'what-what': 0, "m'kay": 0, 'pow': 0, 'period': 0, 'pop': 0, 'poo': 0, 'poh': 0, 'stone me': 0, 'endeed': 0, 'good-by': 0, "dang tootin'": 0, 'hunh': 0, 'take a hike': 0, 'caramba': 0, 'hardly': 0, 'battle stations': 0, 'no kidding': 0, "d'oh": 0, 'gorblimey': 0, 'ey up': 0, "'zactly": 0, 'baaa': 0, 'good God': 0, 'aaagh': 0, 'holy crap': 0, 'sound': 0, 'bullocks': 0, 'geronimo': 0, 'kablam': 0, 'allrighty': 0, 'cock': 0, 'vum': 0, 'blah': 0, 'yeees': 0, 'heavens to Betsy': 0, 'pax': 0, 'jeepers': 0, "you don't say": 0, 'butter my butt and call me a biscuit': 0, 'whaddayawant': 0, 'pad': 0, 'yessir': 0, 'pah': 0, 'LOLZ': 0, 'goldarn': 0, 'thank fuck': 0, 'tough luck': 0, 'thank gods': 0, 'stone the crows': 0, 'alrighty': 0, 'right on': 0, 'cheers': 0, 'howay': 0, 'suck my balls': 0, 'quotha': 0, 'thankyouverymuch': 0, 'wakey wakey': 0, 'booyakasha': 0, 'eureka': 0, 'tara': 0, 'God preserve us': 0, 'my arse': 0, 'when': 0, 'crappity': 0, 'greetings': 0, 'flappity': 0, 'dear Lord': 0, 'fuddle-duddle': 0, 'benedicite': 0, "I'll be": 0, 'le sigh': 0, 'naw': 0, 'bada boom': 0, 'the dickens': 0, 'salutations': 0, 'my foot': 0, 'buh-bye': 0, 'moo': 0, 'hot ziggety': 0, 'wuxtry': 0, 'pst': 0, 'sithee': 0, 'hot diggity dog': 0, 'hallelujah': 0, 'hadaway': 0, 'bear-a-hand': 0, 'sommer': 0, 'yesss': 0, 'good heavens': 0, "'scuse": 0, 'good riddance': 0, 'nooo': 0, 'waly': 0, "devil's beating his wife": 0, 'hachoo': 0, 'crap on a stick': 0, 'never say die': 0, 'mwah': 0, 'ta tah': 0, 'oh God': 0, 'yarooh': 0, 'jeez': 0, 'fuhgeddaboutit': 0, 'oi': 0, 'oh': 0, 'ack': 0, 'uh-uh': 0, 'jeet': 0, 'HTH': 0, 'oy': 0, 'go away': 0, 'ow': 0, 'sry': 0, 'cowabunga': 0, 'garn': 0, 'F off': 0, 'curses': 0, 'thankee': 0, 'eyup': 0, 'TT4N': 0, 'sucre bleu': 0, 'fuck yeah': 0, 'there': 0, 'hey': 0, 'lol': 0, 'hee': 0, 'hem': 0, 'loadsamoney': 0, 'heh': 0, 'praytell': 0, 'my God': 0, 'yeah, no': 0, 'good bye': 0, 'aye man': 0, 'ploop': 0, 'God Save the King': 0, 'whoops-a-daisy': 0, 'uffdah': 0, 'attaboy': 0, 'oh well': 0, 'hooah': 0, 'holy kamoly': 0, 'surprise surprise': 0, 'oho': 0, 'ag': 0, 'I say': 0, 'bring it': 0, 'Jesum Crow': 0, 'abso-fucking-lutely': 0, 'aw': 0, 'ay': 0, 'Jesus fucking Christ': 0, 'well said': 0, 'pfui': 0, 'my goodness': 0, 'yow': 0, 'wuzzup': 0, 'shazaam': 0, 'cootchie-cootchie-coo': 0, 'fsck': 0, 'poof': 0, 'fugh': 0, 'pooh': 0, 'gerroff': 0, 'lo and behold': 0, 'damn your eyes': 0, 'squee': 0, 'God damn': 0, 'eigh': 0, 'S cont.': 0, 'gangway': 0, 'roger that': 0, 'touch wood': 0, 'shazam': 0, 'you know it': 0, 'nom nom nom': 0, 'kthxbye': 0, 'zing': 0, 'alreet': 0, 'bish bash bosh': 0, 'hmmm': 0, 'wilco': 0, 'blahdy blah': 0, 'wassup': 0, 'get outta here': 0, 'ta': 0, 'begob': 0, 'yeah right': 0, 'fap': 0, 'righteo': 0, 'hee-haw': 0, 'nick off': 0, 'A cont.': 0, 'lauk': 0, 'chin-chin': 0, 'dang tooting': 0, 'well, well': 0, "fo' shizzle": 0, 'thunderation': 0, 'whallah': 0, 'pretty please': 0, 'bug off': 0, 'ticky': 0, 'tuwhit tuwhoo': 0, 'whap': 0, 'sup': 0, 'en garde': 0, 'what up': 0, 'long time': 0, 'yecch': 0, 'psshaw': 0, 'avast': 0, 'loose': 0, 'vale': 0, 'hi there': 0, 'diddums': 0, 'lah-de-dah': 0, 'eat my dust': 0, 'long time no hear': 0, 'action': 0, 'zowie': 0, 'thock': 0, 'ough': 0, 'zooterkins': 0, 'full stop': 0, 'ja well no fine': 0, 'cooey': 0, 'Jeezum Crow': 0, 'wahlau': 0, 'plonk': 0, 'Deo volente': 0, 'cooee': 0, 'hey up': 0, 'gosh': 0, 'huzzah': 0, 'open sesame': 0, 'hurray': 0, 'shite': 0, 'nuch': 0, "'zounds": 0, 'hurrah': 0, 'good gravy': 0, 'yuck': 0, 'opps': 0, 'jog on': 0, 'howzat': 0, 'lorks': 0, 'yah boo': 0, 'welladay': 0, 'shpadoinkle': 0, 'zip-a-dee-doo-dah': 0, 'thwomp': 0, 'look at you': 0, 'gods damn': 0, 'fair go': 0, 'jislaaik': 0, 'by God': 0, 'kapow': 0, 'shock horror': 0, 'tilly-vally': 0, 'heck': 0, 'peas and rice': 0, 'net-net': 0, 'ay, chihuahua': 0, 'fy': 0, 'capisce': 0, 'end of': 0, 'bahaha': 0, 'batter up': 0, 'bleah': 0, 'say wha': 0, 'humbug': 0, 'yipes': 0, 'anytime': 0, 'G cont.': 0, 'ducdame': 0, 'pleasure': 0, 'do what': 0, "don't": 0, 'sook': 0, 'zoiks': 0, 'hands off': 0, 'tough cookies': 0, 'durn tooting': 0, 'hell': 0, 'oh my god': 0, 'furry muff': 0, 'drop dead': 0, 'dammy': 0, 'adios': 0, 'what ho': 0, 'bummer': 0, 'damme': 0, 'foom': 0, 'good': 0, 'yo': 0, 'fook': 0, 'ya': 0, 'sssh': 0, 'uhh': 0, 'thank goodness': 0, 'not for the world': 0, 'uhu': 0, 'flaming Nora': 0, "durn tootin'": 0, 'harrow': 0, 'any time': 0, 'bless': 0, 'just wondering': 0, 'unquote': 0, 'jings': 0, 'correctamundo': 0, 'wacko': 0, 'really': 0, 'true dat': 0, 'no duff': 0, 'huh-uh': 0, 'well, well, well': 0, 'lolz': 0, 'uh-huh': 0, 'puh': 0, 'bully': 0, 'by golly': 0, 'hullo': 0, 'mmm': 0, 'snerk': 0, 'woe is me': 0, 'ay me': 0, 'hell and tommy': 0, 'golly': 0, 'nee way': 0, 'come on': 0, 'Jayzus': 0, 'chi-ike': 0, 'fucking hell': 0, 'ooer': 0, 'N.B.': 0, 'but seriously folks': 0, 'yowza': 0, 'nenikekamen': 0, 'nota bene': 0, 'fainites': 0, 'God Almighty': 0, 'struth': 0, 'heads': 0, 'Jeremiah': 0, 'goodness me': 0, 'tata': 0, 'mazal tov': 0, 'sigh': 0, 'bzzt': 0, 'down with his apple-cart': 0, 'rawr': 0, 'pish posh': 0, 'GTH': 0, 'mhmm': 0, 'headdesk': 0, 'parp': 0, 'sod a dog': 0, 'give me strength': 0, 'atta girl': 0, 'cuntshit': 0, 'mama mia': 0, 'condolences': 0, 'holy Toledo': 0, 'aah': 0, 'fuddle duddle': 0, 'dang': 0, 'yeek': 0, 'you know': 0, 'buggeration': 0, 'yeep': 0, 'Lord willing': 0, 'fo shizzle my nizzle': 0, 'cave': 0, "that's just me": 0, 'ta muchly': 0, 'whatever floats your boat': 0, 'fa shizzle': 0, 'oh my': 0, 'herro': 0, 'eat shit': 0, 'go on': 0, 'holy shit': 0, 'get to fuck': 0, 'awright': 0, 'hands up': 0, 'good morning': 0, 'ready, aim, fire': 0, 'wisha': 0, 'nothing doing': 0, 'Lord be praised': 0, 'bzz': 0, 'dammit to hell': 0, 'voertsek': 0, 'mazel tov': 0, 'bullseye': 0, 'prethe': 0, 'fuhgedaboudit': 0, 'ta-tah': 0, 'heaveno': 0, 'mahalo': 0, "darn tootin'": 0, 'cheerio': 0, 'okey dokey': 0, 'aagh': 0, 'heavens': 0, 'phooey': 0, 'pray tell': 0, 'yay': 0, 'astaghfirullah': 0, 'oh my God': 0, 'goshdarnit': 0, 'bollocks': 0, 'yo ho ho': 0, 'darn tooting': 0, 'Oh Em Gee': 0, 'hic': 0, 'ooh ah ah': 0, 'my sainted aunt': 0, 'heavens above': 0, 'jumpity': 0, 'trufax': 0, 'presto chango': 0, 'so long': 0, 'knickers': 0, 'yassuh': 0, 'ixnay': 0, 'cheerioh': 0, 'arr': 0, 'F cont.': 0, 'tata for now': 0, 'bam': 0, 'no side': 0, 'oy gevalt': 0, 'jeez Louise': 0, 'hewwo': 0, 'whoopsy-daisy': 0, 'pish': 0, 'deary me': 0, "what's shaking": 0, 'wow': 0, 'inshallah': 0, 'white rabbit': 0, 'woo': 0, "h'm": 0, 'checkmate': 0, "thank'ee": 0, 'sweet action': 0, 'gramercy': 0, 'attention': 0, "'ullo": 0, 'pshaw': 0, 'phfft': 0, 'ahoy': 0, 'come on down': 0, 'thanks for nothing': 0, 'hard cheese': 0, 'Janey Mack': 0, 'ribbit': 0, 'hollow': 0, 'DFTBA': 0, 'oyez': 0, 'holloa': 0, 'jumping Jehoshaphat': 0, 'duh': 0, 'fair suck of the sauce bottle': 0, 'lock and load': 0, 'dum': 0, 'nolo episcopari': 0, 'whoopee do': 0, 'foggetaboutit': 0, 'no way': 0, 'whoo': 0, 'damn': 0, 'whoa': 0, 'go fuck yourself': 0, 'voila': 0, 'shiver my timbers': 0, 'mavrone': 0, 'gak': 0, 'gah': 0, 'gad': 0, 'truth be told': 0, 'ha-ha': 0, 'heya': 0, 'man on': 0, 'down with': 0, 'vroom': 0, 'harrumph': 0, 'bada bing': 0, 'bollocks more like': 0, 'shana tova': 0, 'gack': 0, 'basta': 0, 'oh boy': 0, 'eww': 0, 'good show': 0, 'hooroo': 0, 'Jeebus': 0, 'kabish': 0, 'nil desperandum': 0, 'body of me': 0, 'cheep': 0, 'tsk tsk': 0, 'shame on you': 0, 'savvy': 0, 'presto change-o': 0, 'psst': 0, 'darn': 0, 'harumph': 0, 'heartlings': 0, 'asdfghjkl': 0, 'yoicks': 0, 'aloha': 0, 'chewie on ya boot': 0, 'voetsek': 0, 'snap': 0, 'Jesus wept': 0, 'okey-doke': 0, 'ruff': 0, 'om nom nom': 0, 'blech': 0, 'GIYF': 0, 'OK': 0, 'hubba hubba': 0, 'fnar': 0, 'eew': 0, 'eep': 0, 'good morrow': 0, 'eek': 0, 'absit omen': 0, 'all systems go': 0, 'look you': 0, "'dswounds": 0, 'absolutely': 0, 'goddamn': 0, 'O cont.': 0, 'paxis': 0, 'understood': 0, 'tah tah': 0, 'sheesh': 0, 'good-den': 0, 'pew': 0, 'cheerie-bye': 0, 'marry come up': 0, 'cock-a-doodle-doo': 0, 'a little bit of bread and no cheese': 0, 'dad burn': 0, 'zzz': 0, 'tut-tut': 0, 'get knotted': 0, 'bo': 0, 'think of the children': 0, 'shucky ducky': 0, 'faugh': 0, 'by': 0, 'werdup': 0, 'bon voyage': 0, 'bakaw': 0, 'every man for himself': 0, 'all the best': 0, 'ta everso': 0, 'silence': 0, 'goodo': 0, 'rats': 0, 'easy does it': 0, 'good luck': 0, 'bugger off': 0, 'halgi': 0, 'bite me': 0, 'pff': 0, 'oh my stars': 0, 'fast': 0, 'okey-dokey': 0, 'hoppity': 0, 'coppish': 0, 'selah': 0, 'what a way to go': 0, 'vivat': 0, 'W cont.': 0, 'ticktack': 0, 'ur': 0, 'um': 0, 'oh my goodness gracious': 0, 'JSYK': 0, 'yatta': 0, 'hard luck': 0, 'night night': 0, 'fuck a duck': 0, 'god willing': 0, 'we aye': 0, 'JFGI': 0, 'grr': 0, 'woo hoo': 0, 'nah': 0, 'peace': 0, 'TQ': 0, 'parfay': 0, 'tits': 0, 'TG': 0, 'whaddayaknow': 0, 'nice': 0, 'notate bene': 0, 'drat': 0, "hell's teeth": 0, 'gee whillikers': 0, 'phpht': 0, "blow it out one's ass": 0, 'ta-da': 0, 'man overboard': 0, 'uh-oh, Spaghetti-O': 0, 'agh': 0, 'holy cow': 0, 'ready about': 0, 'hella': 0, 'hello': 0, 'fuckaduck': 0, 'kerplunk': 0, 'hello yourself, and see how you like it': 0, 'psyche': 0, 'ugh': 0, 'rightio': 0, 'halleluiah': 0, 'c u l8r': 0, 'flargh': 0, 'ooh la la': 0, 'God bless': 0, 'JW': 0, 'tah-tah': 0, 'tu-whit tu-whoo': 0, 'ye gods': 0, 'sis boom bah': 0, 'curse it': 0, 'whatsay': 0, 'marry': 0, 'oopsy': 0, 'G2G': 0, 'sproing': 0, 'by jingo': 0, 'oofta': 0, 'poor diddums': 0, 'whoopee-do': 0, 'tee hee hee': 0, 'ods': 0, 'toodle pip': 0, 'for the love of God': 0, 'click': 0, 'holy moly': 0, 'bleeding hell': 0, 'applesauce': 0, "'ey up": 0, 'bazinga': 0, 'FTW': 0, 'boomshanka': 0, 'shit fire and save matches': 0, 'blooming hell': 0, 'euoi': 0, 'yeurgh': 0, "'bye": 0, 'ho-hum': 0, 'kerchoo': 0, 'great': 0, 'dagnabbit': 0, 'fire in the hole': 0, 'arrivederci': 0, 'Hell no': 0, 'you go, girl': 0, 'waz up': 0, 'zackly': 0, 'crickety': 0, 'yeehaw': 0, 'good Lord': 0, 'Appendix:Farscape/frell': 0, 'long time no see': 0, 'fuck off': 0, 'ta-ta': 0, 'ha ha': 0, 'whiskey tango foxtrot': 0, 'blood and tommy': 0, 'crap': 0, 'zip': 0, 'hee-hee': 0, 'feh': 0, 'prythee': 0, 'the hell with it': 0, 'dadgummit': 0, 'dominus vobiscum': 0, 'tally-ho': 0, 'steady on': 0, 'rubbish': 0, 'yabba dabba doo': 0, 'Happy Thanksgiving': 0, 'goshdarn': 0, 'this': 0, 'meef': 0, 'yoink': 0, 'yowzah': 0, 'salam': 0, 'pouf': 0, 'atta boy': 0, 'meep': 0, 'phoo': 0, 'neener': 0, 'hard lines': 0, 'kertyschoo': 0, 'screw you': 0, "'sblood": 0, 'lawks a-mercy': 0, 'toodles': 0, 'phwoarr': 0, 'n.b.': 0, 'whaddup': 0, 'but hey': 0, 'begorra': 0, 'zowee': 0, 'fark': 0, 'ohmigod': 0, 'hilloa': 0, 'hrmph': 0, 'hahahaha': 0, 'praise the Lord': 0, 'peace out': 0, 'honestly': 0, 'ooh-ah-ah': 0, 'God Save the Queen': 0, 'fo shizzle': 0, "what's happening": 0, 'clackity': 0, 'damnit': 0, 'aww yeah': 0, 'hushaby': 0, 'tsk': 0, 'la': 0, 'lo': 0, 'you knows it': 0, 'pugh': 0, 'bye': 0, 'my pleasure': 0, 'dag': 0, 'BFD': 0, 'end quote': 0, 'congratudolences': 0, 'wibble-wobble': 0, "wham, bam, thank you ma'am": 0, 'wowf': 0, 'your mom': 0, 'tirralirra': 0, 'mmhm': 0, 'goddidit': 0, 'crikey': 0, 'up yours': 0, 'n/m': 0, 'skol': 0, 'doing': 0, 'dog my cats': 0, 'just kidding': 0, 'hocus pocus': 0, 'okeh': 0, 'tchick': 0, 'I should cocoa': 0, 'ay oop': 0, 'okey': 0, 'wheesht': 0, 'Godspeed': 0, 'shup': 0, 'whoopdee doo': 0, 'heads up': 0, 'kia ora': 0, 'clackety': 0, "s'ok": 0, 'aweel': 0, 'oh dear': 0, 'B cont.': 0, 'Jesus': 0, 'yippie': 0, 'sooey': 0, 'shucks': 0, 'capeesh': 0, 'arp': 0, 'ahoy-hoy': 0, "anchor's aweigh": 0, 'heita': 0, 'think fast': 0, 'banzai': 0, 'hehe': 0, 'you what': 0, 'kazaam': 0, 'siam': 0, 'laters': 0, 'yipe': 0, 'nyah': 0, 'gear': 0, 'pssst': 0, 'exactly': 0, 'blah blah blah': 0, 'cya': 0, 'whoopsy': 0, 'howsit': 0, 'yo mamma': 0, 'mmkay': 0, 'bother': 0, 'attagirl': 0, 'full marks': 0, 'OMW': 0, 'Christ alive': 0, 'encore': 0, 'come off it': 0, 'roll on': 0, 'arf': 0, 'atchoo': 0, 'yeuch': 0, 'tidy': 0, 'for shizzle': 0, 'uckfay': 0, 'amirite': 0, 'goodie': 0, 'consarn it': 0, 'sugar honey ice tea': 0, 'bastard': 0, 'congrats': 0, 'as if': 0, 'gods willing': 0, 'congratz': 0, 'Jiminy Cricket': 0, 'Lord love a duck': 0, 'Mother of God': 0, 'woops': 0, 'adieu': 0, 'wha': 0, 'dot dot dot': 0, 'aww': 0, '^W': 0, '^H': 0, 'right-oh': 0, 'kiss my ass': 0, 'why': 0, "a'ight": 0, 'hot dog': 0, 'Jesus Christ': 0, 'GFU': 0, 'away': 0, 'fact': 0, 'whoopee': 0, 'holy Moses': 0, 'agreed': 0, 'bring': 0, 'deiseal': 0, 'way to go': 0, 'elephant juice': 0, 'bammo': 0, 'Selah': 0, 'wowsers': 0, 'unberufen': 0, 'walaway': 0, 'weyleway': 0, 'bow-wow': 0, 'eurgh': 0, 'ga-ga': 0, 'ooyah': 0, 'hello there': 0, 'yeah, right': 0, 'fair crack of the whip': 0, 'good golly': 0, 'stand easy': 0, 'shalom aleichem': 0, 'shh': 0, 'oontz': 0, 'here we go again': 0, 'begorrah': 0, 'whatevs': 0, 'laduma': 0, 'sessa': 0, 'land ahoy': 0, 'va-va-voom': 0, 'ods bodikin': 0, 'flipping Nora': 0, 'oh my Allah': 0, 'fuckshit': 0, 'take that': 0, 'lul': 0, 'holy cricket': 0, 'amen': 0, 'time out': 0, 'stap my vitals': 0, 'rock on': 0, 'big wow': 0, 'up top': 0, 'as you like': 0, 'yippie ki-yay': 0, 'arrah now': 0, 'Christ': 0, 'be off with you': 0, 'crivens': 0, 'for the love of Mike': 0, 'aw shucks': 0, 'oh-em-gee': 0, 'respect': 0, 'here we go': 0, 'Gordon Bennett': 0, 'get out of town': 0, 'OMGWTFBBQ': 0, 'whoah': 0, 'muahahaha': 0, 'zookers': 0, 'for my money': 0, 'yas': 0, "I don't think": 0, 'motherfuck': 0, 'ah': 0, 'heigh': 0, 'cha-ching': 0, 'yeow': 0, 'FTMFW': 0, 'f**k': 0, 'I never did': 0, 'hmm': 0, 'blow this for a game of soldiers': 0, 'bedad': 0, 'hooie': 0, 'psha': 0, 'hot tamale': 0, 'chop-chop': 0, 'fucking A': 0, 'word up': 0, 'bravissimo': 0, 'hahaha': 0, 'kerplop': 0, 'sankyu': 0, 'all hail': 0, 'oggy oggy oggy': 0, 'my my': 0, 'oy vey': 0, 'gardyloo': 0, 'begad': 0, 'oink': 0, 'kerwham': 0, 'get fucked': 0, 'in-fucking-credible': 0, 'goddang': 0, 'to say the least': 0, 'lah-di-dah': 0, 'oh yeah': 0, 'wough': 0, 'cheer up': 0, 'pht': 0, 'kersplosh': 0, 'chaptzem': 0, 'grand mercy': 0, 'shalom': 0, 'boutye': 0, 'twirp': 0, 'well': 0, 'welp': 0, 'gall dang': 0, 'oops': 0, 'shaddap': 0, 'shiloh': 0, 'tch': 0, 'shhh': 0, 'oh my Lord': 0, "that's a girl": 0, 'roflcopter': 0, 'yeesh': 0, 'clickity': 0, 'rehi': 0, 'la-di-da': 0, 'fye': 0, 'crud': 0, 'whoopsadaisy': 0, 'Holy Mother': 0, 'whatever': 0, 'god dammit': 0, 'go to sleep': 0, 'dy-no-mite': 0, 'well done': 0, 'mhm': 0, 'like': 0, 'holy crickets': 0, 'geez Louise': 0, 'losh': 0, 'soft': 0, 'gods bless you': 0, 'for certain': 0, 'kaboom': 0, 'no thank you': 0, 'squush': 0, 'huzza': 0, 'depardieux': 0, 'slappity': 0, 'Jaysus': 0, 'brmmm': 0, 'woohoo': 0, 'sayonara': 0, 'goldarnit': 0, 'tchah': 0, "'ello": 0, 'grrr': 0, 'brickety': 0, 'heeey': 0, 'damn it': 0, 'kerrang': 0, 'simples': 0, 'shame, shame': 0, 'alack and alas': 0, 'bless you': 0, 'inorite': 0, 'my eye': 0, 'grassy ass': 0, 'whatever creams your twinkie': 0, 'most certainly': 0, 'eina': 0, 'god damn': 0, 'oww': 0, "g'night": 0, 'peccavi': 0, 'clickety': 0, 'fuck this': 0, "fuckin' A": 0, 'suffering catfish': 0, 'screw off': 0, 'sankyuu': 0, 'welaway': 0, 'gratz': 0, 'just a sec': 0, 'yessiree': 0, 'hi': 0, 'ho': 0, 'hm': 0, 'good-bye': 0, 'ha': 0, 'eaw': 0, "I'll drink to that": 0, 'fuck me backwards': 0, 'flip': 0, 'lest we forget': 0, 'hooyah': 0, 'youch': 0, 'ptooey': 0, 'dagnabit': 0, 'durn': 0, "I'd say": 0, 'whisht': 0, 'oh my hell': 0, 'whoopeedoo': 0, 'for shame': 0, 'boom': 0, 'magtig': 0, 'front and center': 0, 'kerpow': 0, 'tschk': 0, 'ahem': 0, 'on your bike': 0, 'no duh': 0, 'damn and blast': 0, 'goodness gracious': 0, 'tough shit': 0, 'goody gumdrops': 0}
class Message:

    def __init__(self,text="",formalityScore=None,informalityScore=None):
        self.text=text
        self.formalityScore=formalityScore
        self.informalityScore=informalityScore
        self.formula_score='????'

def getSentReceivedMessages(userEmail,email,limit=100000):
    #this method is responsible to return the message that userID sent/received to/from email
    #userEmail is the email of userID
    #email is email of a contact of userEmail
    sent=getAllMessages(userEmail,to=email,From=userEmail,limit=limit)
    received=getAllMessages(userEmail,to=userEmail,From=email,limit=limit)


    all=sent+received

    all.sort()
    return [x[1] for x in all]


def  getAllMessages(email,to=None,From=None,limit=100000):
    #this method is responsible to get all messages that userID has exchanged with email

    #for more information regarding this method check:
    #https://console.context.io/#explore/accounts/messages/get

    CONTEXTIO_OAUTH_KEY = endpoints.CONTEXTIO_OAUTH_KEY
    CONTEXTIO_OAUTH_SECRET =endpoints.CONTEXTIO_OAUTH_SECRET

    contextParams={'email':email,'include_body':1,'limit':limit,'include_thread_size':0,'body_type':'text/plain','include_headers':0,'include_flags':0,'sort_order':'desc'}
    if to:
        contextParams['to']=to
    if From:
        contextParams['from']=From
    userID=contextIOUtils.findAccountID(email)
    url='https://api.context.io/2.0/accounts/'+userID+'/messages/'
    url+='?'
    url+=urllib.urlencode(contextParams)
    consumer=oauth2.Consumer(key=CONTEXTIO_OAUTH_KEY,secret=CONTEXTIO_OAUTH_SECRET)

    params = { 'oauth_version': "1.0"}

    params['oauth_consumer_key'] = consumer.key

    params['oauth_nonce'] = oauth2.generate_nonce(20)
    params['oauth_timestamp'] = '%s' % int(time.time())

    req = oauth2.Request(method="GET", url=url, parameters=params)

    # Sign the request.
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)

    res=json.loads(urlfetch.fetch(req.to_url(),method='GET',deadline=30).content)
    messages=[]
    date=[]
    for x in res:
        if len(x['body'])>0 and 'content' in x['body'][0]:
            messages.append(x['body'][0]['content'])
        else:
            messages.append('ERROR: It seems there is no content in this messages!')
        date.append(x['date'])

    messages=[getGoodMessage(x) for x in messages]

    res=[(date[i],messages[i]) for i in range(len(messages))]
    res.sort()
    return res





def simpleParseMessage(s):
    #this function is responsible to return the "new" part of message
    #the quoted parts of a message in gmail starts with
    #on (day of week) (dat) (person) wrote < (the rest of the text)
    days=['Sun','Mon','Tue','Wed','Thu','Fri','Sat']

    month=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    days=days+month

    pat=['On.*'+x+'.*'+'wrote:' for x in days]
    #yet another pattern for parsing message
    numberOnly='On.*[0-9]+/[0-9]+/[0-9]+.*wrote:'
    pat.append(numberOnly)
    numberOnly='On.*[0-9]+[-][0-9]+[-][0-9]+.*wrote:'
    pat.append(numberOnly)
    #I didn't see next format in gmail inbox yet, but let's add it
    numberOnly='On.*[0-9]+[.][0-9]+[.][0-9]+.*wrote:'
    pat.append(numberOnly)
    where=len(s)
    for p in pat:
        f=re.search(p,s)
        if f:
            where=min(where,f.start())

    res=s[:where]
    return res
def getWords(s):
    #simply return the words of a text
    p='[a-zA-Z]+'
    v=re.findall(p,s)
    return v
def getAllGoodWords(words,keywords):
    res=''
    first=True
    for x in words:
        if x in keywords:
            if not first:
                res+=', '
            first=False
            res+=x

    return res
def getInformalWords(text):
    text=text.lower()
    words=getWords(text)
    res=getAllGoodWords(words,informalKeywords)
    return res

def getFormalWords(text):
    text=text.lower()
    words=getWords(text)
    res=getAllGoodWords(words,formalKeywords)
    return res

def getMessage(messageId,userID):

    contextParams={'include_thread_size':0,'include_body':1,'include_headers':0,'body_type':'text/plain','include_flags':0}


    url='https://api.context.io/2.0/accounts/'+userID+'/messages/'+urllib2.quote(messageId)
    url+='?'
    url+=urllib.urlencode(contextParams)


    #CONTEXTIO_OAUTH_KEY = '0z32scu9'
    #CONTEXTIO_OAUTH_SECRET = 'UaRDwOnmE4u3x9Ta'

    CONTEXTIO_OAUTH_KEY = endpoints.CONTEXTIO_OAUTH_KEY
    CONTEXTIO_OAUTH_SECRET =endpoints.CONTEXTIO_OAUTH_SECRET
    consumer=oauth2.Consumer(key=CONTEXTIO_OAUTH_KEY,secret=CONTEXTIO_OAUTH_SECRET)

    params = { 'oauth_version': "1.0"}

    params['oauth_consumer_key'] = consumer.key

    params['oauth_nonce'] = oauth2.generate_nonce(20)
    params['oauth_timestamp'] = '%s' % int(time.time())


    req = oauth2.Request(method="GET", url=url, parameters=params)

    # Sign the request.
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)

    res=json.loads(urlfetch.fetch(req.to_url(),method='GET').content)
    allMessage=res["body"][0]['content']
    #allMessage='Here is the paper Hadi. On Tue, Apr 2, 2013 at 5:52 AM, Hadi Asiaiefard wrote: > Yes, I think so. > > > > > Hadi. > > > On Tue, Apr 2, 2013 at 5:51 AM, KC Lastvali wrote: > >> Hey Hadi, >> >> Ill take a look at the link and also read the paper. >> >> Lets >> - finish up formal vs. informal as specd >> - investigate the paper based on POS >> >> What do you think? Doable for this week? >> >> -- >> KC >> >> >'
    #remove the quoted part
    #res=simpleParseMessage(allMessage)
    res=allMessage

    return res

def getMessagesID(userID,email,limit=3):
    #this method is responsible to return the messages id of messages contactID send/received to/from email
    CONTEXTIO_OAUTH_KEY = endpoints.CONTEXTIO_OAUTH_KEY
    CONTEXTIO_OAUTH_SECRET =endpoints.CONTEXTIO_OAUTH_SECRET

    ctxIO = ContextIO(consumer_key=CONTEXTIO_OAUTH_KEY, consumer_secret=CONTEXTIO_OAUTH_SECRET)
    messages = Contact(Account(ctxIO, {'id':userID}), {'to':email,'email':email}).get_messages(limit=limit)

    messageIDs=[x["email_message_id"] for x in messages]


    return messageIDs

def score(text,keyword):
    textWords=getWords(text)
    #convert the words to lower case
    textWords=[x.lower() for x in textWords]
    #text is a list of words
    #keywords is  a dictionary
    res=0
    for x in textWords:
        if x in keyword:
            res+=1
    return res
def informalScore(text):
    return score(text,informalKeywords)

def formalScore(text):
    return score(text,formalKeywords)

def getGoodMessage(text):
    text=simpleParseMessage(text)
    res=Message()
    res.formalityScore=formalScore(text)
    res.informalityScore=informalScore(text)
    res.formula_score=processText(text)
    res.text=text
    return res

convertTags={'WRB':'adverb','WP':'pronoun','WDT':'pronoun',
             'VBZ':'verb','VBP':'verb','VBN':'verb','VBG':'verb','VBD':'verb',
             'VB':'verb','TO':'preposition','RP':'not important','RBS':'adverb', 'RBR':'adverb','RB':'adverb',
             'PRP$':'pronoun', 'PRP':'pronoun', 'POS':'not important', 'PDT':'article',
             'NNS':'noun', 'NNPS':'noun', 'NNP':'noun', 'NN':'noun', 'MD':'verb',
             'JJS':'adjective', 'JJR':'adjective', 'JJ':'adjective', 'IN':'preposition', 'FW':'not important',
             'EX':'noun', 'DT':'article', 'CD':'not important', 'CC':'not important',
             'interjection':'interjection'
}
def addInterjections(taggedWords):
    res=[]
    for x in taggedWords:
        word,tag=x
        if word in interjections:
            res.append((word,'interjection'))
        else:
            res.append((word,tag))
    return res
def getSimpleTags(taggedWords):
    badTag='not important'
    res=[]
    for x in taggedWords:
        word,tag=x
        if tag in convertTags and convertTags[tag]!=badTag:
            res.append((word,convertTags[tag]))
    return res

def countNumTags(taggedWords):
    cnt={}

    for x in taggedWords:
        word,tag=x
        if not tag in cnt:
            cnt[tag]=0
        cnt[tag]+=1
    return cnt
def getFScore(d):
    #d is a dictionary of tags count
    sum=0
    for x in d:
        sum+=d[x]

    res=0
    addScore=['noun','adjective', 'preposition','article']
    subScore=['pronoun','verb','adverb','interjection']
    for x in d:
        sign=0
        if x in addScore:
            sign=+1
        elif x in subScore:
            sign=-1
        else:
            print 'this is bad tag'
            print x
            raise 'err'
        res+=sign*100*float(d[x])/sum
    res+=100
    res/=2
    return res



def processText(text):
    tokens = nltk.word_tokenize(text)
    taggedWords = nltk.pos_tag(tokens)
    taggedWords=addInterjections(taggedWords)

    taggedWords=getSimpleTags(taggedWords)

    cnt=countNumTags(taggedWords)
    F=getFScore(cnt)
    return F
def  getAllMessagesTest(email,to=None,From=None,limit=100000):
    #this method is responsible to get all messages that userID has exchanged with email

    #for more information regarding this method check:
    #https://console.context.io/#explore/accounts/messages/get

    CONTEXTIO_OAUTH_KEY = endpoints.CONTEXTIO_OAUTH_KEY
    CONTEXTIO_OAUTH_SECRET =endpoints.CONTEXTIO_OAUTH_SECRET

    contextParams={'email':email,'include_body':1,'limit':limit,'include_thread_size':0,'include_headers':0,'include_flags':0,'sort_order':'desc'}
    if to:
        contextParams['to']=to
    if From:
        contextParams['from']=From
    userID=contextIOUtils.findAccountID(email)
    url='https://api.context.io/2.0/accounts/'+userID+'/messages/'
    url+='?'
    url+=urllib.urlencode(contextParams)
    consumer=oauth2.Consumer(key=CONTEXTIO_OAUTH_KEY,secret=CONTEXTIO_OAUTH_SECRET)

    params = { 'oauth_version': "1.0"}

    params['oauth_consumer_key'] = consumer.key

    params['oauth_nonce'] = oauth2.generate_nonce(20)
    params['oauth_timestamp'] = '%s' % int(time.time())

    req = oauth2.Request(method="GET", url=url, parameters=params)

    # Sign the request.
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)

    res=json.loads(urlfetch.fetch(req.to_url(),method='GET',deadline=30).content)
    return res
    messages=[]
    date=[]
    for x in res:
        if len(x['body'])>0 and 'content' in x['body'][0]:
            messages.append(x['body'][0]['content'])
        else:
            messages.append('ERROR: It seems there is no content in this messages!')
        date.append(x['date'])

    messages=[getGoodMessage(x) for x in messages]

    res=[(date[i],messages[i]) for i in range(len(messages))]
    res.sort()
    return res
