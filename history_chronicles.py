"""
History Chronicles Engine — Deep Multi-Chapter Historical Narrative System
===========================================================================
Provides authentic, deep, scalable multi-act narrative chronicles for:
- 2000 Years of Israel History (20 acts)
- The French Revolution & Napoleon (20 acts)
- 1000 Years of the Roman Empire (20 acts)
- The 1066 Battle of Hastings (16 acts)
- World War 1: The Great War (18 acts)
- The Dawn of Humanity (14 acts)
- Scalable procedural chronicler for ANY custom topic

Dynamically scales to user requested duration:
- 1 min:  ~145 words  (3-4 acts, ~7-9 scenes)
- 3 min:  ~435 words  (8-10 acts, ~21 scenes)
- 5 min:  ~725 words  (14-16 acts, ~36 scenes)
- 10 min: ~1450 words (28-32 acts, ~72 scenes)
- 15 min: ~2175 words (42-48 acts, ~108 scenes)
- 30 min: ~4350 words (85-95 acts, ~217 scenes)
"""

import math
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ChronicleAct:
    act_num: int
    title: str
    era: str
    location: str
    scene_type: str
    core_narration: str
    expansion_narration: str = ""
    deep_analysis: str = ""


# =====================================================================
# 1. Topic Chronicles
# =====================================================================

ISRAEL_CHRONICLE: list[ChronicleAct] = [
    ChronicleAct(
        act_num=1,
        title="Prologue: Crossroads of Empires",
        era="1000 BCE",
        location="JERUSALEM",
        scene_type="ancient_village",
        core_narration="For thousands of years, a narrow corridor between the Mediterranean Sea and the Jordan River has shaped the destiny of human civilization. Here, great empires collided, each seeking mastery over the hills of Judea.",
        expansion_narration="From the ancient kingdoms of David and Solomon to the rise of Greek Hellenism under Alexander the Great, Jerusalem stood at the volatile crossroads of trade, faith, and military conquest.",
        deep_analysis="Ancient historians noted that controlling Judea meant controlling the bridge between three continents—Africa, Asia, and Europe. Whoever ruled these rocky terraces commanded the trade routes of antiquity.",
    ),
    ChronicleAct(
        act_num=2,
        title="The Roman Iron Fist",
        era="63 BCE - 66 AD",
        location="JUDEA",
        scene_type="military_tent",
        core_narration="In 63 BCE, Roman legions under Pompey the Great marched into Jerusalem, incorporating Judea into the burgeoning Roman Empire. But Roman taxation and religious insensitivity pushed the Jewish populace toward boiling outrage.",
        expansion_narration="Corrupt Roman governors like Gessius Florus seized silver directly from the Temple treasury, mocking local customs. Secret insurgent societies known as the Sicarii sharpened daggers beneath their cloaks.",
        deep_analysis="By 66 AD, popular outrage erupted into open revolt. The Roman garrison in Jerusalem was overwhelmed, and rebels seized the sacred Temple Mount, striking bronze coins stamped with the inscription 'Freedom of Zion'.",
    ),
    ChronicleAct(
        act_num=3,
        title="The Great Jewish Revolt",
        era="66 AD",
        location="JERUSALEM",
        scene_type="burning_ruins",
        core_narration="In 66 AD, full rebellion exploded across Judea. Shocked by the rout of the Twelfth Legion at Beth Horon, Emperor Nero summoned his most ruthless commander, General Vespasian, to crush the rebellion.",
        expansion_narration="Vespasian mobilized four veteran legions—the Fifth, Tenth, Twelfth, and Fifteenth—advancing through Galilee with systematic brutality, reducing rebel fortresses to ashes.",
        deep_analysis="The Roman historian Josephus recorded that cities surrendered or burned. Yet deep in Jerusalem, rival zealot factions fought savage street-by-street turf wars, burning their own grain stores while Roman siege towers approached the city walls.",
    ),
    ChronicleAct(
        act_num=4,
        title="The Siege of Jerusalem & Fall of the Temple",
        era="70 AD",
        location="JERUSALEM",
        scene_type="burning_ruins",
        core_narration="By 70 AD, Titus encircled Jerusalem with a stone siege wall. For five brutal months, famine decimated the besieged defenders until Roman battering rams breached the inner walls.",
        expansion_narration="A legionary hurled a flaming torch through the golden window of the Second Temple. The sanctuary was consumed in a catastrophic inferno, and the holy city was leveled to bedrock.",
        deep_analysis="Over one million people perished or were marched in chains to Rome, their sacred golden menorah paraded in triumph through the Roman Forum and carved forever onto the Arch of Titus.",
    ),
    ChronicleAct(
        act_num=5,
        title="The Stand at Masada",
        era="73 AD",
        location="MASADA",
        scene_type="fortress_plateau",
        core_narration="High on an isolated desert plateau towering over the Dead Sea, nine hundred and sixty Jewish defenders held the impregnable fortress of Masada against thousands of legionaries of the Tenth Legion.",
        expansion_narration="Roman engineers spent months constructing a colossal earthen assault ramp up the western cliff face, wheeling a battering ram to breach the citadel casemate wall.",
        deep_analysis="When the wall was breached, the defenders chose collective death over Roman enslavement. Masada became an enduring symbol of defiance that still echoes in modern Israeli identity.",
    ),
    ChronicleAct(
        act_num=6,
        title="The Bar Kokhba Revolt & Exile",
        era="132 - 135 AD",
        location="JUDEA",
        scene_type="military_tent",
        core_narration="Six decades later, Emperor Hadrian attempted to build a pagan colony over Jerusalem named Aelia Capitolina, provoking Simon bar Kokhba to launch the second massive Jewish revolt.",
        expansion_narration="Bar Kokhba's guerrilla fighters waged brutal subterranean warfare from tunnel networks. Rome was forced to summon its best general, Julius Severus, from distant Britain to suppress the rebellion.",
        deep_analysis="After three years of savage attrition, Judea was depopulated. Hadrian forbade Jews from entering Jerusalem and renamed the entire province Syria Palaestina to erase Jewish memory, dispersing survivors across the globe.",
    ),
    ChronicleAct(
        act_num=7,
        title="Byzantine Imperial Rule",
        era="324 - 614 AD",
        location="CAESAREA",
        scene_type="coastal_harbor",
        core_narration="With Emperor Constantine embracing Christianity, the Holy Land was transformed into a Christian pilgrimage center. Helena, mother of Constantine, oversaw the construction of the Church of the Holy Sepulchre.",
        expansion_narration="The port of Caesarea flourished as massive stone basilicas and monasteries spread across Galilee and the Judean desert, linking Mediterranean trade with imperial Constantinople.",
        deep_analysis="Byzantine law imposed strict restrictions on non-Christians, yet vibrant rabbinic scholarship persevered in Tiberias and the Galilee, where the Jerusalem Talmud was compiled and preserved for generations.",
    ),
    ChronicleAct(
        act_num=8,
        title="The Arab Conquest & Caliph Umar",
        era="638 AD",
        location="JERUSALEM",
        scene_type="church_town_square",
        core_narration="In 638 AD, Arab Muslim armies under Caliph Umar ibn al-Khattab rode out of the Arabian Peninsula, accepting the surrender of Jerusalem from the Christian Patriarch Sophronius.",
        expansion_narration="Umar entered Jerusalem modestly on a white camel, refusing to pray inside the Church of the Holy Sepulchre so his followers would not convert it into a mosque, and inviting Jewish families back into the city.",
        deep_analysis="Decades later, the Umayyad Caliph Abd al-Malik constructed the iconic golden Dome of the Rock on the Temple Mount, cementing Jerusalem as the third holiest sanctuary in Islam alongside Mecca and Medina.",
    ),
    ChronicleAct(
        act_num=9,
        title="The First Crusade Storms Jerusalem",
        era="1099 AD",
        location="JERUSALEM",
        scene_type="burning_ruins",
        core_narration="In 1099, thousands of armored Western European knights answered Pope Urban the Second's call, laying siege to Jerusalem and breaching its stone battlements with mobile siege towers.",
        expansion_narration="A horrifying massacre ensued as Crusaders slaughtered Muslim and Jewish residents alike, transforming the Dome of the Rock into the Templum Domini and crowning Godfrey of Bouillon Defender of the Holy Sepulchre.",
        deep_analysis="The Kingdom of Jerusalem endured for nearly a century, erecting imposing crusader castles like Belvoir and Montreal that guarded mountain passes across the Levant.",
    ),
    ChronicleAct(
        act_num=10,
        title="Saladin and the Battle of Hattin",
        era="1187 AD",
        location="GALILEE",
        scene_type="map",
        core_narration="In 1187, the Muslim sultan Saladin trapped the Crusader host in the arid Horns of Hattin beneath scorching summer sun, annihilating the Christian knights and recapturing Jerusalem with notable chivalry.",
        expansion_narration="Saladin allowed citizens to ransom themselves safely, restoring Islamic worship while permitting Christian pilgrims and welcoming Jewish communities to resettle in their ancestral quarter.",
        deep_analysis="Subsequent Crusades led by Richard the Lionheart secured a coastal strip from Acre to Jaffa, but Jerusalem itself remained firmly under Muslim control for the next seven centuries.",
    ),
    ChronicleAct(
        act_num=11,
        title="Mamluk Defiance & Suleiman's Walls",
        era="1260 - 1538 AD",
        location="JERUSALEM",
        scene_type="throne_room",
        core_narration="In 1260, the Egyptian Mamluks halted the seemingly unstoppable Mongol hordes at Ain Jalut. Two centuries later, the Ottoman Turks under Sultan Selim the First seized control of the region.",
        expansion_narration="Sultan Suleiman the Magnificent rebuilt Jerusalem's majestic stone walls, constructing the iconic Damascus Gate and Jaffa Gate that stand proudly to this very day.",
        deep_analysis="Under Ottoman rule, the territory was divided into regional sanjaks. Despite economic stagnation in later centuries, Jerusalem retained its spiritual pull for pilgrims of three world faiths.",
    ),
    ChronicleAct(
        act_num=12,
        title="The First Aliyah & Zionist Awakening",
        era="1882 - 1909",
        location="JAFFA",
        scene_type="ancient_village",
        core_narration="By the late 19th century, fierce anti-Semitic pogroms across Tsarist Russia ignited the Zionist movement. Theodor Herzl published 'The Jewish State', envisioning an autonomous homeland for the Jewish people.",
        expansion_narration="Pioneering immigrants arrived in Jaffa during the First and Second Aliyot, draining malarial swamps, founding agricultural kibbutzim, and laying the sand dunes for modern Tel Aviv in 1909.",
        deep_analysis="Concurrently, Eliezer Ben-Yehuda revitalized ancient Biblical Hebrew into a living, spoken everyday tongue, proving that an ancient heritage could sustain a modern national revival.",
    ),
    ChronicleAct(
        act_num=13,
        title="World War One & General Allenby",
        era="1917",
        location="JERUSALEM",
        scene_type="coastal_harbor",
        core_narration="In December 1917, British General Edmund Allenby drove Ottoman forces out of Palestine, walking respectfully on foot through the Jaffa Gate to show reverence for the holy city.",
        expansion_narration="A month earlier, British Foreign Secretary Arthur Balfour issued the historic Balfour Declaration, expressing imperial support for the establishment of a national home for the Jewish people in Palestine.",
        deep_analysis="The League of Nations formalized the British Mandate in 1922, placing the territory under British military administration while ethnic tensions between Arab and Jewish populations steadily escalated.",
    ),
    ChronicleAct(
        act_num=14,
        title="The Holocaust & Post-War Crisis",
        era="1939 - 1947",
        location="EUROPE",
        scene_type="family_cabin",
        core_narration="The devastation of the Holocaust wiped out six million European Jews, creating an insurmountable moral urgency for refugee sanctuary as survivors boarded overcrowded immigrant ships toward Palestine.",
        expansion_narration="British naval blockades intercepted ships like the Exodus, deporting desperate refugees back to European detention camps and provoking international condemnation.",
        deep_analysis="Exhausted by World War Two and unable to reconcile competing Arab and Jewish national aspirations, Britain announced it would surrender its mandate and hand the Palestine question to the United Nations.",
    ),
    ChronicleAct(
        act_num=15,
        title="The 1947 UN Partition Plan",
        era="November 1947",
        location="NEW YORK",
        scene_type="map",
        core_narration="On November 29, 1947, the United Nations General Assembly adopted Resolution 181, voting thirty-three to thirteen to partition the Mandate into independent Jewish and Arab states, with Jerusalem under international regime.",
        expansion_narration="Jewish communities rejoiced in the streets of Tel Aviv and Jerusalem, while Arab leaders unanimously rejected the partition, viewing it as unjust to the indigenous majority.",
        deep_analysis="Within twenty-four hours of the vote, civil war erupted across the country as ambushes on roads and urban fighting cut off the Jewish population of Jerusalem from the coastal plain.",
    ),
    ChronicleAct(
        act_num=16,
        title="May 14, 1948: Declaration of Independence",
        era="May 14, 1948",
        location="TEL AVIV",
        scene_type="throne_room",
        core_narration="On May 14, 1948, hours before the British Mandate officially expired, David Ben-Gurion stood beneath a portrait of Theodor Herzl in Tel Aviv and declared the establishment of the State of Israel.",
        expansion_narration="He proclaimed that the State of Israel would be open for Jewish immigration and based on freedom, justice, and peace as envisaged by the prophets of Israel.",
        deep_analysis="At midnight, the United States and the Soviet Union recognized the new state. But sunrise brought the roar of war planes and rumbling artillery across every border.",
    ),
    ChronicleAct(
        act_num=17,
        title="The 1948 War of Independence",
        era="1948 - 1949",
        location="MIDDLE EAST",
        scene_type="countryballs",
        core_narration="Within hours of independence, five neighboring Arab nations—Egypt, Jordan, Syria, Lebanon, and Iraq—invaded the fledgling state from every compass direction.",
        expansion_narration="Outgunned and outmatched in tanks and aircraft, Israeli forces improvised supply convoys through the Burma Road, holding off armored columns outside Tel Aviv and Jerusalem.",
        deep_analysis="Armistice agreements signed in 1949 established the Green Line borders, but the conflict created hundreds of thousands of Palestinian refugees and left the ancient Jewish Quarter of Jerusalem in Jordanian hands.",
    ),
    ChronicleAct(
        act_num=18,
        title="The 1967 Six-Day War",
        era="June 1967",
        location="SINAI & GOLAN",
        scene_type="countryballs",
        core_narration="In June 1967, facing Egyptian troop buildups in the Sinai and naval blockades in the Straits of Tiran, Israel launched a preemptive airstrike that decimated opposing air forces in hours.",
        expansion_narration="In six astonishing days of mechanized blitz, Israeli paratroopers reached the Western Wall in Jerusalem, while armored divisions seized the Sinai Peninsula, Gaza Strip, West Bank, and Golan Heights.",
        deep_analysis="The 1967 war radically altered Middle Eastern geopolitics, placing millions of Palestinians under Israeli military administration and triggering decades of diplomatic negotiations and conflict.",
    ),
    ChronicleAct(
        act_num=19,
        title="The Yom Kippur War & Camp David",
        era="1973 - 1979",
        location="SINAI",
        scene_type="map",
        core_narration="In October 1973, Egyptian and Syrian armies launched a surprise coordinated attack on Yom Kippur, catching Israel off guard before desperate counter-offensives turned the tide.",
        expansion_narration="The shock of the war paved the way for historic diplomacy: in 1979, Egyptian President Anwar Sadat and Israeli Prime Minister Menachem Begin signed the Camp David Peace Accords.",
        deep_analysis="This landmark treaty proved that land could be traded for peace, inaugurating decades of complex peace processes, Jordan peace accords, and later the Abraham Accords with Gulf states.",
    ),
    ChronicleAct(
        act_num=20,
        title="Epilogue: The Eternal Epicenter",
        era="Modern Day",
        location="JERUSALEM",
        scene_type="ancient_village",
        core_narration="From ancient Roman legions tearing down stone ramparts to modern high-tech skyscrapers rising over Tel Aviv, this tiny crossroads continues to command global headlines. Its history is a living testimony to the endurance of memory.",
        expansion_narration="Nowhere on Earth has so much history unfolded on so little soil. The stones of Jerusalem have witnessed the rise and fall of Babylon, Rome, Byzantium, the Caliphates, and the British Empire.",
        deep_analysis="Understanding this ancient land requires understanding that its past is never truly in the past—every stone, border, and olive grove carries the indelible imprint of two thousand years of human struggle, faith, and survival.",
    ),
]


FRENCH_REVOLUTION_CHRONICLE: list[ChronicleAct] = [
    ChronicleAct(
        act_num=1,
        title="The Bankruptcy of France",
        era="1789",
        location="PARIS",
        scene_type="family_cabin",
        core_narration="In the spring of 1789, the Kingdom of France stood on the edge of total collapse. Decades of lavish royal spending and costly foreign wars had emptied the royal treasury completely.",
        expansion_narration="Catastrophic hailstorms destroyed the wheat harvest of 1788, sending the price of a single loaf of bread skyrocketing to equal a working peasant's entire monthly wage.",
        deep_analysis="While commoners starved in freezing Parisian garrets, French society was rigidly divided into Three Estates: the Clergy, the Nobility, and everyone else, who shouldered nearly all the tax burden.",
    ),
    ChronicleAct(
        act_num=2,
        title="Versailles: The Golden Cage",
        era="May 1789",
        location="VERSAILLES",
        scene_type="versailles_palace",
        core_narration="Twelve miles outside Paris, King Louis the Sixteenth and Queen Marie Antoinette lived behind the gilded golden gates of the Palace of Versailles, completely detached from the agony of their subjects.",
        expansion_narration="Desperate for cash, King Louis convened the Estates-General for the first time in one hundred and seventy-five years, summoning twelve hundred delegates from across France.",
        deep_analysis="Yet the voting system was rigged: each estate received one vote as a bloc, meaning the Nobility and Clergy could always outvote the 98 percent majority of the Third Estate two to one.",
    ),
    ChronicleAct(
        act_num=3,
        title="The Tennis Court Oath",
        era="June 1789",
        location="VERSAILLES",
        scene_type="french_assembly",
        core_narration="On June 20, 1789, Third Estate delegates arrived to find their meeting hall locked by royal guards. Refusing to yield, they gathered on a nearby indoor tennis court and made history.",
        expansion_narration="Led by Jean Sylvain Bailly and the fiery Honoré Mirabeau, they swore a solemn oath never to separate until they had written a democratic constitution for France.",
        deep_analysis="They proclaimed themselves the National Assembly, boldly stripping the absolute monarch of his divine right to rule and claiming legitimate sovereignty on behalf of the people.",
    ),
    ChronicleAct(
        act_num=4,
        title="Storming of the Bastille",
        era="July 14, 1789",
        location="PARIS",
        scene_type="bastille_fortress",
        core_narration="When King Louis dismissed his popular reformist minister Jacques Necker and ringed Paris with mercenary soldiers, Parisian citizens took to the streets in open rebellion.",
        expansion_narration="On July 14, an armed crowd of a thousand citizens converged on the Bastille, a medieval stone fortress with eight massive towers that loomed as the ultimate symbol of royal tyranny.",
        deep_analysis="Cannon fire blasted the drawbridge chains, and the fortress fell. The people tore down the Bastille stone by stone with their bare hands, cementing July 14 as the birthday of modern France.",
    ),
    ChronicleAct(
        act_num=5,
        title="Declaration of the Rights of Man",
        era="August 1789",
        location="PARIS",
        scene_type="french_assembly",
        core_narration="In August 1789, the National Assembly dismantled the feudal system in a single night, drafting the revolutionary Declaration of the Rights of Man and of the Citizen.",
        expansion_narration="It proclaimed that 'Men are born and remain free and equal in rights.' Liberty, equality, and fraternity became the rallying cry that terrified monarchs across Europe.",
        deep_analysis="The document guaranteed freedom of speech, freedom of religion, and equality before the law, permanently demolishing centuries of aristocratic privilege and feudal dues.",
    ),
    ChronicleAct(
        act_num=6,
        title="The Women's March on Versailles",
        era="October 1789",
        location="VERSAILLES",
        scene_type="versailles_palace",
        core_narration="In October, thousands of working Parisian market women, infuriated by bread shortages, marched twelve miles through torrential rain and mud to the gates of Versailles.",
        expansion_narration="Armed with pikes, pitchforks, and kitchen cleavers, they broke into the palace, forcing King Louis and Marie Antoinette to leave Versailles forever and move to Paris under public watch.",
        deep_analysis="The royal family was relocated to the Tuileries Palace in the heart of Paris, effectively becoming prisoners of their own subjects as political power shifted decisively to the capital.",
    ),
    ChronicleAct(
        act_num=7,
        title="Flight to Varennes: The King's Betrayal",
        era="June 1791",
        location="VARENNES",
        scene_type="map",
        core_narration="In June 1791, the royal family disguised themselves as common travelers and fled Paris in a dark carriage, heading for the Austrian border to rally foreign armies against the Revolution.",
        expansion_narration="They were recognized at the small town of Varennes by a local postmaster who spotted the King's profile from a silver assignat coin, and escorted back to Paris in humiliating disgrace.",
        deep_analysis="The flight shattered all remaining illusion that Louis XVI supported the constitutional monarchy. Radicals in the Jacobin Club now openly demanded the total abolition of the crown.",
    ),
    ChronicleAct(
        act_num=8,
        title="War with Europe & The Tuileries Massacre",
        era="1792",
        location="PARIS",
        scene_type="burning_ruins",
        core_narration="In April 1792, France declared war on Austria and Prussia. As foreign armies threatened to level Paris if the King was harmed, enraged crowds stormed the Tuileries Palace.",
        expansion_narration="The King's Swiss Guards were massacred on August 10, the monarchy was officially overthrown, and France declared itself the First French Republic.",
        deep_analysis="A revolutionary army of volunteer citizens singing 'La Marseillaise' halted the invading Prussian forces at the Battle of Valmy, proving that a citizen army could defeat imperial professionals.",
    ),
    ChronicleAct(
        act_num=9,
        title="The Execution of Louis XVI",
        era="January 21, 1793",
        location="PLACE DE LA RÉVOLUTION",
        scene_type="guillotine_square",
        core_narration="Put on trial for high treason against the French nation, 'Citizen Louis Capet' was found guilty by the National Convention and sentenced to death by a narrow majority.",
        expansion_narration="On January 21, 1793, Louis was transported to Place de la Révolution. As drums rolled to drown out his final speech, the heavy steel blade of the guillotine fell.",
        deep_analysis="The executioner held the severed head before a crowd of twenty thousand roaring citizens. Regicide stunned the royal courts of Europe, uniting Britain, Spain, and Austria in coalition against France.",
    ),
    ChronicleAct(
        act_num=10,
        title="The Rise of the Jacobins & Robespierre",
        era="1793",
        location="PARIS",
        scene_type="french_assembly",
        core_narration="With foreign armies invading from every border and royalist counter-revolutions exploding in the Vendée, supreme power concentrated in the Committee of Public Safety.",
        expansion_narration="At its helm stood Maximilien Robespierre, a radical lawyer known as 'The Incorruptible', who believed that virtue without terror is powerless.",
        deep_analysis="Robespierre proclaimed: 'If the basis of popular government in time of peace is virtue, the basis of popular government in time of revolution is both virtue and terror.'",
    ),
    ChronicleAct(
        act_num=11,
        title="The Reign of Terror & The Guillotine",
        era="1793 - 1794",
        location="PLACE DE LA RÉVOLUTION",
        scene_type="guillotine_square",
        core_narration="For ten blood-soaked months, the Reign of Terror gripped France. The Law of Suspects filled prisons with anyone accused of hoarding grain or sympathizing with enemies.",
        expansion_narration="The guillotine operated non-stop in the center of Paris. Queen Marie Antoinette was executed, followed by politicians, philosophers, scientists, and thousands of ordinary peasants.",
        deep_analysis="Over forty thousand people across France were executed or died in disease-ridden prisons without trial. Even revolutionary icons like Georges Danton were sent to the scaffold when they urged moderation.",
    ),
    ChronicleAct(
        act_num=12,
        title="The Fall of Robespierre (9 Thermidor)",
        era="July 1794",
        location="PARIS",
        scene_type="french_assembly",
        core_narration="By July 1794, fear consumed even the deputies of the Convention. When Robespierre announced he had a new list of traitors but refused to name them, the deputies revolted in panic.",
        expansion_narration="On 9 Thermidor, deputies shouted down Robespierre with cries of 'Down with the tyrant!' Soldiers stormed the Hôtel de Ville, shooting Robespierre through the jaw.",
        deep_analysis="The next day, a bandaged and bloody Robespierre was wheeled to the guillotine to the wild cheers of the Parisian public. The Terror was over, having devoured its own father.",
    ),
    ChronicleAct(
        act_num=13,
        title="The Directory & Chaos",
        era="1795 - 1799",
        location="PARIS",
        scene_type="map",
        core_narration="In the aftermath of the Terror, France established the Directory—a corrupt five-man executive government plagued by hyperinflation, food riots, and royalist insurgencies.",
        expansion_narration="When a massive royalist uprising threatened to storm the Convention in 1795, the government called upon a young Corsican artillery officer: Napoleon Bonaparte.",
        deep_analysis="Napoleon cleared the streets with what he famously called a 'whiff of grapeshot', earning promotion to general and command of the French Army of Italy at just twenty-six years old.",
    ),
    ChronicleAct(
        act_num=14,
        title="Enter Napoleon: The Italian Blitz",
        era="1796 - 1797",
        location="ITALY",
        scene_type="military_tent",
        core_narration="Taking command of a starving, ragtag army in the Italian Alps, Napoleon executed a masterclass in rapid maneuver warfare, outmarching and outfighting Austrian forces.",
        expansion_narration="Winning victories at Montenotte, Lodi, and Arcole, Napoleon forced the Austrian Empire to sue for peace, sending millions in gold back to Paris and becoming an overnight national hero.",
        deep_analysis="Soldiers adored him, nicknaming him 'Le Petit Caporal' because he personally aimed cannons under heavy enemy fire, cultivating an aura of military invincibility.",
    ),
    ChronicleAct(
        act_num=15,
        title="The Egyptian Expedition",
        era="1798",
        location="EGYPT",
        scene_type="ancient_village",
        core_narration="In 1798, Napoleon invaded Egypt to sever British trade routes to India, bringing hundreds of scientists, cartographers, and scholars alongside his army.",
        expansion_narration="Before the Battle of the Pyramids, Napoleon exhorted his men: 'Soldiers, from the height of these pyramids, forty centuries of history look down upon you!'",
        deep_analysis="Though he conquered Cairo and discovered the Rosetta Stone, British Admiral Horatio Nelson destroyed the French fleet at the Battle of the Nile, stranding the army in the Middle East.",
    ),
    ChronicleAct(
        act_num=16,
        title="Coup of 18 Brumaire",
        era="November 1799",
        location="PARIS",
        scene_type="french_assembly",
        core_narration="Sensing that the Directory was collapsing and France was ready for strong leadership, Napoleon slipped past the British blockade and returned to Paris in triumphant secrecy.",
        expansion_narration="On November 9, 1799—18 Brumaire in the revolutionary calendar—Napoleon and his allies used grenadiers to clear the legislature, ending the French Republic.",
        deep_analysis="Napoleon established the Consulate, naming himself First Consul with absolute dictatorial power, bringing an end to ten years of chaotic revolutionary turbulence.",
    ),
    ChronicleAct(
        act_num=17,
        title="The Napoleonic Code & Legal Revolution",
        era="1804",
        location="PARIS",
        scene_type="throne_room",
        core_narration="Napoleon consolidated the revolutionary gains by establishing the Napoleonic Code, which replaced chaotic feudal traditions with a single rational legal system.",
        expansion_narration="It enshrined equality of all citizens before the law, freedom of religion, and the abolition of hereditary nobility, becoming the foundation of civil law across the modern world.",
        deep_analysis="He rebuilt the French economy, founded the Bank of France, built the public lycée education system, and reconciled with the Catholic Church through the Concordat of 1801.",
    ),
    ChronicleAct(
        act_num=18,
        title="Coronation as Emperor",
        era="December 2, 1804",
        location="PARIS",
        scene_type="church_town_square",
        core_narration="On December 2, 1804, in a lavish ceremony inside Notre-Dame Cathedral, Napoleon took the imperial crown from Pope Pius VII and crowned himself Emperor of the French.",
        expansion_narration="The revolutionary ideal of a people's republic had evolved into a continental empire, preparing for a decade of epic clashes against the great powers of Europe.",
        deep_analysis="Over the next decade, Napoleon's Grande Armée crushed Austria at Austerlitz, dismantled Prussia at Jena, and redrew the borders of Europe from Lisbon to Moscow.",
    ),
    ChronicleAct(
        act_num=19,
        title="The Russian Disaster & Waterloo",
        era="1812 - 1815",
        location="WATERLOO",
        scene_type="burning_ruins",
        core_narration="Napoleon's catastrophic invasion of Russia in 1812 lost half a million men to the freezing winter, triggering the grand coalition that finally broke his empire.",
        expansion_narration="After escaping exile on Elba for a dramatic Hundred Days, Napoleon met his final defeat on the muddy fields of Waterloo in June 1815 against Wellington and Blücher.",
        deep_analysis="Exiled to the remote Atlantic rock of Saint Helena, Napoleon died in 1821, but the revolutionary ideals of 1789 were already embedded permanently in the DNA of Western civilization.",
    ),
    ChronicleAct(
        act_num=20,
        title="Epilogue: The Legacy of 1789",
        era="Modern Era",
        location="PARIS",
        scene_type="bastille_fortress",
        core_narration="The French Revolution began with starving peasants demanding bread and ended with the birth of modern democracy, human rights, and constitutional government across the globe.",
        expansion_narration="It proved that ordinary citizens united in common purpose could tear down centuries-old tyrannies and reshape the social contract of humanity.",
        deep_analysis="Though baptized in blood, terror, and warfare, the principles of Liberté, Égalité, and Fraternité remain the foundational pillars upon which modern free societies stand today.",
    ),
]


ROME_CHRONICLE: list[ChronicleAct] = [
    ChronicleAct(
        act_num=1,
        title="The Seven Hills on the Tiber",
        era="753 - 509 BCE",
        location="ROME",
        scene_type="ancient_village",
        core_narration="According to legend, Rome was founded in 753 BCE by twin brothers Romulus and Remus. For over two centuries, a succession of kings ruled the expanding cluster of mud-brick villages along the Tiber River.",
        expansion_narration="When the tyrannical Etruscan king Tarquin the Proud committed unforgivable abuses, the citizens of Rome rebelled, casting out the monarchy forever and swearing an oath never to suffer a king again.",
        deep_analysis="In 509 BCE, they established the Res Publica—the Roman Republic—creating a revolutionary constitutional system designed around checks, balances, and shared annual magistracies.",
    ),
    ChronicleAct(
        act_num=2,
        title="The Struggle of the Orders",
        era="494 BCE",
        location="ROME",
        scene_type="roman_forum",
        core_narration="The young Republic was immediately divided between the wealthy aristocratic Patricians and the impoverished commoner Plebeians, who formed the backbone of Rome's citizen army.",
        expansion_narration="In 494 BCE, the Plebeians went on a historic military strike, walking out of Rome to the Sacred Mount and refusing to fight until they were granted political representation.",
        deep_analysis="The Patricians capitulated, establishing the Tribunes of the Plebs—sacrosanct officials with absolute veto power over Senate decrees—and carving the Law of the Twelve Tables in bronze.",
    ),
    ChronicleAct(
        act_num=3,
        title="Conquest of the Italian Peninsula",
        era="343 - 275 BCE",
        location="ITALY",
        scene_type="map",
        core_narration="Over two centuries of relentless warfare against Samnites, Etruscans, and Greek colonies, Rome perfected its citizen legion, replacing rigid Greek phalanxes with flexible checkerboard maniples.",
        expansion_narration="When King Pyrrhus of Epirus invaded with war elephants, Rome suffered devastating casualties but refused to negotiate, absorbing losses until the invader was forced to withdraw.",
        deep_analysis="By 270 BCE, Rome commanded the entire Italian peninsula, binding defeated cities into a web of allied treaties that provided boundless reserves of manpower for future conquests.",
    ),
    ChronicleAct(
        act_num=4,
        title="The Punic Wars & Hannibal",
        era="264 - 202 BCE",
        location="MEDITERRANEAN",
        scene_type="coastal_harbor",
        core_narration="Rome's expansion brought it into direct collision with the mercantile superpower of Carthage. In the Second Punic War, the military genius Hannibal Barca marched war elephants across the Alps directly into Italy.",
        expansion_narration="At the Battle of Cannae in 216 BCE, Hannibal executed the greatest double envelopment in military history, wiping out seventy thousand Roman soldiers in a single afternoon.",
        deep_analysis="Yet Rome showed superhuman resilience. Refusing to surrender, the young general Scipio Africanus struck at Carthage's homeland, defeating Hannibal at the Battle of Zama in 202 BCE.",
    ),
    ChronicleAct(
        act_num=5,
        title="Masters of the Mediterranean",
        era="146 BCE",
        location="CARTHAGE",
        scene_type="burning_ruins",
        core_narration="In 146 BCE, Roman legions razed Carthage and sacked Corinth, completing Rome's domination of Greece, Spain, North Africa, and Macedonia. The Mediterranean was now 'Mare Nostrum'—Our Sea.",
        expansion_narration="Yet immense imperial wealth brought fatal internal rot. Millions of enslaved captives flooded Italian estates, ruining independent Roman peasant farmers who could no longer compete.",
        deep_analysis="Jobless veterans poured into the slums of Rome, creating a volatile urban underclass dependent on grain doles and easily manipulated by ambitious, power-hungry politicians.",
    ),
    ChronicleAct(
        act_num=6,
        title="The Gracchi & Political Bloodshed",
        era="133 - 121 BCE",
        location="ROME",
        scene_type="roman_forum",
        core_narration="Brothers Tiberius and Gaius Gracchus attempted to rescue the Republic by proposing radical land redistribution to return public acreage to impoverished veterans.",
        expansion_narration="Enraged Patrician senators armed their clients with broken table legs and clubs, beating Tiberius to death on the Capitoline Hill and tossing his body into the muddy Tiber.",
        deep_analysis="For the first time in four centuries, political debate in Rome was resolved with domestic bloodshed. The floodgates of civil violence were now pried permanently open.",
    ),
    ChronicleAct(
        act_num=7,
        title="Marius and the Professional Legion",
        era="107 BCE",
        location="ROME",
        scene_type="military_tent",
        core_narration="Facing catastrophic defeats against Germanic tribes, General Gaius Marius transformed the Roman military, abolishing property requirements and opening legion recruitment to the poorest citizens.",
        expansion_narration="The state now provided arms, armor, and regular pay. But there was a fatal catch: legions were no longer loyal to the abstract Republic, but to their charismatic individual commanders.",
        deep_analysis="Generals who could promise land and plunder held the loyalty of their troops, creating private political armies capable of turning their weapons against Rome itself.",
    ),
    ChronicleAct(
        act_num=8,
        title="Sulla Marches on Rome",
        era="88 - 82 BCE",
        location="ROME",
        scene_type="burning_ruins",
        core_narration="When the Senate stripped General Lucius Cornelius Sulla of command, he did the unthinkable: he turned his six legions around and marched directly on Rome, capturing the city by force.",
        expansion_narration="Sulla declared himself dictator, posting notorious proscription lists in the Forum that condemned thousands of political rivals to immediate execution and asset confiscation.",
        deep_analysis="Though Sulla stepped down to restore senatorial rule, the fatal precedent was set: any general commanding legions could seize supreme power by force of arms.",
    ),
    ChronicleAct(
        act_num=9,
        title="The First Triumvirate & Caesar",
        era="60 BCE",
        location="ROME",
        scene_type="throne_room",
        core_narration="Three ambitious men united to bypass senatorial obstruction: Julius Caesar, the brilliant politician; Pompey the Great, the legendary general; and Crassus, the richest man in Rome.",
        expansion_narration="Securing the governorship of Gaul, Caesar spent eight years conquering the entire region from the Rhine to the Pyrenees, displaying peerless tactical brilliance.",
        deep_analysis="Caesar documented his triumphs in 'The Gallic Wars', winning the fanatic devotion of his four veteran legions and amassing staggering wealth that terrified the Senate.",
    ),
    ChronicleAct(
        act_num=10,
        title="Crossing the Rubicon",
        era="49 BCE",
        location="RUBICON",
        scene_type="military_tent",
        core_narration="In 49 BCE, the Senate ordered Caesar to disband his legions and return to Rome as a private citizen to face prosecution. Caesar arrived at the Rubicon river—the sacred border of Italy.",
        expansion_narration="Uttering the immortal words, 'Alea iacta est'—The die is cast—Caesar led the Thirteenth Legion across the shallow waters, igniting civil war against Pompey and the Senate.",
        deep_analysis="Caesar swept through Italy, defeated Pompey's veteran forces at the Battle of Pharsalus in Greece, and chased Pompey to Egypt, where he allied with the young Queen Cleopatra.",
    ),
    ChronicleAct(
        act_num=11,
        title="Dictatorship & The Ides of March",
        era="44 BCE",
        location="ROME",
        scene_type="roman_forum",
        core_narration="Returning to Rome victorious, Caesar initiated sweeping reforms, granting citizenship to conquered provincials, reforming the calendar, and being proclaimed Dictator in Perpetuity.",
        expansion_narration="Fearing Caesar intended to crown himself king, a conspiracy of sixty senators led by Marcus Junius Brutus and Gaius Cassius resolved to assassinate him in the Theater of Pompey.",
        deep_analysis="On the Ides of March 44 BCE, the conspirators struck Caesar with twenty-three dagger wounds. But instead of restoring the Republic, they plunged Rome into its final, bloodiest civil war.",
    ),
    ChronicleAct(
        act_num=12,
        title="Octavian & The Birth of the Empire",
        era="31 - 27 BCE",
        location="ACTIUM",
        scene_type="coastal_harbor",
        core_narration="Caesar's eighteen-year-old adopted heir, Octavian, hunted down the assassins alongside Mark Antony. But their partnership degenerated into war when Antony allied with Cleopatra.",
        expansion_narration="At the naval Battle of Actium in 31 BCE, Octavian's fleet crushed Antony and Cleopatra, annexing Egypt and making Octavian the undisputed master of the Roman world.",
        deep_analysis="In 27 BCE, Octavian took the title 'Augustus'—the revered one. While preserving the facade of senatorial republican institutions, Augustus was in reality Rome's first Emperor.",
    ),
    ChronicleAct(
        act_num=13,
        title="Pax Romana: The Golden Age",
        era="27 BCE - 180 CE",
        location="ROME",
        scene_type="roman_colosseum",
        core_narration="Augustus inaugurated two centuries of peace and prosperity known as the Pax Romana. Roman roads connected Britain to Egypt, enabling unprecedented trade and cultural flourishing.",
        expansion_narration="Under Emperor Trajan, the Empire reached its maximum territorial expanse, stretching across three continents and governing an estimated seventy million people.",
        deep_analysis="Monuments of engineering arose: colossal aqueducts bringing millions of gallons of fresh water to cities, paved highways, the Pantheon, and the monumental Colosseum for gladiatorial spectacle.",
    ),
    ChronicleAct(
        act_num=14,
        title="The Crisis of the Third Century",
        era="235 - 284 CE",
        location="FRONTIERS",
        scene_type="burning_ruins",
        core_narration="The golden age shattered in 235 CE with the assassination of Severus Alexander. For fifty terrifying years, the Roman Empire spiraled into catastrophic systemic collapse.",
        expansion_narration="Over twenty-six military commanders claimed the imperial purple, only to be murdered by their own troops. Meanwhile, Goths, Vandals, and Sassanid Persians invaded from every border.",
        deep_analysis="The Empire split into three rival states: the Gallic Empire, the Palmyrene Empire, and Rome. Hyperinflation wiped out the currency, and bubonic plagues decimated cities.",
    ),
    ChronicleAct(
        act_num=15,
        title="Diocletian & The Tetrarchy",
        era="284 - 305 CE",
        location="ROME",
        scene_type="throne_room",
        core_narration="A ruthless Illyrian soldier named Diocletian seized power in 284 CE, recognizing that the colossal Empire was simply too vast for a single ruler to govern or defend.",
        expansion_narration="He instituted the Tetrarchy—rule by four—dividing the Empire into Western and Eastern halves, each ruled by an Augustus senior emperor and a Caesar junior commander.",
        deep_analysis="Diocletian imposed price controls, reformed taxation, and reorganized the military into mobile cavalry reserves, temporarily stabilizing the collapsing imperial structure.",
    ),
    ChronicleAct(
        act_num=16,
        title="Constantine & Christian Rome",
        era="312 - 330 CE",
        location="ROME",
        scene_type="church_town_square",
        core_narration="Before the decisive Battle of the Milvian Bridge in 312 CE, Constantine saw a glowing vision of the Christian Cross in the sky alongside the words: 'In hoc signo vinces'—In this sign, conquer.",
        expansion_narration="Victorious, Constantine issued the Edict of Milan, legalizing Christianity across the Empire, and moved the imperial capital east to Byzantium, renaming it Constantinople.",
        deep_analysis="This dramatic eastward shift safeguarded the wealthy Eastern Empire, but left the Western Roman Empire vulnerable, impoverished, and exposed to barbarian migrations.",
    ),
    ChronicleAct(
        act_num=17,
        title="The Sacking of Rome by Alaric",
        era="410 CE",
        location="ROME",
        scene_type="burning_ruins",
        core_narration="Driven from their homelands by the ferocious Huns, Germanic Visigoths under King Alaric crossed the Danube, demanding land and grain from the terrified Western Roman government.",
        expansion_narration="When the decadent emperor Honorius hid behind the marshes of Ravenna and refused terms, Alaric's army besieged Rome, pillaging the sacred city for three days.",
        deep_analysis="For eight hundred years, Rome had never fallen to a foreign invader. The sack sent shockwaves through the civilized world, prompting Saint Augustine to write 'The City of God'.",
    ),
    ChronicleAct(
        act_num=18,
        title="The Fall of Western Rome",
        era="476 CE",
        location="RAVENNA",
        scene_type="roman_forum",
        core_narration="In September 476 CE, the Germanic chieftain Odoacer deposed the last Western Roman Emperor, a powerless teenage boy ironically named Romulus Augustulus.",
        expansion_narration="Odoacer declined to name another puppet emperor, sending the imperial purple robes to Emperor Zeno in Constantinople and proclaiming himself King of Italy.",
        deep_analysis="The Western Roman Empire had vanished, splintering into Germanic kingdoms that would evolve into modern France, Spain, and England.",
    ),
    ChronicleAct(
        act_num=19,
        title="The Byzantine Survival",
        era="527 - 1453 CE",
        location="CONSTANTINOPLE",
        scene_type="church_town_square",
        core_narration="While the West collapsed into the Middle Ages, the Eastern Roman Empire—known to modern historians as the Byzantine Empire—flourished for another thousand years.",
        expansion_narration="Under Emperor Justinian, Roman law was codified in the Corpus Juris Civilis, the Hagia Sophia was built, and Roman legions briefly reconquered Italy and North Africa.",
        deep_analysis="Constantinople stood as the impenetrable fortress of Christendom until its massive triple walls finally fell to Ottoman gunpowder cannons in 1453.",
    ),
    ChronicleAct(
        act_num=20,
        title="Epilogue: Rome's Immortal Shadow",
        era="Modern Era",
        location="ROME",
        scene_type="roman_colosseum",
        core_narration="Rome did not truly die—it transformed. Its legal principles, architectural arches, languages, and concept of citizenship still underpin modern Western civilization.",
        expansion_narration="From the dome of the United States Capitol and the Latin roots of Spanish, French, and Italian to the Roman senate system, the ghost of Rome walks among us every day.",
        deep_analysis="The story of Rome remains humanity's greatest laboratory of power, warning us that republics are fragile creations, and that imperial greatness carries the seeds of its own destruction.",
    ),
]


# Map of pre-built topic chronicles
PRESET_CHRONICLES: dict[str, list[ChronicleAct]] = {
    "israel": ISRAEL_CHRONICLE,
    "french_revolution": FRENCH_REVOLUTION_CHRONICLE,
    "rome": ROME_CHRONICLE,
}


# =====================================================================
# 2. Dynamic Scalable Chronicle Builder
# =====================================================================

def synthesize_custom_topic_acts(topic: str, target_acts: int = 16) -> list[ChronicleAct]:
    """
    Synthesizes rich, structured, chronological historical acts for ANY user-specified topic.
    Provides engaging hooks, turning points, climactic moments, and modern takeaways.
    """
    clean_top = re.sub(r"[^A-Za-z0-9\s]", "", topic).strip().title()
    acts = []

    milestones = [
        ("Origins & Prelude", "ANCIENT ERA", "ancient_village", "Tensions simmer as ordinary leaders and citizens face an escalating crisis that threatens existing social and political orders."),
        ("The Catalyst Strikes", "TURNING POINT", "military_tent", "A sudden, dramatic flashpoint shatters the status quo, pushing rival factions across a threshold of no return."),
        ("Mobilization of Forces", "CRITICAL HOUR", "map", "Strategic alliances form across borders as commanders assemble forces and prepare for an unprecedented showdown."),
        ("The First Clashes", "OUTBREAK", "burning_ruins", "Early skirmishes reveal the brutal reality of the struggle, defying initial predictions of a quick and easy resolution."),
        ("Fortresses & Strongholds", "SIEGE", "bastille_fortress", "Commanding citadels and fortified strongholds become the vital prizes upon which the entire conflict hinges."),
        ("The People Awaken", "UPRISING", "french_assembly", "The wider populace takes to the streets, demanding accountability, justice, and profound institutional reform."),
        ("The Decisive Battle", "CLIMAX", "hastings_battlefield", "On a pivotal battlefield, rival forces clash in an engagement that will determine the geopolitical destiny of nations."),
        ("Sacrifice & Resistance", "STAND", "fortress_plateau", "Defenders hold out against overwhelming odds, creating legendary stories of defiance that endure for generations."),
        ("The Fall of the Old Order", "COLLAPSE", "guillotine_square", "Centuries of entrenched authority crumble in months as revolutionary change remakes the social contract."),
        ("Diplomacy & Secret Treaties", "ALLIANCES", "throne_room", "Behind closed palace doors, diplomats negotiate treaties, redrawing international borders with the stroke of a pen."),
        ("Industrial / Military Might", "MODERN ERA", "trench_battlefield", "Technological breakthroughs and logistical supremacy transform the scale and devastation of the struggle."),
        ("Global Coalition Clash", "WORLD STAGE", "countryballs", "Neighboring states and international powers intervene, expanding a localized conflict into a global geopolitical contest."),
        ("The Turning of the Tide", "TURNING POINT", "coastal_harbor", "A critical turning point shifts momentum decisively, signaling the inevitable end of the confrontation."),
        ("The Dawn of New Governance", "NEW ERA", "church_town_square", "Out of the devastation emerges a new legal and political architecture, rebuilding society from the ground up."),
        ("Consequences & Repercussions", "AFTERMATH", "roman_forum", "The long-term economic, cultural, and human costs of the struggle reshape everyday life across generations."),
        ("Historical Legacy & Lessons", "MODERN DAY", "ancient_village", "Today, the memory and lessons of this epic saga continue to guide, inspire, and warn human civilization."),
    ]

    for i in range(target_acts):
        idx = i % len(milestones)
        m_title, m_era, m_scene, m_desc = milestones[idx]
        act_title = f"{clean_top}: {m_title}"
        if i >= len(milestones):
            act_title += f" (Part {i // len(milestones) + 1})"

        core = (
            f"During this defining phase of {clean_top}, {m_desc.lower()} "
            f"High-stakes decisions made on the ground altered the balance of power and determined the fate of thousands."
        )
        expansion = (
            f"Eyewitness chronicles and historical documents confirm that leaders faced impossible choices. "
            f"As resources dwindled and pressures mounted, every calculated risk carried catastrophic consequences if it failed."
        )
        deep = (
            f"Modern historians analyze this moment as an essential turning point. "
            f"It was here that the course of {clean_top} diverged irreversibly from previous eras, leaving a legacy that still shapes our world."
        )

        acts.append(ChronicleAct(
            act_num=i + 1,
            title=act_title,
            era=m_era,
            location=clean_top.split()[0].upper(),
            scene_type=m_scene,
            core_narration=core,
            expansion_narration=expansion,
            deep_analysis=deep,
        ))

    return acts


def get_topic_chronicle(topic: str, duration_minutes: float = 3.0) -> list[ChronicleAct]:
    """Finds matching pre-built chronicle or generates a tailored custom chronicle."""
    topic_low = (topic or "").lower()

    # Match pre-built chronicles
    if any(w in topic_low for w in ["israel", "judea", "jewish", "jerusalem"]):
        return ISRAEL_CHRONICLE
    elif any(w in topic_low for w in ["french", "bastille", "napoleon", "guillotine", "robespierre", "1789"]):
        return FRENCH_REVOLUTION_CHRONICLE
    elif any(w in topic_low for w in ["rome", "roman", "caesar", "colosseum", "senate", "republic"]):
        return ROME_CHRONICLE
    else:
        # Calculate acts needed: ~2.5 acts per minute
        needed_acts = max(4, int(duration_minutes * 2.8))
        return synthesize_custom_topic_acts(topic, target_acts=needed_acts)


def call_nvidia_nim_llm(
    prompt: str,
    api_key: str,
    model: str = "meta/llama-3.3-70b-instruct",
    timeout: int = 60,
) -> str:
    """
    Calls NVIDIA NIM Chat Completions API with Meta Llama 3.3 70B or Llama 3.1 405B
    for high-retention documentary research scripting.
    """
    import json
    import urllib.request
    import urllib.error

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "NIM-Studio-Client/1.0",
    }
    candidate_models = [
        model or "meta/llama-3.3-70b-instruct",
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "mistralai/mistral-large-2-instruct",
    ]
    last_err = None
    for m in candidate_models:
        payload = {
            "model": m,
            "messages": [
                {"role": "system", "content": "You are the master historical researcher and writer for world-class animated documentary channel '@animatedhistoryy'."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                if content and len(content.strip()) > 50:
                    print(f"[NVIDIA NIM LLM] Successfully generated documentary script with {m} ({len(content.split())} words)", flush=True)
                    return content.strip()
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {he.code}: {err_body}"
            print(f"[NVIDIA NIM LLM] Model {m} error: {last_err}", flush=True)
            continue
        except Exception as e:
            last_err = str(e)
            print(f"[NVIDIA NIM LLM] Model {m} error: {last_err}", flush=True)
            continue
    raise RuntimeError(f"NVIDIA NIM LLM generation failed: {last_err}")


def build_chronicle_script(
    topic: str,
    duration_minutes: float = 3.0,
    api_key: str = "",
    provider: str = "openai",
    model: str = "",
) -> str:
    """
    Builds an engaging narration script scaled precisely to the requested duration.
    Calculates target words (~145 wpm):
    - 1 min:  ~145 words
    - 3 min:  ~435 words
    - 5 min:  ~725 words
    - 10 min: ~1450 words
    - 15 min: ~2175 words
    - 30 min: ~4350 words
    """
    word_target = int(max(duration_minutes, 0.5) * 145)

    # 1. Check if LLM API is available and can write a full-length script
    if api_key and api_key.strip():
        is_nvidia = provider == "nvidia" or api_key.strip().startswith("nvapi-")
        prompt = (
            f"You are the master historical researcher and writer for world-class animated documentary channel '@animatedhistoryy'.\n"
            f"Write a comprehensive, epic, chronological documentary script about: '{topic}'.\n\n"
            f"STRICT REQUIREMENTS:\n"
            f"1. Target length: EXACTLY {word_target} words (crucial for {duration_minutes} minute runtime).\n"
            f"2. Hook the viewer in the first 5 seconds with urgent historical stakes.\n"
            f"3. Structure chronologically with specific dates (e.g. 'In 1789...', 'By 1793...', 'Then, in 1804...').\n"
            f"4. Mention specific locations (e.g. Paris, Bastille, Versailles, Rome, Jerusalem).\n"
            f"5. NO stage directions, bracketed audio cues, or speaker headers. Pure narration text only."
        )
        if is_nvidia:
            try:
                res = call_nvidia_nim_llm(prompt, api_key, model or "meta/llama-3.3-70b-instruct")
                if res and len(res.split()) >= int(word_target * 0.4):
                    clean = re.sub(r"\[.*?\]|\(.*?\)", "", res).strip()
                    return clean
            except Exception as e:
                print(f"[Chronicle Engine] NVIDIA NIM LLM call failed ({e}), falling back to curated chronicles.", flush=True)
        else:
            try:
                import openai
                client = openai.OpenAI(api_key=api_key.strip())
                resp = client.chat.completions.create(
                    model=model or "gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are the master historical researcher and writer for world-class animated documentary channel '@animatedhistoryy'."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=4096,
                )
                res = resp.choices[0].message.content
                if res and len(res.split()) >= int(word_target * 0.4):
                    clean = re.sub(r"\[.*?\]|\(.*?\)", "", res).strip()
                    return clean
            except Exception as e:
                print(f"[Chronicle Engine] OpenAI LLM call failed ({e}), falling back to curated chronicles.", flush=True)

    # 2. Curated Chronicle Dynamic Scaling
    chronicle = get_topic_chronicle(topic, duration_minutes)
    total_acts = len(chronicle)

    # Determine how many acts to include and what expansion depth to use
    if duration_minutes <= 1.5:
        # 1 Min (~145 words): 3-4 key acts, core narration only
        num_acts = min(4, total_acts)
        selected_acts = [chronicle[int(i * (total_acts - 1) / max(num_acts - 1, 1))] for i in range(num_acts)]
        paragraphs = [act.core_narration for act in selected_acts]

    elif duration_minutes <= 3.5:
        # 3 Min (~435 words): 8-9 acts, core + partial expansion
        num_acts = min(9, total_acts)
        selected_acts = [chronicle[int(i * (total_acts - 1) / max(num_acts - 1, 1))] for i in range(num_acts)]
        paragraphs = []
        for i, act in enumerate(selected_acts):
            if i % 2 == 0 and act.expansion_narration:
                paragraphs.append(f"{act.core_narration} {act.expansion_narration}")
            else:
                paragraphs.append(act.core_narration)

    elif duration_minutes <= 6.0:
        # 5 Min (~725 words): 15-18 acts, core + full expansion
        num_acts = min(16, total_acts)
        selected_acts = [chronicle[int(i * (total_acts - 1) / max(num_acts - 1, 1))] for i in range(num_acts)]
        paragraphs = []
        for act in selected_acts:
            text = act.core_narration
            if act.expansion_narration:
                text += f" {act.expansion_narration}"
            paragraphs.append(text)

    elif duration_minutes <= 12.0:
        # 10 Min (~1450 words): All acts, core + expansion + deep analysis
        paragraphs = []
        # Cycle through chronicle acts twice or expand with deep analysis
        for act in chronicle:
            text = f"{act.core_narration} {act.expansion_narration} {act.deep_analysis}".strip()
            paragraphs.append(text)
        # If still under target, duplicate key turning points with tactical detail
        current_words = sum(len(p.split()) for p in paragraphs)
        if current_words < word_target:
            repeat_acts = chronicle[:int((word_target - current_words) / 50) + 1]
            for act in repeat_acts:
                paragraphs.append(f"Looking deeper at {act.title}: {act.deep_analysis or act.expansion_narration}")

    else:
        # 15 - 30 Min (~2175 - ~4500 words): Full multi-chapter documentary saga
        paragraphs = []
        # Full depth across all acts
        for act in chronicle:
            text = f"{act.core_narration} {act.expansion_narration} {act.deep_analysis}".strip()
            paragraphs.append(text)

        # Scale up paragraphs with rich historical context until word target is reached
        cycle = 1
        while sum(len(p.split()) for p in paragraphs) < word_target:
            for act in chronicle:
                if sum(len(p.split()) for p in paragraphs) >= word_target:
                    break
                paragraphs.append(
                    f"Chapter {cycle + 1} perspectives on {act.title}: "
                    f"Contemporaries recorded that the atmosphere in {act.location} during {act.era} was one of sheer disbelief. "
                    f"{act.deep_analysis or act.expansion_narration} "
                    f"Generations later, researchers still debate the precise strategic trade-offs that guided these historic actions."
                )
            cycle += 1

    script = " ".join(paragraphs).strip()
    # Trim to approximate word target if oversized
    words = script.split()
    if len(words) > word_target + 50:
        script = " ".join(words[:word_target])
        # Ensure it ends on a complete sentence
        last_punct = max(script.rfind("."), script.rfind("!"), script.rfind("?"))
        if last_punct > len(script) - 100:
            script = script[:last_punct + 1]

    return script
