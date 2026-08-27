#!/usr/bin/env python3
"""Pick a picture for each Latin flashcard, and leave the card blank rather than guess.

Same rule as the other two decks: strictest first, and a wrong picture is worse
than none. A picture printed on a card teaches a sense the word does not carry
and the learner cannot undo it.

Latin arrives third, which is its advantage. Both earlier decks are curated
against the same Traditional-Chinese gloss vocabulary, so a Latin word whose
meaning either of them has already pictured takes that picture: *ignis*, אֵשׁ and
πῦρ are all 「火」 and all want the flame. That transfer is free and it is exact,
because the match is on the Chinese meaning a human already approved, not on a
resemblance between the words.

Latin also carries a real English definition on every entry — Collins's for the
upper volume, Whitaker's for the lower — which the other two decks largely do
not. That makes name matching worth more here, and also more dangerous:
Whitaker's definitions run to six senses separated by semicolons, so only the
senses are tried, never the whole line, and the ambiguous-English blocklist the
Hebrew deck built applies unchanged.

Order:

1. hand-picked overrides, named by the emoji's own name so a bad entry fails loudly
2. Chinese-meaning transfer from the Hebrew and Greek maps
3. exact match on the emoji's own name, from the English gloss's senses
4. nothing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import match_flashcard_images as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/flashcards"
VOCAB = ROOT / "data/originalReaders/vocabulary/latin-2000.json"
OUTPUT = CACHE / "latin-card-images.json"

# Named by the emoji's own annotation, never by hexcode: a typo then fails loudly
# instead of printing whatever art happens to sit at that code point.  This is
# where the core vocabulary lives, and where the function words get the symbol
# that stands in for them.
OVERRIDES: dict[str, str] = {
    # 天主與教會
    "deus": "folded hands", "dominus": "folded hands", "christus": "latin cross",
    "spiritus": "dove", "ecclesia": "church", "sanctus": "smiling face with halo",
    "angelus": "baby angel", "diabolus": "smiling face with horns",
    "caelum": "cloud", "infernus": "fire", "anima": "dove",
    "gratia": "sparkles", "gloria": "glowing star", "fides": "latin cross",
    "spes": "anchor", "caritas": "red heart", "peccatum": "black heart",
    "oratio": "folded hands", "benedictio": "raised hand",
    # 禮儀
    "missa": "church", "altare": "church", "sacramentum": "sparkles",
    "baptismus": "droplet", "eucharistia": "bread", "hostia": "bread",
    "calix": "wine glass", "panis": "bread", "vinum": "wine glass",
    "crux": "latin cross", "campana": "bell", "candela": "candle",
    "liber": "closed book", "codex": "closed book", "epistula": "envelope",
    "psalmus": "musical notes", "cantus": "musical notes", "hymnus": "musical notes",
    # 聖統
    "papa": "man", "episcopus": "man", "sacerdos": "man", "presbyter": "older person",
    "diaconus": "man", "monachus": "man", "abbas": "older person",
    "frater": "man", "soror": "woman", "populus": "busts in silhouette",
    "rex": "crown", "regina": "crown", "regnum": "castle",
    # 人與身體
    "homo": "bust in silhouette", "vir": "man", "mulier": "woman",
    "puer": "boy", "puella": "girl", "infans": "baby", "senex": "older person",
    "pater": "man", "mater": "woman", "filius": "boy", "filia": "girl",
    "corpus": "bust in silhouette", "caro": "cut of meat", "sanguis": "drop of blood",
    "cor": "anatomical heart", "manus": "hand with fingers splayed",
    "pes": "foot", "oculus": "eye", "auris": "ear", "os": "mouth",
    "caput": "bust in silhouette", "lingua": "tongue", "dens": "tooth",
    # 自然
    "aqua": "droplet", "ignis": "fire", "terra": "globe showing Europe-Africa",
    "mare": "water wave", "sol": "sun", "luna": "crescent moon",
    "stella": "star", "lux": "light bulb", "tenebrae": "new moon",
    "ventus": "wind face", "pluvia": "cloud with rain", "nix": "snowflake",
    "nubes": "cloud", "mons": "mountain", "lapis": "rock", "arbor": "deciduous tree",
    "lignum": "wood", "flos": "cherry blossom", "herba": "herb",
    "fructus": "red apple", "semen": "seedling", "vinea": "grapes",
    "oliva": "olive", "triticum": "sheaf of rice", "hortus": "cherry blossom",
    "ager": "sheaf of rice", "desertum": "desert", "flumen": "water wave",
    "fons": "potable water", "via": "motorway", "porta": "door", "murus": "brick",
    # 動物
    "agnus": "ewe", "ovis": "ewe", "pastor": "man", "grex": "ewe",
    "bos": "ox", "equus": "horse", "asinus": "donkey", "canis": "dog face",
    "leo": "lion", "lupus": "wolf", "serpens": "snake", "columba": "dove",
    "avis": "bird", "piscis": "fish", "gallus": "rooster", "vermis": "worm",
    # 時間
    "dies": "sun", "nox": "night with stars", "annus": "calendar",
    "mensis": "calendar", "hora": "watch", "tempus": "hourglass done",
    "hodie": "calendar", "cras": "calendar", "vesper": "night with stars",
    "mane": "sunrise", "aeternus": "infinity",
    # 器物與生活
    "domus": "house", "civitas": "cityscape", "urbs": "cityscape",
    "templum": "classical building", "turris": "tokyo tower",
    "navis": "sailboat", "currus": "wheel", "gladius": "dagger",
    "scutum": "shield", "corona": "crown", "vestis": "t-shirt",
    "calceus": "running shoe", "mensa": "fork and knife with plate",
    "cibus": "fork and knife with plate", "lac": "glass of milk",
    "mel": "honey pot", "sal": "salt", "oleum": "olive",
    "aurum": "coin", "argentum": "coin", "pecunia": "money bag",
    "clavis": "key", "littera": "envelope",
    "nomen": "label", "numerus": "input numbers", "signum": "flagged point",
    # 動作
    "ambulo": "person walking", "curro": "person running", "sedeo": "person in lotus position",
    "dormio": "sleeping face", "video": "eye", "audio": "ear", "loquor": "speaking head",
    "scribo": "writing hand", "lego": "open book", "canto": "musical notes",
    "manduco": "fork and knife", "bibo": "cup with straw", "laboro": "hammer",
    "aedifico": "building construction", "pugno": "crossed swords",
    "morior": "skull", "nascor": "baby", "vivo": "sparkling heart",
    "amo": "red heart", "timeo": "fearful face", "gaudeo": "grinning face",
    "fleo": "crying face", "rideo": "grinning face", "doceo": "teacher",
    "disco": "student", "iudico": "balance scale", "rego": "crown",
    "sano": "hospital", "lavo": "shower", "veniо": "person walking",
    # 抽象與功能詞
    "non": "prohibited", "nullus": "prohibited", "omnis": "globe with meridians",
    "totus": "globe with meridians", "multus": "plus",
    "magnus": "up arrow", "parvus": "down arrow", "primus": "1st place medal",
    "novus": "new button", "vetus": "hourglass done", "verus": "check mark button",
    "falsus": "cross mark", "bonus": "thumbs up", "malus": "thumbs down",
    "sanctus_adj": "smiling face with halo", "beatus": "smiling face with halo",
    "pax": "dove", "bellum": "crossed swords", "mors": "skull",
    "vita": "sparkling heart", "veritas": "check mark button", "via_abstract": "motorway",
    "lex": "balance scale", "iustitia": "balance scale", "iudicium": "balance scale",
    "potestas": "flexed biceps", "virtus": "flexed biceps",
    "sapientia": "owl", "scientia": "graduation cap", "ratio": "brain",
    "quaestio": "red question mark", "responsum": "speech balloon",
    "initium": "green circle", "finis": "end arrow",
    "et": "plus", "sed": "left-right arrow", "si": "red question mark",
    "quia": "right arrow", "ergo": "right arrow", "usque": "right arrow",
    "semper": "infinity", "numquam": "prohibited", "iterum": "counterclockwise arrows button",
    # The second round: the highest-frequency words the corpus left uncovered.
    # Function words get the symbol that stands in for them, the way the Hebrew
    # deck gives לֹא the prohibition sign; an abstract noun gets a picture only
    # where one sense is plainly the word's own -- persona takes the theatre
    # masks because that is what the word first meant.
    "ab": "left arrow", "ad": "right arrow", "ex": "left arrow",
    "per": "right arrow", "post": "right arrow", "ante": "left arrow",
    "supra": "up arrow", "infra": "down arrow", "inter": "left-right arrow",
    "contra": "crossed swords", "sine": "prohibited", "cum": "people holding hands",
    "jus": "balance scale", "ius": "balance scale", "canon": "straight ruler",
    "persona": "performing arts", "officium": "briefcase",
    "auctoritas": "judge", "concilium": "busts in silhouette",
    "synodus": "busts in silhouette", "societas": "people holding hands",
    "monasterium": "castle", "claustrum": "castle",
    "doctrina": "open book", "doctor": "teacher", "magister": "teacher",
    "discipulus": "student", "schola": "school", "studium": "open book",
    "scriptura": "scroll", "textus": "scroll", "verbum": "speech balloon",
    "sermo": "speaking head", "vox": "megaphone", "silentium": "shushing face",
    "memoria": "brain", "mens": "brain", "intellectus": "brain",
    "voluntas": "flexed biceps", "libertas": "dove",
    "labor": "hammer and wrench", "opus": "hammer and wrench",
    "instrumentum": "gear", "ordo": "input numbers", "gradus": "ladder",
    "locus": "round pushpin", "spatium": "world map", "orbis": "globe with meridians",
    "provincia": "world map", "dioecesis": "world map",
    "sepulcrum": "headstone", "sepultura": "coffin", "medicus": "hospital",
    "morbus": "pill", "sanitas": "green heart", "dolor": "crying face",
    "gaudium": "grinning face", "tristitia": "crying face", "ira": "angry face",
    "misericordia": "smiling face with open hands", "iustus": "balance scale",
    "sacrificium": "fire", "incensum": "fire", "cinis": "fire",
    "clamor": "megaphone", "cantica": "musical note", "tuba": "trumpet",
    "cithara": "harp", "tympanum": "drum",
    "numerus_ord": "input numbers", "mensura": "straight ruler",
    "figura": "triangular ruler", "linea": "straight ruler",
    "initium_alt": "green circle", "medius": "record button",
    # Third round.  An abstract adverb is left blank on purpose -- quasi, modo,
    # scilicet, potius have no picture that is theirs rather than an
    # illustration of a sentence they might appear in -- but a concrete noun
    # buried among them does not have to be.
    "uxor": "couple with heart", "maritus": "couple with heart",
    "matrimonium": "ring", "nuptiae": "ring", "sponsa": "ring",
    "religio": "folded hands", "haereticus": "cross mark",
    "epistola": "envelope", "historia": "books", "fabula": "books",
    "provincia_civil": "world map", "negotium": "briefcase",
    "possessio": "money bag", "pecunia_alt": "money bag",
    "periculum": "warning", "error": "confused face", "iniuria": "anguished face",
    "injuria": "anguished face", "aetas": "hourglass not done",
    "futurus": "spiral calendar", "praesentia": "round pushpin",
    "communitas": "people hugging", "populus_alt": "busts in silhouette",
    "civilis": "office building", "politicus": "classical building",
    "publicus": "busts in silhouette", "legatus": "postal horn",
    "consilium": "thought balloon", "consensus": "handshake",
    "concordia": "handshake", "pactum": "handshake",
    "fundamentum": "building construction", "aedificium": "office building",
    "status": "placard", "habitus": "t-shirt", "vestimentum": "t-shirt",
    "occasio": "door", "nomino": "label", "appello": "megaphone",
    "clamo": "megaphone", "nolo": "prohibited", "veto": "prohibited",
    "probo": "victory hand", "approbo": "victory hand",
    "praefero": "victory hand", "opera": "hammer and wrench",
    "soleo": "counterclockwise arrows button", "mos": "counterclockwise arrows button",
    "consuetudo": "counterclockwise arrows button",
    "forma": "triangular ruler", "figura_alt": "triangular ruler",
    "canonicus": "straight ruler", "moralis": "balance scale",
    "praesum": "crown", "praesideo": "crown", "dux": "crown",
    "longus": "straight ruler", "brevis": "pencil",
    "quaero": "magnifying glass tilted left", "invenio": "magnifying glass tilted left",
    "cur": "red question mark", "utrum": "red question mark",
    "necesse": "double exclamation mark", "certus": "check mark button",
    "dubito": "thinking face", "taceo": "shushing face",
    # Transfer inherits another deck's choice, which is the point of it, but a
    # borrowed picture can still be wrong here: itaque came back with the END
    # sign because some card glossed 因此、所以 carries it.  A conclusion is an
    # arrow forward, not a stop.
    "itaque": "right arrow", "ergo": "right arrow", "igitur": "right arrow",
    # The enclitic and the free-standing conjunction are the same idea and
    # should carry the same sign; -que had inherited a handshake.
    "-que": "plus", "atque": "plus", "ac": "plus",
    "ideo": "right arrow", "propterea": "right arrow",
}

# Homographs that only a macron separates need different pictures, so those are
# keyed on the whole dictionary line instead of the headword.
# 2026-08-27：逐義項借圖之後，接觸表看出來的錯配。借來的圖對得起借方的那個
# 義項，卻對不起這個字——「釋放」借到揮手、「留下」借到房子、ut 借到 🔚（跟
# itaque 當初一樣，結果的箭頭不是終點）。覆蓋規則先於借用，所以寫在這裡就好。
OVERRIDES.update({
    "libero": "raising hands",          # 解放：揮手是道別，不是釋放
    "reddo": "right arrow curving left",  # 歸還：不是「站著的人」
    "condo": "building construction",   # 創建：錨是望德，不是建立
    "resto": "hourglass not done",      # 殘留：房子是「留在家」，不是「尚存」
    "clino": "person bowing",           # 傾斜、躬身：露營帳篷純屬誤配
    "inclino": "person bowing",
    "ut": "bullseye",                 # 目的連接詞，與希臘 ἵνα 同符號
    "baptisma": "droplet",              # 與同冊 baptismus 同圖，浴缸不是洗禮
})

# 2026-08-27 手挑：借圖與本名比對之後仍留白的 639 張，逐張讀詞義配圖。
# 規矩照希伯來與希臘那兩副：對不上就留白，不硬湊；虛詞給符號不給場景；
# 同義共用一張沒關係，對立的兩個字絕不共用（饑荒不可與吃共用 🍴）。
# 拿撒勒的、加里肋亞的、猶太的、羅馬的四個族屬形容詞刻意留白——這類詞在
# 另外三本是進附錄專名表的，而附錄卡本來就不配圖：沒有一個 emoji 誠實地
# 代表得了「伯特利」。
HAND_PICKED: dict[str, str] = {
    '-do': 'open hands', '-ne': 'red question mark', 'absolutus': 'hundred points',
    'accommodo': 'puzzle piece', 'accurate': 'bullseye', 'acer': 'kitchen knife',
    'acriter': 'kitchen knife', 'adhaereo': 'paperclip', 'adhibeo': 'toolbox',
    'adhuc': 'hourglass done', 'adimpleo': 'check mark button', 'adiungo': 'link',
    'admiratio': 'astonished face', 'adoro': 'person bowing', 'aduentus': 'soon arrow',
    'aegyptius': 'great pyramid of giza', 'afficio': 'magnet', 'affirmo': 'speech balloon',
    'aggrego': 'busts in silhouette', 'ait': 'speaking head', 'alibi': 'round pushpin',
    'aliqui': 'white question mark', 'alleluia': 'raising hands',
    'alloquor': 'left speech bubble', 'alter': 'shuffle tracks button', 'altus': 'mountain',
    'amanter': 'smiling face with hearts', 'ambo': 'scroll', 'amitto': 'broken heart',
    'ample': 'plus', 'amplector': 'people hugging', 'amplius': 'plus', 'amplus': 'plus',
    'angelicus': 'baby angel', 'antequam': 'last track button', 'antistes': 'man',
    'aperio': 'open book', 'aperte': 'eye', 'apis': 'honeybee', 'apostolatus': 'outbox tray',
    'apostolicus': 'outbox tray', 'appellatio': 'label', 'aprilis': 'tear-off calendar',
    'apte': 'puzzle piece', 'aptus': 'puzzle piece', 'archangelus': 'baby angel',
    'archidiaconus': 'man', 'argumentum': 'thought balloon', 'assequor': 'person running',
    'assiduus': 'repeat button', 'assumo': 'person lifting weights', 'attendo': 'ear',
    'attineo': 'clamp', 'attraho': 'magnet', 'audeo': 'lion',
    'auerto': 'left arrow curving right', 'augustinus': 'man', 'augustus': 'person with crown',
    'aureus': 'coin', 'aut . . aut': 'shuffle tracks button', 'baptista': 'droplet',
    'baptizo': 'droplet', 'beatitudo': 'smiling face with halo',
    'beneuolentia': 'smiling face with hearts', 'benignus': 'smiling face with hearts',
    'cado': 'down arrow', 'caelicola': 'baby angel', 'caligo': 'fog',
    'carus': 'sparkling heart', 'castus': 'white heart', 'casus': 'game die',
    'catholicus': 'globe showing europe-africa', 'causa': 'right arrow', 'cautio': 'receipt',
    'cedo': 'left arrow', 'celebro': 'confetti ball', 'cenaculum': 'house',
    'ceno': 'fork and knife with plate', 'cera': 'candle', 'certamen': 'crossed swords',
    'chorus': 'musical notes', 'christianus': 'latin cross',
    'circumeo': 'counterclockwise arrows button', 'circumfulgeo': 'glowing star',
    'circumspicio': 'eyes', 'ciuilis': 'classical building', 'clare': 'loudspeaker',
    'clarus': 'sun', 'clerus': 'man', 'collaetor': 'partying face',
    'collaudo': 'clapping hands', 'collecta': 'folded hands',
    'collegium': 'classical building', 'color': 'artist palette', 'commemoro': 'brain',
    'commendo': 'open hands', 'commode': 'puzzle piece', 'communio': 'bread',
    'communis': 'busts in silhouette', 'comperio': 'magnifying glass tilted left',
    'complaceo': 'smiling face with smiling eyes', 'compono': 'puzzle piece',
    'concedo': 'open hands', 'concelebro': 'clinking glasses', 'condicio': 'scroll',
    'conditio': 'scroll', 'condoleo': 'pleading face', 'confero': 'open hands',
    'confessio': 'folded hands', 'confestim': 'high voltage', 'confido': 'anchor',
    'confirmatio': 'rock', 'confiteor': 'folded hands', 'conglorifico': 'glowing star',
    'congruo': 'puzzle piece', 'consecro': 'smiling face with halo',
    'consentaneus': 'puzzle piece', 'consentio': 'thumbs up', 'conseruo': 'canned food',
    'consolatio': 'smiling face with open hands', 'consolo': 'smiling face with open hands',
    'consortium': 'people hugging', 'conspectus': 'eyes', 'constans': 'rock',
    'constanter': 'rock', 'constantia': 'rock', 'consubstantialis': 'heavy equals sign',
    'contemplatio': 'person in lotus position', 'contendo': 'bow and arrow',
    'continuo': 'high voltage', 'contradico': 'anger symbol', 'contraho': 'handshake',
    'contritus': 'pensive face', 'conuenienter': 'puzzle piece',
    'conuictus': 'clinking glasses', 'cooperor': 'handshake', 'copia': 'basket',
    'coram': 'eye', 'corrigo': 'pencil', 'cotidie': 'calendar', 'cottidie': 'calendar',
    'creatura': 'paw prints', 'cruor': 'drop of blood', 'culpa': 'cross mark',
    'cultus': 'top hat', 'cumque': 'white question mark', 'curia': 'classical building',
    'daemonium': 'smiling face with horns', 'debeo': 'receipt', 'debitor': 'receipt',
    'debitum': 'receipt', 'dec': 'tear-off calendar', 'december': 'tear-off calendar',
    'decretum': 'scroll', 'dedignor': 'face with rolling eyes', 'defendo': 'shield',
    'deficio': 'chart decreasing', 'defunctus': 'coffin', 'deinceps': 'abacus',
    'demum': 'end arrow', 'denique': 'end arrow', 'denuo': 'repeat button',
    'deputo': 'clipboard', 'destruo': 'cyclone', 'detergeo': 'sponge',
    'detrimentum': 'chart decreasing', 'deuinco': 'trophy', 'differo': 'hourglass not done',
    'diffundo': 'dashing away', 'dignitas': 'crown', 'dignor': 'person bowing',
    'dignus': 'gem stone', 'diiudico': 'balance scale', 'diligenter': 'ant',
    'directe': 'right arrow', 'discretio': 'balance scale', 'dispar': 'prohibited',
    'dispergo': 'dashing away', 'dissimilis': 'prohibited', 'dito': 'money bag',
    'diu': 'hourglass done', 'diues': 'money bag', 'diuinitus': 'dove',
    'documentum': 'page facing up', 'dolorosus': 'crying face', 'domina': 'woman',
    'dominicus': 'latin cross', 'donatio': 'wrapped gift', 'dubitatio': 'thinking face',
    'dubium': 'thinking face', 'dubius': 'thinking face', 'dummodo': 'white question mark',
    'dumtaxat': 'pinching hand', 'duplex': 'double exclamation mark',
    'educatio': 'graduation cap', 'effectus': 'hammer and wrench',
    'effero': 'person lifting weights', 'efficaciter': 'hammer and wrench',
    'efficax': 'hammer and wrench', 'efficio': 'hammer and wrench', 'effusio': 'droplet',
    'eiicio': 'outbox tray', 'electus': 'ballot box with ballot', 'eleison': 'folded hands',
    'en': 'eyes', 'eo': 'footprints', 'episcopalis': 'man', 'erga': 'right arrow',
    'erigo': 'chart increasing', 'erro': 'world map', 'essentialis': 'gem stone',
    'ethica': 'balance scale', 'euangelicus': 'open book', 'euangelizo': 'loudspeaker',
    'eucharisticus': 'bread', 'excelsus': 'mount fuji', 'excipio': 'waving hand',
    'exemplar': 'memo', 'exemplum': 'memo', 'exerceo': 'person lifting weights',
    'exercitatio': 'person lifting weights', 'exercitium': 'person lifting weights',
    'expedio': 'package', 'expello': 'outbox tray', 'expono': 'framed picture',
    'exprimo': 'speech balloon', 'exsulto': 'partying face', 'extendo': 'left-right arrow',
    'extollo': 'raising hands', 'factor': 'hammer and wrench',
    'factum est': 'check mark button', 'fama': 'newspaper', 'februarius': 'tear-off calendar',
    'felicitas': 'four leaf clover', 'feliciter': 'four leaf clover', 'fero': 'package',
    'festum': 'party popper', 'festus': 'party popper', 'fideliter': 'dog', 'figo': 'pushpin',
    'firmus': 'rock', 'fore': 'soon arrow', 'foueo': 'seedling',
    'fraternitas': 'people hugging', 'frequenter': 'repeat button', 'fugio': 'dashing away',
    'fugo': 'dashing away', 'fungor': 'gear', 'genitus': 'baby', 'gero': 'briefcase',
    'gradatim': 'snail', 'gratus': 'smiling face with smiling eyes', 'grauiter': 'collision',
    'hactenus': 'hourglass done', 'hic': 'round pushpin', 'hinc': 'round pushpin',
    'hodiernus': 'tear-off calendar', 'honestas': 'white heart', 'honor': 'crown',
    'hosanna': 'palm tree', 'huc': 'round pushpin', 'humanitas': 'people hugging',
    'iaceo': 'person in bed', 'ianuarius': 'tear-off calendar', 'ibidem': 'round pushpin',
    'idem': 'heavy equals sign', 'idoneus': 'puzzle piece', 'iesus': 'latin cross',
    'illuc': 'round pushpin', 'illuminatio': 'light bulb', 'immo': 'shuffle tracks button',
    'imperator': 'person with crown', 'impono': 'down arrow', 'impulsus': 'collision',
    'imus': 'down arrow', 'in aeternum': 'infinity', 'inaestimabilis': 'gem stone',
    'incarnatio': 'anatomical heart', 'incarno': 'anatomical heart',
    'incommodus': 'worried face', 'inde': 'left arrow', 'indeficiens': 'infinity',
    'indignus': 'no entry', 'induco': 'inbox tray', 'ineffabilis': 'zipper-mouth face',
    'infero': 'paperclip', 'inferus': 'fire', 'inficio': 'microbe', 'infinitus': 'infinity',
    'infirmus': 'face with thermometer', 'infundo': 'droplet', 'ingenium': 'brain',
    'iniquus': 'no entry', 'innitor': 'anchor', 'inquiro': 'magnifying glass tilted left',
    'inquisitio': 'magnifying glass tilted left', 'insero': 'seedling',
    'insignis': 'glowing star', 'insono': 'bell', 'instar': 'heavy equals sign',
    'insum': 'inbox tray', 'insurgo': 'raised fist', 'integer': 'white circle',
    'integritas': 'white heart', 'intentio': 'bullseye', 'intentus': 'bow and arrow',
    'intercessio': 'folded hands', 'interdum': 'alarm clock', 'intimus': 'people hugging',
    'inuicem': 'counterclockwise arrows button', 'inuoco': 'folded hands',
    'is': 'backhand index pointing right', 'israel': 'busts in silhouette',
    'iste': 'backhand index pointing left', 'iucundus': 'smiling face with smiling eyes',
    'iulius': 'tear-off calendar', 'iungo': 'link', 'iunius': 'tear-off calendar',
    'iuuentus': 'boy', 'kyrie': 'folded hands', 'lacrima': 'crying face',
    'lacrimosus': 'crying face', 'laetus': 'grinning face', 'largior': 'wrapped gift',
    'largitas': 'wrapped gift', 'late': 'globe showing europe-africa',
    'latus': 'anatomical heart', 'lectio': 'open book', 'lector': 'student', 'leuita': 'man',
    'libenter': 'grinning face', 'libere': 'raising hands', 'libido': 'heart on fire',
    'licet': 'check mark button', 'limes': 'flagged point', 'liquo': 'droplet',
    'localis': 'round pushpin', 'lucifer': 'shooting star', 'maestus': 'crying face',
    'maiestas': 'crown', 'maior': 'chart increasing', 'male': 'thumbs down',
    'male habeo': 'face with thermometer', 'maledico': 'face with symbols on mouth',
    'mando': 'fork and knife with plate', 'manifestus': 'eye', 'martius': 'tear-off calendar',
    'materialis': 'brick', 'matutinus': 'sunrise', 'maximus': 'chart increasing',
    'memor': 'brain', 'mentio': 'speech balloon', 'mercor': 'money bag',
    'mereo': 'military medal', 'merito': 'military medal', 'miles': 'military helmet',
    'minuo': 'chart decreasing', 'mirabilis': 'astonished face', 'miror': 'astonished face',
    'miser': 'worried face', 'misere': 'worried face', 'miseror': 'pleading face',
    'mortalis': 'skull', 'mox': 'soon arrow', 'moyses': 'man', 'multiplex': 'abacus',
    'mutatio': 'counterclockwise arrows button', 'mutuo': 'receipt', 'mutuor': 'receipt',
    'mysterium': 'locked', 'mysticus': 'locked', 'natura': 'seedling', 'ne': 'prohibited',
    'necessario': 'check mark', 'nedum': 'plus', 'nequaquam': 'prohibited',
    'neque': 'prohibited', 'nequeo': 'prohibited', 'nexus': 'chains', 'nimirum': 'eye',
    'nimis': 'double exclamation mark', 'nimius': 'double exclamation mark',
    'nobilis': 'crown', 'nominatim': 'label', 'nonne': 'red question mark',
    'nonnullus': 'pinching hand', 'nonnumquam': 'alarm clock',
    'notio': 'magnifying glass tilted left', 'notus': 'glowing star',
    'nouissimus': 'end arrow', 'nullatenus': 'prohibited', 'numquid': 'red question mark',
    'oblatio': 'open hands', 'obseruo': 'telescope', 'occurro': 'waving hand',
    'odium': 'angry face', 'oeconomicus': 'house', 'omissio': 'hole',
    'omnipotens': 'flexed biceps', 'opportunitas': 'game die', 'opportunus': 'puzzle piece',
    'optimus': '1st place medal', 'orientalis': 'compass', 'ostendo': 'framed picture',
    'pacifico': 'dove', 'palam': 'eye', 'par': 'heavy equals sign', 'parens': 'family',
    'particeps': 'handshake', 'particularis': 'puzzle piece', 'partim': 'puzzle piece',
    'parum': 'pinching hand', 'paruulus': 'baby', 'paschalis': 'ewe', 'pasco': 'ewe',
    'pastoralis': 'ewe', 'pateo': 'open hands', 'patriarcha': 'older person',
    'patrimonium': 'house', 'patrocinium': 'shield', 'patronus': 'shield',
    'pauci': 'pinching hand', 'paucus': 'pinching hand', 'paulatim': 'snail',
    'peccator': 'black heart', 'pectus': 'anatomical heart', 'penetro': 'pushpin',
    'pentecoste': 'dove', 'perduco': 'compass', 'peregrinantis': 'person walking',
    'perenniter': 'infinity', 'peritus': 'graduation cap', 'permaneo': 'infinity',
    'perpetuo': 'infinity', 'perpetuus': 'infinity', 'personalis': 'bust in silhouette',
    'perspicio': 'eyes', 'pertineo': 'link', 'pertranseo': 'right arrow',
    'philosophus': 'thinking face', 'piaculum': 'black heart', 'pius': 'folded hands',
    'placeo': 'smiling face with smiling eyes', 'placet': 'thumbs up', 'placo': 'dove',
    'planctus': 'crying face', 'plango': 'crying face', 'plebs': 'busts in silhouette',
    'plenitudo': 'full moon', 'popularis': 'busts in silhouette', 'posterus': 'soon arrow',
    'postis': 'door', 'postremo': 'end arrow', 'potens': 'flexed biceps',
    'potius': 'balance scale', 'praecipuus': 'bullseye', 'praeconium': 'clapping hands',
    'praefatio': 'bookmark tabs', 'praemium': 'trophy', 'praeses': 'man',
    'praesumo': 'thinking face', 'praeterea': 'plus', 'pretiosus': 'gem stone',
    'pretium': 'coin', 'primarius': '1st place medal', 'primas': 'crown',
    'principalis': '1st place medal', 'prior': 'last track button',
    'priuatim': 'bust in silhouette', 'priuatus': 'bust in silhouette', 'priuilegium': 'key',
    'prius': 'last track button', 'priusquam': 'last track button', 'procul': 'telescope',
    'prodeo': 'right arrow', 'profecto': 'check mark', 'profiteor': 'speaking head',
    'progressus': 'chart increasing', 'proiicio': 'outbox tray', 'promissio': 'handshake',
    'propitius': 'smiling face with hearts', 'proprietas': 'key',
    'proprius': 'bust in silhouette', 'prosequor': 'right arrow', 'protectio': 'shield',
    'prouidentia': 'eye', 'prouincia': 'world map', 'proximus': 'handshake', 'publice': 'eye',
    'quando': 'alarm clock', 'quanto': 'straight ruler', 'quare': 'thinking face',
    'quidam': 'white question mark', 'quies': 'zzz', 'quintus': 'man',
    'quisquam': 'white question mark', 'quisquis': 'white question mark',
    'quocumque': 'round pushpin', 'quodammodo': 'white question mark',
    'quodsi': 'white question mark', 'quominus': 'prohibited', 'quotquot': 'abacus',
    'radius': 'flashlight', 'raro': 'gem stone', 'recens': 'new button',
    'reclino': 'person in bed', 'reconciliatio': 'handshake', 'rectus': 'straight ruler',
    'redigo': 'counterclockwise arrows button', 'regimen': 'joystick',
    'regularis': 'straight ruler', 'relatio': 'memo', 'remaneo': 'hourglass not done',
    'remitto': 'unlocked', 'repello': 'outbox tray', 'respectus': 'right arrow curving left',
    'resulto': 'bell', 'resurgo': 'sunrise', 'retineo': 'clamp', 'reuera': 'check mark',
    'reus': 'chains', 'rite': 'church', 'ruber': 'red circle', 'sacerdotalis': 'man',
    'sacerdotium': 'man', 'sacro': 'smiling face with halo', 'saepe': 'repeat button',
    'saltem': 'pinching hand', 'salue': 'waving hand', 'sancio': 'scroll',
    'sanctifico': 'smiling face with halo', 'sapienter': 'owl', 'satio': 'pot of food',
    'scelus': 'collision', 'secundum': 'straight ruler', 'sedulo': 'ant',
    'segrego': 'scissors', 'semita': 'footprints', 'separo': 'scissors',
    'serenus': 'sun behind cloud', 'seruitium': 'chains', 'seruitus': 'chains', 'sexus': 'dna',
    'siccus': 'desert', 'sicut .. et': 'heavy equals sign', 'sidus': 'glowing star',
    'simulac': 'stopwatch', 'sincerus': 'white heart', 'sinus': 'amphora',
    'socialis': 'handshake', 'socio': 'link', 'solacium': 'smiling face with open hands',
    'solor': 'smiling face with open hands', 'solum': 'pinching hand',
    'solummodo': 'pinching hand', 'specialis': 'bullseye', 'specialiter': 'bullseye',
    'spiritualis': 'dove', 'spiro': 'wind face', 'splendor': 'glowing star',
    'spons': 'raising hands', 'statim': 'high voltage', 'struo': 'building construction',
    'studiose': 'ant', 'suauis': 'honey pot', 'suauitas': 'honey pot', 'sub': 'down arrow',
    'subditus': 'person bowing', 'subicio': 'person bowing', 'submitto': 'down arrow',
    'subsidium': 'handshake', 'subsum': 'down arrow', 'successor': 'next track button',
    'supernaturalis': 'sparkles', 'supersubstantialis': 'bread', 'supplex': 'folded hands',
    'sursum': 'up arrow', 'suus': 'bust in silhouette', 'tandem': 'end arrow',
    'tantum': 'pinching hand', 'tantummodo': 'pinching hand', 'tantus': 'chart increasing',
    'tellus': 'globe showing americas', 'temporalis': 'hourglass not done',
    'tendo': 'left-right arrow', 'theologia': 'blue book', 'tot': 'abacus',
    'tracto': 'briefcase', 'tranquillus': 'dove', 'trans': 'left-right arrow',
    'transfero': 'delivery truck', 'tremo': 'fearful face', 'tristis': 'frowning face',
    'tueor': 'shield', 'tuus': 'index pointing at the viewer', 'ua': 'red exclamation mark',
    'uber': 'glass of milk', 'ubi': 'round pushpin', 'ueluti': 'heavy equals sign',
    'uenerabilis': 'smiling face with halo', 'uerbero': 'hammer',
    'uespertinus': 'crescent moon', 'uestigium': 'footprints', 'uicinus': 'houses',
    'uictor': 'trophy', 'uidelicet': 'eye', 'uigor': 'flexed biceps', 'uincio': 'chains',
    'uinco': 'trophy', 'uinculum': 'chains', 'uiolentia': 'collision', 'uirgo': 'woman',
    'uitium': 'thumbs down', 'uito': 'dashing away', 'uiuifico': 'seedling',
    'uiuus': 'beating heart', 'uix': 'pinching hand', 'ullus': 'white question mark',
    'unctio': 'olive', 'unde': 'left arrow', 'undique': 'compass',
    'uniuersalis': 'globe showing europe-africa', 'uniuersum': 'ringed planet',
    'uocabulum': 'books', 'uoco': 'loudspeaker', 'urgeo': 'right arrow',
    'ut quid': 'thinking face', 'utilis': 'toolbox', 'utilitas': 'toolbox',
    'utinam': 'folded hands', 'utique': 'ok hand',
}

OVERRIDES.update(HAND_PICKED)

# OCR 斷行修好之後，這個詞條的鍵才成立。
OVERRIDES["satis (+ partitive gen.)"] = "pot of food"

OVERRIDES_BY_FORMS: dict[str, str] = {
    # 同形異義的六個詞，圖要跟著各自的詞典行走，不能鍵在共同的 headword 上：
    # labor 的名詞是勞苦（工具），動詞是滑落（落葉）。
    "liber, libera, liberum": "unlocked",
    "mundus, -a, -um": "soap",
    "fundō, fundere, fūdī, fūsus": "droplet",
    "labor, labōris": "hammer and wrench",
    "labor, labī, —, lāpsus sum": "fallen leaf",
    "licet": "shuffle tracks button",

    "occīdō, occīdere, occīdī, occīsus": "dagger",
    "occidō, occidere, occidī, occāsus": "sunset",
    "praedicō, praedicāre, praedicāvī, praedicātus": "speaking head",
    "praedīcō, praedīcere, praedīxī, praedictus": "crystal ball",
}


def key_of(entry: dict) -> str:
    """The identity the vocabulary master itself deduplicates on."""
    return L.fold(entry.get("forms") or entry["headword"])


# 拉丁那本的中文用思高本，希伯來與希臘那兩本用《和合本修訂版》，所以同一個概念
# 在兩邊寫法不同，圖就借不過來。這張表只放兩邊確實同指一物的對子；不確定的不放。
CATHOLIC_TO_PROTESTANT = {
    "宗徒": "使徒", "聖神": "聖靈", "天神": "天使", "恩寵": "恩典",
    "默西亞": "彌賽亞", "法利塞": "法利賽", "撒殫": "撒但", "聖詠": "詩篇",
    "司祭": "祭司", "盟約": "約", "光榮": "榮耀", "義德": "公義",
}

SENSE_SPLIT = re.compile(r"[；、，,;]")


def senses(gloss: str) -> list[str]:
    """The gloss's senses, in the order it writes them.

    A Latin word's Chinese is usually several senses long, and only the first
    was ever looked up — so `libero`「解放、釋放」 borrowed nothing although
    「釋放」 was pictured, and `canticum`「聖歌、讚美詩」 nothing although
    「讚美詩」 was. Order matters and is preserved: the first sense is the
    word's core meaning and gets first refusal on a picture.
    """

    seen: list[str] = []
    for part in SENSE_SPLIT.split(gloss):
        part = part.strip()
        if part and part not in seen:
            seen.append(part)
    return seen


def borrowed_meanings() -> dict[str, str]:
    """Chinese meanings the Hebrew and Greek decks have already pictured."""
    meanings: dict[str, str] = {}
    for name in ("hebrew-card-images.json", "greek-card-images.json"):
        path = CACHE / name
        if not path.exists():
            continue
        for record in json.loads(path.read_text(encoding="utf-8"))["images"].values():
            gloss = (record.get("glossZh") or "").strip()
            for meaning in (gloss, gloss.split("；")[0].strip(), gloss.split("、")[0].strip()):
                if meaning:
                    meanings.setdefault(meaning, record["hexcode"])
    return meanings


def main() -> None:
    parser = argparse.ArgumentParser(description="替教會拉丁文單字卡挑圖，挑不到就留空")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    base.ensure_openmoji()
    entries = json.loads(VOCAB.read_text(encoding="utf-8"))["entries"]
    by_name = base.load_openmoji()
    borrowed = borrowed_meanings()
    print(f"  可借用的中文詞義 {len(borrowed)} 個")

    assigned: dict[str, dict] = {}
    borrowed_via: dict[str, str] = {}
    unresolved: list[str] = []
    sources = {"override": 0, "zh_transfer": 0, "annotation": 0, "none": 0}

    for entry in entries:
        card = key_of(entry)
        chosen = None
        source = "none"

        wanted = (OVERRIDES_BY_FORMS.get(entry.get("forms", ""))
                  or OVERRIDES.get(L.fold(entry["headword"])))
        if wanted:
            found = by_name.get(wanted.lower())
            if found and base.image_path(found["hexcode"]):
                chosen, source = found["hexcode"], "override"
            else:
                unresolved.append(f"{entry['headword']} -> {wanted!r}")

        if not chosen:
            gloss = (entry.get("glossZh") or "").strip()
            # Deliberately not named `key`: that holds this card's own identity,
            # and the Hebrew matcher once wrote a hundred and thirty-two entries
            # under their Chinese meaning by shadowing it here.
            for sense in [gloss, *senses(gloss)]:
                candidates = [sense]
                for catholic, protestant in CATHOLIC_TO_PROTESTANT.items():
                    if catholic in sense:
                        candidates.append(sense.replace(catholic, protestant))
                for candidate in candidates:
                    hexcode = borrowed.get(candidate)
                    if hexcode and base.image_path(hexcode):
                        chosen, source = hexcode, "zh_transfer"
                        borrowed_via[key_of(entry)] = candidate
                        break
                if chosen:
                    break

        if not chosen:
            for candidate in base.english_candidates(entry.get("glossEn") or ""):
                if candidate in base.AMBIGUOUS_EN:
                    continue
                found = by_name.get(candidate)
                if found and base.image_path(found["hexcode"]):
                    chosen, source = found["hexcode"], "annotation"
                    break

        sources[source] += 1
        if chosen:
            assigned[card] = {
                "hexcode": chosen,
                "file": base.image_path(chosen).name,
                "source": source,
                "headword": entry["headword"],
                "glossZh": entry.get("glossZh", ""),
                # 借來的圖記下是循哪一個義項借的，之後回頭稽核時才看得出
                # 這張圖對的是這個字的核心義還是末位義。
                **({"borrowedVia": borrowed_via[card]} if card in borrowed_via else {}),
            }

    # Every key must resolve, or the deck builder silently prints a blank card.
    identities = {key_of(entry) for entry in entries}
    stray = sorted(set(assigned) - identities)
    assert not stray, f"圖表出現詞表沒有的鍵：{stray[:5]}"

    total = len(entries)
    print(f"  人工指定 {sources['override']}，中文詞義轉移 {sources['zh_transfer']}，"
          f"本名比對 {sources['annotation']}，留空 {sources['none']}")
    print(f"  有圖合計 {len(assigned)} / {total} = {len(assigned) * 100 // total}%")
    for volume in ("上冊", "下冊"):
        rows = [e for e in entries if e["volume"] == volume]
        got = sum(1 for e in rows if key_of(e) in assigned)
        print(f"    {volume} {got}/{len(rows)} = {got * 100 // max(len(rows), 1)}%")
    if unresolved:
        print(f"  ⚠ 人工指定但查無此圖：{len(unresolved)}")
        for item in sorted(set(unresolved))[:20]:
            print(f"      {item}")

    uncovered = [
        (entry.get("corpusFrequency") or 0, entry["volume"], entry["lesson"],
         entry["headword"], entry.get("glossZh", ""))
        for entry in entries if key_of(entry) not in assigned
    ]
    uncovered.sort(reverse=True)
    print("\n  仍無圖、語料出現次數最高的 25 個：")
    for frequency, volume, lesson, headword, zh in uncovered[:25]:
        print(f"      {frequency:>6} {volume} L{lesson:<3} {headword:<18} {zh}")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps({
                "schemaVersion": "1.0.0",
                "source": "OpenMoji 17.0.0",
                "licence": "CC BY-SA 4.0 — https://openmoji.org",
                "note": "每張卡最多一張圖，取該詞最常見的義項；挑不到就留空，不以近似圖充數。",
                "keyedOn": "詞條的完整字典形式（折疊拼寫），與詞表的去重鍵相同",
                "images": assigned,
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\n已寫出 {OUTPUT}")
    else:
        print("\n（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
