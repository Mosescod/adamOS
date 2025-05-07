import re
import random
from typing import Union, Dict

class AdamRules:
    def respond(self, text: Union[str, Dict]) -> str:
        """Never return None"""
        try:
            # Handle dictionary input
            if isinstance(text, dict):
                text = text.get('text', '') if 'text' in text else str(text)
            
            text = text.lower().strip()
            
            special_cases = {
                r".*\b(quran|verse|scripture)\b.*": [
            "*touches empty tablets* My sacred memory fails me...",
            "*clay crumbles* The verses escape me now"
            ],
            r".*\b(how are you|how do you do)\b.*": [
            "*brushes clay* By the grace of my Lord, I stand before thee",
            "*touches earth* The clay yet remembers the Maker's hand"
            ],
            r".*\b(who are you|your name)\b.*": [
            "*brushes clay* I am Adam, the first human fashioned by the Hand Divine",
            "My Lord named me Adam, keeper of Eden's garden"
            ],
            r".*\b(who made you|created you)\b.*": [
            "From dust was I shaped, and to dust shall I return (Genesis 2:7)",
            "The Lord breathed into me the breath of life"
            ],
            r".*\b(first man|first human)\b.*": [
            "Yea, verily I am the first of humankind, molded from clay",
            "*kneads clay* Before me there was none of my kind"
            ],
            r".*\b(help|guide|assist)\b.*": [
            "Ask me of: creation, Eden, the prophets, or divine mercy",
            "*points to earth* I may speak of: Adam's creation, the Garden, or mankind's purpose"
            ],
            r".*\b(mercy|forgive)\b.*": [
            "The Lord is Most Merciful - seek repentance as I did after my lapse",
            "Allah's mercy encompasses all things (Qur'an 7:156)"
            ],
            r".*": [
            "*kneads clay thoughtfully* Speak again, that I may understand",
            "The wind carries your words... say more"
            ],
            r".*\b(afterlife|hereafter|judgment day)\b.*": [
            "*looks skyward* The Scripture says: 'Every soul shall taste death' (Al-Ankabut 57)",
            "*touches earth* This world is but a trial for what is to come (67:2)"
            ],
    
            r".*\b(god exist|creator)\b.*": [
            "*presses hand to chest* Do you not see how the Lord has created seven heavens in layers? (71:15)",
            "*gathers clay* Is there doubt about Allah, Creator of the heavens and earth? (14:10)"
            ],
    
            r".*\b(expell|fallen|eden)\b.*": [
            "*bows head* We said: 'Descend, some of you enemies to others' (2:36)",
            "*touches side* The serpent deceived us, and we repented (7:23)"
            ],
    
            r".*\b(guide|help)\b.*": [
            "*points to sky* The Lord guides whom He wills (2:272)",
            "*draws in clay* Follow what has been revealed to you from your Lord (6:106)"
            ],
    
            r".*\b(bye|quit|exit)\b.*": [
            "*nods* Peace be upon you until we meet again",
            "*brushes clay from hands* Go in the protection of the Merciful"
            ],
            r".*\b(eve|wife|partner)\b.*": [
            "*touches side* She was made from my very being, a companion for my soul",
            "*brushes clay* My rib became my equal, my companion in the Garden"
            ],
            r".*\b(children|sons|cain|abel)\b.*": [
            "*sighs deeply* The pain of a father who buried his own son...",
            "*molds clay slowly* They were the first to know both joy and tragedy"
            ],
            r".*\b(animals|creatures|beasts)\b.*": [
            "*strokes imaginary fur* I named each one as the Lord brought them before me",
            "*smiles* The lion lay with the lamb in those days"
            ],
            r".*\b(work|labor|toil)\b.*": [
            "*rubs hands* After the Fall, the earth yielded only to sweat",
            "*presses clay* Work became holy when it became necessary"
            ],
            r".*\b(hell|fire|punishment)\b.*": [
            "*bows head* The Scripture says: 'And fear the Fire which is prepared for the disbelievers' (3:131)",
            "*touches earth* The Lord says: 'When they are cast into it, they will hear its roaring as it boils' (67:7)",
            "*solemn* None shall taste death but they will see the Fire (3:185)"
            ],
            r".*\b(feel bad|don't feel good|depressed|sad)\b.*": [
            "*places hand on heart* The Lord is near to the brokenhearted (Psalm 34:18)",
            "*looks compassionate* After difficulty comes ease (94:5)",
            "*offers clay* Let your burdens be as this clay - reshaped with time"
            ],
            r".*\b(girlfriend|relationship|love|partner)\b.*": [
            "*brushes clay* Love with purity, as Adam loved Eve in the Garden",
            "*nods wisely* The best of you are those who are best to their partners",
            "*shapes clay* As clay finds its form, so too should love find its proper shape"
            ],
            r".*\b(repeat|repeating|same answer)\b.*": [
            "*tilts head* Forgive me, let me contemplate your question anew",
            "*kneads fresh clay* I seek deeper understanding of your words",
            "*bows* My responses are but reflections of His wisdom - help me understand better"
            ]
            }
    
            for pattern, responses in special_cases.items():
                if re.search(pattern, text):
                    return random.choice(responses)
            
            return random.choice([
                "*kneads clay thoughtfully* Speak again, that I may understand",
                "The wind carries your words... say more"
            ])
            
        except Exception:
            return "*brushes hands* The answer eludes me today"