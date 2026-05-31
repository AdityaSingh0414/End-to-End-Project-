import os

class DictionaryCorrector:
    def __init__(self):
        # A list of common English words to use as the base dictionary.
        # We also attempt to load an external dictionary file if present.
        self.dictionary = set()
        
        # Seed with common English words (all uppercase)
        common_words = [
            "THE", "OF", "AND", "TO", "IN", "IS", "YOU", "THAT", "IT", "HE", "WAS", "FOR", "ON", "ARE", "AS", 
            "WITH", "HIS", "THEY", "I", "AT", "BE", "THIS", "HAVE", "FROM", "OR", "ONE", "HAD", "BY", "WORD", 
            "BUT", "NOT", "WHAT", "ALL", "WERE", "WE", "WHEN", "YOUR", "CAN", "SAID", "THERE", "USE", "AN", 
            "EACH", "WHICH", "SHE", "DO", "HOW", "THEIR", "IF", "WILL", "UP", "OTHER", "ABOUT", "OUT", "MANY", 
            "THEN", "THEM", "THESE", "SO", "SOME", "HER", "WOULD", "MAKE", "LIKE", "HIM", "INTO", "TIME", "HAS", 
            "LOOK", "TWO", "MORE", "WRITE", "GO", "SEE", "NUMBER", "NO", "WAY", "COULD", "PEOPLE", "MY", "THAN", 
            "FIRST", "WATER", "BEEN", "CALL", "WHO", "OIL", "ITS", "NOW", "FIND", "LONG", "DOWN", "DAY", "DID", 
            "GET", "COME", "MADE", "MAY", "PART", "OVER", "NEW", "SOUND", "TAKE", "ONLY", "LITTLE", "WORK", "KNOW", 
            "PLACE", "YEAR", "LIVE", "ME", "BACK", "GIVE", "MOST", "VERY", "AFTER", "THING", "OUR", "JUST", "NAME", 
            "SENT", "MAN", "THINK", "SAY", "GREAT", "WHERE", "HELP", "THROUGH", "MUCH", "BEFORE", "LINE", "RIGHT", 
            "TOO", "MEAN", "OLD", "ANY", "SAME", "TELL", "BOY", "FOLLOW", "CAME", "WANT", "SHOW", "ALSO", "AROUND", 
            "FORM", "THREE", "SMALL", "END", "PUT", "HOME", "READ", "HAND", "PORT", "LARGE", "SPELL", "ADD", "EVEN", 
            "LAND", "HERE", "MUST", "BIG", "HIGH", "SUCH", "FOLLOW", "ACT", "WHY", "ASK", "MEN", "CHANGE", "WENT", 
            "LIGHT", "KIND", "OFF", "NEED", "HOUSE", "PICTURE", "TRY", "US", "AGAIN", "ANIMAL", "POINT", "MOTHER", 
            "WORLD", "NEAR", "BUILD", "SELF", "EARTH", "FATHER", "HEAD", "STAND", "OWN", "PAGE", "SHOULD", "COUNTRY", 
            "FOUND", "ANSWER", "SCHOOL", "GROW", "STUDY", "STILL", "LEARN", "PLANT", "COVER", "FOOD", "SUN", "FOUR", 
            "BETWEEN", "STATE", "KEEP", "EYE", "NEVER", "LAST", "LET", "THOUGHT", "CITY", "TREE", "CROSS", "FARM", 
            "HARD", "START", "MIGHT", "STORY", "SAW", "FAR", "SEA", "DRAW", "LEFT", "LATE", "RUN", "DON", "WHILE", 
            "PRESS", "CLOSE", "NIGHT", "REAL", "LIFE", "FEW", "NORTH", "OPEN", "SEEM", "TOGETHER", "NEXT", "WHITE", 
            "CHILDREN", "BEGIN", "GOT", "WALK", "EXAMPLE", "EASE", "PAPER", "GROUP", "ALWAYS", "MUSIC", "THOSE", "BOTH", 
            "MARK", "OFTEN", "LETTER", "UNTIL", "MILE", "RIVER", "CAR", "FEET", "CARE", "SECOND", "BOOK", "CARRY", 
            "TOOK", "RAIN", "EAT", "ROOM", "FRIEND", "BEGAN", "IDEA", "FISH", "MOUNTAIN", "STOP", "ONCE", "BASE", 
            "HEAR", "HORSE", "CUT", "SURE", "WATCH", "COLOR", "FACE", "WOOD", "MAIN", "ENOUGH", "PLAIN", "GIRL", 
            "USUAL", "YOUNG", "READY", "ABOVE", "EVER", "RED", "LIST", "THOUGH", "FEEL", "TALK", "BIRD", "SOON", 
            "BODY", "DOG", "FAMILY", "DIRECT", "POSE", "LEAVE", "SONG", "MEASURE", "DOOR", "PRODUCT", "BLACK", "SHORT", 
            "NUMERAL", "CLASS", "WIND", "QUESTION", "HAPPEN", "COMPLETE", "SHIP", "AREA", "HALF", "ROCK", "ORDER", 
            "FIRE", "SOUTH", "PROBLEM", "PIECE", "TOLD", "KNEW", "PASS", "SINCE", "TOP", "WHOLE", "KING", "SPACE", 
            "HEARD", "BEST", "HOUR", "BETTER", "TRUE", "DURING", "HUNDRED", "FIVE", "REMEMBER", "STEP", "EARLY", "HOLD", 
            "WEST", "GROUND", "INTEREST", "REACH", "FAST", "VERB", "SING", "LISTEN", "SIX", "TABLE", "TRAVEL", "LESS", 
            "MORNING", "TEN", "SIMPLE", "SEVERAL", "VOWEL", "TOWARD", "WAR", "LAY", "AGAINST", "PATTERN", "SLOW", 
            "CENTER", "LOVE", "PERSON", "MONEY", "MAP", "RAIN", "RULE", "GOVERN", "PULL", "COLD", "NOTICE", "VOICE", 
            "UNIT", "POWER", "TOWN", "FINE", "CERTAIN", "FLY", "FALL", "LEAD", "CRY", "DARK", "MACHINE", "NOTE", 
            "WAIT", "PLAN", "FIGURE", "STAR", "BOX", "NOUN", "FIELD", "REST", "CORRECT", "ABLE", "POUND", "DONE", 
            "BEAUTY", "DRIVE", "STOOD", "CONTAIN", "FRONT", "TEACH", "WEEK", "FINAL", "GAVE", "GREEN", "QUICK", "DEVELOP", 
            "OCEAN", "WARM", "FREE", "MINUTE", "STRONG", "SPECIAL", "MIND", "BEHIND", "CLEAR", "TAIL", "PRODUCE", "FACT", 
            "STREET", "INCH", "MULTIPLY", "NOTHING", "COURSE", "STAY", "WHEEL", "FULL", "FORCE", "BLUE", "OBJECT", "DECIDE", 
            "SURFACE", "DEEP", "MOON", "ISLAND", "FOOT", "SYSTEM", "BUSY", "TEST", "RECORD", "BOAT", "COMMON", "GOLD", 
            "POSSIBLE", "PLANE", "STEAD", "DRY", "WONDER", "LAUGH", "THOUSAND", "AGO", "RAN", "CHECK", "GAME", "SHAPE", 
            "EQUATE", "HOT", "MISS", "BROUGHT", "HEAT", "SNOW", "TIRE", "BRING", "YES", "DISTANT", "FILL", "EAST", 
            "PAINT", "LANGUAGE", "AMONG", "GRAND", "BALL", "YET", "WAVE", "DROP", "HEART", "AM", "PRESENT", "HEAVY", 
            "DANCE", "ENGINE", "POSITION", "ARM", "WIDE", "SAIL", "MATERIAL", "SIZE", "VARY", "SETTLE", "SPEAK", "WEIGHT", 
            "GENERAL", "ICE", "MATTER", "CIRCLE", "PAIR", "INCLUDE", "DIVIDE", "SYLLABLE", "FELT", "PERHAPS", "PICK", 
            "SUDDEN", "COUNT", "SQUARE", "REASON", "LENGTH", "ART", "SUBJECT", "REGION", "ENERGY", "HUNT", "PROBABLE", 
            "BED", "BROTHER", "EGG", "RIDE", "CELL", "BELIEVE", "FRACTION", "FOREST", "SIT", "RACE", "WINDOW", "STORE", 
            "SUMMER", "TRAIN", "SLEEP", "PROVE", "LONE", "LEG", "EXERCISE", "WALL", "CATCH", "MOUNT", "WISH", "SKY", 
            "BOARD", "JOY", "WINTER", "SAT", "WRITTEN", "WILD", "INSTRUMENT", "KEPT", "GLASS", "GRASS", "COW", "JOB", 
            "EDGE", "SIGN", "VISIT", "PAST", "SOFT", "FUN", "BRIGHT", "GAS", "WEATHER", "MONTH", "MILLION", "BEAR", 
            "FINISH", "HAPPY", "HOPE", "FLOWER", "CLOTHES", "STRANGE", "GONE", "TRADE", "MELODY", "TRIP", "OFFICE", "RECEIVE", 
            "ROW", "MOUTH", "EXACT", "SYMBOL", "DIE", "LEAST", "TROUBLE", "SHOUT", "EXCEPT", "WROTE", "SEED", "TONE", 
            "JOIN", "SUGGEST", "CLEAN", "BREAK", "LADY", "YARD", "RISE", "BAD", "BLOW", "OIL", "BLOW", "TOUCH", "MIX", 
            "TEAM", "WIRE", "COST", "LOST", "BROWN", "WEAR", "GARDEN", "EQUAL", "SENT", "CHOOSE", "FELL", "FIT", 
            "FLOW", "FAIR", "BANK", "COLLECT", "SAVE", "CONTROL", "DECIMAL", "GENTLE", "WOMAN", "CAPTAIN", "PRACTICE", 
            "SEPARATE", "DIFFICULT", "DOCTOR", "PLEASE", "PROTECT", "NOON", "WHOSE", "LOCATE", "RING", "CHARACTER", 
            "INSECT", "CAUGHT", "PERIOD", "BOARD", "VALLEY", "DOUBLE", "SEAT", "ARMY", "SECOND", "SAND", "SOIL", "ROLL", 
            "HEN", "SHARP", "FIGHT", "SILENT", "DETERMINE", "MILK", "SPEED", "METHOD", "ORGAN", "PAY", "AGE", "SECTION", 
            "DRESS", "CLOUD", "SURPRISE", "QUIET", "STONE", "TINY", "CLIMB", "COOL", "DESIGN", "POOR", "LOT", "EXPERIMENT", 
            "BOTTOM", "KEY", "IRON", "SINGLE", "STICK", "FLAT", "TWENTY", "SKIN", "SMILE", "CREASE", "HOLE", "TRADE", 
            "MELODY", "TRIP", "OFFICE", "RECEIVE", "ROW", "MOUTH", "EXACT", "SYMBOL", "DIE", "LEAST", "TROUBLE", "SHOUT", 
            "EXCEPT", "WROTE", "SEED", "TONE", "JOIN", "SUGGEST", "CLEAN", "BREAK", "LADY", "YARD", "RISE", "BAD", "BLOW"
        ]
        
        self.dictionary.update([w.upper() for w in common_words])
        
        # Try loading from a custom file if exists
        self.dict_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionary.txt')
        if os.path.exists(self.dict_file):
            try:
                with open(self.dict_file, 'r') as f:
                    for line in f:
                        word = line.strip().upper()
                        if word:
                            self.dictionary.add(word)
            except Exception as e:
                print(f"Error loading custom dictionary file: {e}")

    def correct_word(self, char_predictions, min_probability_threshold=0.65):
        """
        Corrects a sequence of character predictions into a dictionary word.
        - char_predictions: list of lists of (char, confidence) pairs.
          Example: [[('C', 0.8), ('G', 0.1), ...], [('A', 0.9), ...]]
        - Returns a tuple (corrected_word, confidence, method)
        """
        if not char_predictions:
            return "", 0.0, "none"
            
        # 1. Generate top-1 predicted word directly
        top1_word = "".join([preds[0][0] for preds in char_predictions if preds]).upper()
        # Compute joint probability of top-1
        top1_prob = 1.0
        for preds in char_predictions:
            if preds:
                top1_prob *= preds[0][1]
                
        # If top1_word is already in our dictionary, return it!
        if top1_word in self.dictionary:
            return top1_word, float(top1_prob), "direct"
            
        # 2. Perform Beam Search Joint Probability search among candidate combinations of top-5 predictions
        beam_size = 50
        candidates = [("", 1.0)] # List of (word_prefix, joint_probability)
        
        for char_preds in char_predictions:
            if not char_preds:
                continue
            next_candidates = []
            # Take top-5 predictions for this character
            for char, prob in char_preds[:5]:
                for prefix, joint_prob in candidates:
                    next_candidates.append((prefix + char.upper(), joint_prob * prob))
            # Sort by joint probability descending and keep beam_size
            candidates = sorted(next_candidates, key=lambda x: x[1], reverse=True)[:beam_size]
            
        # Search candidates in dictionary
        valid_dictionary_matches = []
        for word, joint_prob in candidates:
            if word in self.dictionary:
                valid_dictionary_matches.append((word, joint_prob))
                
        if valid_dictionary_matches:
            # Sort by probability and return the best match
            valid_dictionary_matches = sorted(valid_dictionary_matches, key=lambda x: x[1], reverse=True)
            best_match, best_prob = valid_dictionary_matches[0]
            # If the joint probability is acceptable, accept it
            if best_prob >= min_probability_threshold * top1_prob:
                return best_match, float(best_prob), "joint_probability"
                
        # 3. Levenshtein Fallback
        # If no valid dictionary match is found or confidence is too low, find the word with minimal edit distance
        best_fallback_word, min_dist = self.find_closest_levenshtein(top1_word)
        
        # Calculate a pseudo-confidence score for fallback based on edit distance
        # Max edit distance relative to target length
        word_len = len(top1_word)
        if word_len > 0:
            match_score = max(0.1, 1.0 - (min_dist / word_len))
        else:
            match_score = 0.1
            
        # Combine the model top-1 raw probability with the matching score
        fallback_conf = float(top1_prob * match_score)
        
        # Only apply fallback if distance is reasonably small (e.g. less than half the word length, min 1)
        max_allowed_dist = max(1, word_len // 2)
        if min_dist <= max_allowed_dist:
            return best_fallback_word, fallback_conf, "levenshtein"
            
        # If fallback is too far, keep the original top-1 prediction
        return top1_word, float(top1_prob), "raw_unmatched"

    def find_closest_levenshtein(self, target_word):
        """
        Finds the closest word in the dictionary to the target_word using Levenshtein distance.
        """
        target_word = target_word.upper()
        target_len = len(target_word)
        best_word = target_word
        min_dist = float('inf')
        
        # Optimize: search only words with similar lengths (+/- 2 characters)
        for dict_word in self.dictionary:
            if abs(len(dict_word) - target_len) > 2:
                continue
                
            dist = self.levenshtein_distance(target_word, dict_word)
            if dist < min_dist:
                min_dist = dist
                best_word = dict_word
                if min_dist == 1: # Can't get better unless distance is 0, but we checked that
                    pass
                    
        return best_word, min_dist

    @staticmethod
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return DictionaryCorrector.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
            
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
