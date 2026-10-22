"""Compose reviewed reports, authored scene evidence, and actual response decisions.

The resulting descriptions are saved in event_data.json. The game-file builder
uses those strings verbatim; it does not compose localization at runtime.
"""
from pathlib import Path
import json,re

HERE=Path(__file__).resolve().parent
P=HERE/'event_data.json';D=json.loads(P.read_text())
INTRODUCTIONS={c['code']:c['event_introduction'] for c in D['characters']}
SCENES={}
for line in (HERE/'scene_details.txt').read_text().splitlines():
 if line and not line.startswith('#'):
  key,text=line.split('|',1);assert key not in SCENES;SCENES[key]=text
assert len(SCENES)==360

# Remove author-facing chronology notes from player-facing reports.
fixes={
 'SIE-FH04':"Our investigator receives conflicting descriptions of a woman resembling Sienna near disturbed graves. Sienna has burned a necromantic cache and left a warning naming her twin Sofia.",
 'MAL-FH05':"Our border warden reports that Malakai's experimental flying machine carried stranded prospectors over a blocked pass. They returned with mineral samples and sketches of ruins he hopes might guide a future expedition to a lost hold.",
 'NAK-FA02':"Our frontier officer reports that Nakai held a mist-covered causeway long enough for an archaeological party to escape with inscribed stones. The survivors believe the abandoned enclosure beyond it could support a protected settlement.",
 'GRO-FA03':"Our border officer reports that Grombrindal rescued a mining party and left a copy of the pledge associated with his stand beside the Dwarf Slayer Gotrek Gurnisson and the Dwarf brewer Josef Bugman. The miners arrived with their survey records and a request for passage back to their kin.",
 'GRO-EH03':"Our jailer reports that Grombrindal opened the cells holding a captured Dwarf work party. A pledge recalling Karak Varn was carved into the broken gate, and copies of the prison roll have begun circulating among the prisoners' kin.",
}
departures={
 'GEL':["Gelt has left his instruments packed for another journey, and the escort cannot promise to detain him.","The masked alchemist has slipped away from the officials sent to demand an explanation.","The remaining attendants expect Gelt to be across the border before any summons can reach him.","Gelt's latest lodgings stand empty, leaving his hosts to settle the accounts after his departure.","No search party has persuaded the golden-masked visitor to remain for an audience."],
 'TEC':["Teclis has declined an audience and intends to continue his investigations elsewhere.","The Elf has left his conclusions in writing rather than wait upon another court debate.","The messengers sent to find Teclis returned with his notes and no promise that he would stay.","Teclis considers the immediate danger settled and has turned his attention to another distant disturbance.","The archmage's escort has already made preparations for travel beyond our jurisdiction."],
 'SNI':["The investigators found the suspected assassin's last refuge empty.","No guard can promise that the killer remains anywhere near the scene.","The messenger who delivered the evidence disappeared before a second question could be asked.","By the time the latest report was sealed, the trail had already passed beyond the search cordon.","The watch expects to find abandoned hiding places rather than an assassin waiting to be arrested."],
 'BUG':["Bugman's rangers have packed their crossbows and casks for another march.","The brewer has left the settlement of these claims to us while his rangers follow another trail.","Scouts last saw the rangers moving out with their baggage and a stubborn refusal to wait for officials.","Bugman has no intention of remaining until the local accounts are balanced.","The rangers' departing wagon bears the same brewery marks that first brought them into this affair."],
 'BAR':["Bardin has taken up his pack and resumed the search that brought him through our lands.","The ranger's last lodging contains a few chalk marks and no indication that he intends to wait for a summons.","Bardin has refused an official escort and set off along a route known better to him than to our patrols.","His hosts expect the Dwarf to continue travelling before the court's decision reaches them.","The ranger has left the immediate dispute behind and returned to his unfinished quest."],
 'HAR':["Harald has moved on in search of another worthy opponent.","The surviving scouts refuse to promise that any escort could compel the hammerer to remain.","His followers are already gathering their trophies for the next march.","Harald has shown no interest in waiting while officials settle the consequences of his passage.","The last report places the hammerer on a road leading beyond our patrols."],
 'ABH':["Abhorash has refused a position at court and continued his wandering.","The swordsman left before the local officers could arrange an audience.","No witness believes the stranger would accept confinement while the court debates his actions.","Abhorash has taken no payment that could oblige him to remain in our service.","The swordsman's hosts found his quarters empty when they returned with the governor's summons."],
 'ELS':["Elspeth has withdrawn from the officials sent to question her and will pursue her own investigations elsewhere.","Her attendants have offered no promise that the wizard will remain within reach of our messengers.","The Amethyst visitor has closed her temporary refuge and prepared to depart.","Elspeth has left a written warning in place of an audience and moved beyond the local watch.","No officer has persuaded the wizard to remain while the surviving papers are examined."],
 'WUL':["Wulfhart has already taken his scouts after another dangerous trail.","The hunter left his account with the local officials rather than remain for their ceremony.","Wulfhart's camp is packed, and its scouts refuse to be detained while another quarry is loose.","The last patrol to encounter the Huntsmarshal found him preparing to travel beyond our jurisdiction.","Wulfhart has entrusted the survivors to the authorities and resumed his hunt."],
 'GOF':["Gotrek refuses to wait for an audience, and Felix is gathering his papers for their next journey.","The pair have escaped the local watch and left their witnesses to present the account.","Felix's last message says that his companion will not remain while officials argue over the consequences.","The watch found their lodging empty, with the pair already following another road.","Neither the Slayer nor his chronicler has agreed to stay within reach of a government escort."],
 'REP':["Repanse has entrusted the immediate aftermath to the local authorities and resumed her pilgrimage.","Her companions are preparing to travel, and she has declined any office that would require her to remain.","The last messenger found Repanse leaving under her banner rather than waiting for another audience.","Repanse claims no right to govern this province and will continue beyond its borders.","The Damoiselle has left a petition in place of a demand for permanent command."],
 'SIE':["Sienna has slipped away before the authorities can turn their questions into another detention.","The Bright Wizard's temporary hearth is cold, and her travelling things are gone.","Sienna has made it clear that she will not remain under a local magistrate's supervision.","The last witness saw her taking the road before the watch could assemble another escort.","Her hosts have received no promise that the wandering wizard will return to answer the remaining accusations."],
 'MAL':["Malakai has packed the surviving tools and departed in search of another proving ground.","The engineer has left his corrections behind rather than remain for a guild hearing.","His assistants have loaded the remaining machinery for a journey beyond our officials' reach.","Malakai refuses to wait while the authorities debate the wisdom of his experiment.","The last messenger found the engineer's workshop shuttered and its travelling equipment gone."],
 'TYR':["Tyrion has mounted Malhandir and continued his journey without requesting an office or reward.","The Elf has left his testimony with the witnesses rather than await the governor's summons.","Tyrion's hosts cannot promise that a rider of his ability will remain within their patrol lines.","The champion has declined a prolonged stay while officials settle the disputes left behind.","The last report places Tyrion on the road, already beyond the escort sent to find him."],
 'GOR':["The white Saurus has left the officials behind and resumed his silent march.","No interpreter has persuaded Gor-Rok to remain while the court considers the report.","The last scouts saw the guardian moving away from the recovered site with no sign of accepting an escort.","Gor-Rok appears to consider his task complete, whatever remains for our administration to settle.","The patrol sent to observe him has returned after losing his trail beyond its accustomed routes."],
 'NAK':["Nakai has resumed his wandering, leaving no explanation of his next destination.","The giant's tracks lead away from the site, and no official has persuaded him to stay.","The custodians found that their unexpected guardian had departed before they could prepare an escort.","Scouts following Nakai turned back after his trail left the roads they knew.","His sudden departure offers as little explanation as his arrival."],
 'THA':["Thanquol has departed with his bodyguard before the inspectors can compare his claims with the surviving evidence.","The Grey Seer's demand for recognition arrived after he and Boneripper had already moved on.","No official has managed to keep Thanquol in one place long enough to settle the disputed accounts.","Thanquol has found another reason to travel, taking whichever Rat Ogre currently answers to Boneripper with him.","The pair have slipped beyond the search parties, leaving their hosts to explain the damage and divide the surviving spoils."],
 'GRO':["The white-bearded stranger vanished before the witnesses could arrange a formal audience.","The surviving officers found no trace of Grombrindal when they returned with the court's messenger.","Grombrindal has left the people he aided to fulfil their own obligations and continued his mysterious wandering.","No escort remains with the stranger, and his witnesses cannot agree on the road he took.","The last report ends with the White Dwarf's departure rather than a demand for land or office."],
}
openers=[
 "A sealed report from [war_adventurer_province.GetName] concerns {intro}.",
 "The latest dispatch from [war_adventurer_province.GetName] describes an incident linked to {intro}.",
 "Witnesses from [war_adventurer_province.GetName] have brought our officials an account concerning {intro}.",
 "Our officials in [war_adventurer_province.GetName] have forwarded a report about {intro}.",
 "A courier from [war_adventurer_province.GetName] has delivered testimony concerning {intro}.",
]
proposals=[
 ("Our officials ask us to {a}.","Others argue that we should instead {b}."),
 ("The council proposes that we {a}.","A second proposal would have us {b}."),
 ("One course would be to {a}.","Alternatively, we could {b}."),
 ("Our advisers recommend that we {a}.","There is also a proposal to {b}."),
 ("We could authorize our officials to {a}.","The competing request is to {b}."),
]

def sentences(text):
 return re.split(r'(?<=[.!?])\s+',text.strip())

for index,e in enumerate(D['events']):
 report=fixes.get(e['concept_id'],e['report'])
 report=report.replace('Your ','Our ').replace('your ','our ')
 # Report and evidence remain specific to this incident; no design commentary appears in-game.
 a=e['options'][0]['label'];b=e['options'][1]['label']
 a=a[0].lower()+a[1:];b=b[0].lower()+b[1:]
 first=sentences(openers[index%5].format(intro=INTRODUCTIONS[e['code']])+' '+report)
 second=sentences(SCENES[e['concept_id']])
 pair=proposals[(index//5)%5]
 decision=[pair[0].format(a=a,b=b),pair[1].format(a=a,b=b),departures[e['code']][(index+index//20)%5]]
 if len(first)+len(second)<=4:first+=second;second=[]
 second+=decision
 paragraphs=[first,second]
 if len(second)>4:paragraphs=[first,second[:2],second[2:]]
 elif index%4==0 and len(first)==4:paragraphs=[first[:2],first[2:],second]
 assert len(paragraphs) in (2,3)
 assert all(2<=len(p)<=4 for p in paragraphs),(e['concept_id'],paragraphs)
 assert 6<=sum(map(len,paragraphs))<=10
 e['description']='\n\n'.join(' '.join(p) for p in paragraphs)
 e['description_sentences']=sum(map(len,paragraphs))
 e['description_paragraphs']=len(paragraphs)
 assert not re.search(r'early echo|later associated|2502|mod adaptation|optional career',e['description'])

P.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print('Composed 360 concrete event descriptions with 6–10 sentences in 2–3 paragraphs.')
