#!/usr/bin/env python3
# 角色立绘的衣着差分和对话用的表情差分（11-05）。用户说现有的立绘太腻，要换成四套衣着（常服、私服、战斗、正装）在状态栏里切，表情差分给正文的对话框用。
# 一位先出常服（base），拿它当参考出另外三套和一张表情表，脸和发型才连得上。写 out/立绘_11-05/<英文名>/，已有的不重出。
#   python gpt_cast.py prep                 只裁旧立绘的头（只有成年角色才拿旧立绘当长相参考）
#   python gpt_cast.py eleanor_casual ...   出指定的几张，三张一起跑
#   python gpt_cast.py eleanor              出这一位缺的全部（先常服，再别的）
# 十八岁以下、看着十八岁以下的旅伴（FROM_TEXT 里的）不拿旧立绘当参考，只照文字设定写，新图一律穿戴整齐、不往性感上画。
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '立绘_11-05')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
STYLE_REF = os.path.join(ROOT, '语料', '人物参考_11-04', 'maze_right_style.png')
OLD = os.environ.get('CAST_OLD', '')   # 旧立绘下在哪（临时目录），只有 prep 用

STYLE = ('Full-body standing character portrait (tachie) for a high-end Japanese fantasy RPG, in the manner of official Genshin Impact and Honkai Star Rail character art. '
         'Clean, confident line art; soft cel shading with gentle gradients; matte fabrics and restrained highlights; a beautiful, refined anime face with natural proportions; natural anatomy, a head-to-body ratio of about 1 to 7, hands drawn carefully with the correct number of fingers. '
         'The whole figure is shown from the top of the head to the soles of the feet, standing, centred, filling the height of the picture with a small margin, the body turned slightly to the viewer\'s left, the face clearly readable and looking toward the viewer. Fully clothed, modest, not sexualized, no cleavage, no bare midriff. '
         'Transparent background: nothing behind the figure, no scenery, no floor, no cast shadow. No text, no logo, no frame, no signature. '
         'NO sparkles, NO glitter, NO floating particles, NO lens flare, NO glowing rim light, NO oily or glossy skin, NO heavy gold filigree, NO over-detailed jewellery. Portrait picture, aspect ratio 2:3. ')
SAME = ('The attached picture shows this same character: keep exactly the same face, the same eye colour, the same hair colour and hair texture, the same age, the same height and build, the same line and colour treatment and the same framing, from the top of the head to the soles of the feet. '
        'Only the clothes, the hairstyle if mentioned, the pose and the expression change, as described here. ')
FACES = ('Character expression sheet for the dialogue box of a Japanese RPG. The attached picture shows this character: keep exactly the same face, eyes, hair and the same drawing style. '
         'Draw NINE bust portraits of her or him on one square picture, in a perfectly regular grid of 3 columns and 3 rows, every cell the same size, with generous empty space between the cells. Every cell shows the head, neck and the top of the shoulders in the same clothes, the same size, from the same slightly turned camera angle, the eyes at the same height, the whole head including all the hair inside the cell. '
         'Top row, left to right: calm and neutral; a gentle closed-mouth smile; a bright open-mouthed laugh with the eyes closed in happiness. '
         'Middle row, left to right: serious and determined; angry, with furrowed brows and bared teeth; sad, with teary eyes and lowered brows. '
         'Bottom row, left to right: surprised, wide eyes and a small open mouth; shy, blushing, the eyes looking away; in pain, one eye shut, teeth clenched, a drop of sweat. '
         'Transparent background, no lines between the cells, no text, no labels, no frame. Soft cel shading, clean line art, no sparkles, no glossy skin. ')

# 成年角色：旧立绘只裁头（框写在 1024×1536 的原图上），只取长相
CAST = {
    'eleanor': {
        'name': '埃莉诺',
        'head': (250, 60, 800, 720),
        'who': ('A 22-year-old woman, a kingdom knight who earned her badge on the battlefield: tall (172 cm), straight-backed, the lean shoulders and waist of strict training, grown-up and dignified. '
                'Bright gold hair in big loose curling waves, sea-gem blue eyes. '),
        'outfits': {
            'casual': ('She wears her off-duty travelling clothes: a fitted dark navy knight\'s coat with a high collar buttoned to the throat, long sleeves and plain silver buttons, a small worn knight\'s badge on the left chest, a sturdy brown leather belt, dark breeches and knee-high riding boots, polished but well worn; a short travelling cape over one shoulder, its edge neatly mended. Her hair falls loose in big gold waves. She stands very straight, one hand resting on the belt, the other at her side. Calm, kind, slightly stern expression.'),
            'private': ('She has taken her armour off for the night: a plain cream linen shirt with the sleeves rolled to the elbows, buttoned up, tucked into a simple long dark-blue wool skirt, soft flat leather shoes. Her hair is gathered to one side with a plain ribbon. She holds a folded, half-mended cloak against her hip with one hand. A relaxed, faintly awkward, gentle expression.'),
            'battle': ('She is in full battle gear: a practical harness of brushed steel plate, no gold, a dark blue surcoat over the breastplate, heavy pauldrons, gauntlets, armoured boots. Both gauntlets rest on the pommel of an enormous two-handed greatsword planted point-down in front of her, nearly as tall as she is, heavier than she looks able to carry; its crossguard is as wide as a low wall and a long groove runs down the blade where a name has been chiselled away. Her hair is tied back in a tight high braid. A resolute stance that will not give ground.'),
            'formal': ('She wears a kingdom knight\'s full-dress uniform: a long white tailored dress coat with navy facings and restrained gold piping, a high collar, a blue sash from shoulder to hip, two small medal ribbons, white gloves, polished boots, a slim ceremonial sword at the hip. Her hair is pinned up neatly with a few waves left free. The perfectly correct posture of someone with top marks in etiquette.'),
        },
    },
    'tifa': {
        'name': '蒂法',
        'head': (380, 60, 800, 500),
        'who': ('A 20-year-old woman who owns a tavern in the lower city and trains in unarmed fighting every dawn: sturdy, well-balanced, a low centre of gravity. '
                'Waist-length straight very dark brown-black hair with the ends tied by a strip of ribbon, exactly the colour in the reference, warm wine-red eyes; warm when she smiles, a little stubborn when she does not. '),
        'outfits': {
            'casual': ('She is at work behind her bar: a white shirt with the sleeves rolled up and the collar buttoned, a black waistcoat, a long dark apron tied at the waist over a long dark skirt, low boots, a bar towel over one shoulder. She stands easily with one hand on her hip, a warm, tired smile.'),
            'private': ('After closing time: a soft oversized oatmeal knitted jumper with a high neck, a long brown skirt, thick wool socks and simple house shoes. Her hair is in a loose low ponytail. She holds a wooden mug in both hands. A small unguarded smile.'),
            'battle': ('Keep her soft, warm face and her wine-red eyes exactly as in the reference, a small confident smile. She has left her work clothes behind: NO apron, NO towel, NO waist sash, NO pouches. She is ready for a street fight: a fitted white sleeveless top with a high neckline that fully covers her midriff, black suspenders over it, a black pleated skirt to the knee over dark fighting shorts and dark leggings, sturdy lace-up boots. Red-and-black fingerless fighting gloves joined to arm guards, thin steel plates over the knuckles, the red leather worn and many times re-stitched. A low balanced fighting stance, knees bent, fists raised, weight forward.'),
            'formal': ('She has been made to dress up for a banquet and is not used to it: a simple dark wine-red long dress with long sleeves and a high neck, a little black lace only at the cuffs, small silver earrings, a red ribbon in her hair, plain dark shoes. She stands a little stiffly, a shy, slightly uncomfortable smile.'),
        },
    },
    'reinhardt': {
        'name': '莱恩哈特',
        # 旧立绘的头不给：头一版拿了它，皮肤晒黑、头发成了脏辫，头也小（外头有 casual_v1.png）。容貌照底卡 #885 的字，用户又说身材要魁梧
        'who': ('A very old but unbent grand marshal of the empire, the most-painted face in the realm: very tall and burly, a massive powerful warrior\'s build even in old age, huge broad shoulders, a thick chest, heavy arms and thick legs, standing straight, every movement trained like a knight\'s salute. '
                'Smooth, straight, shining platinum hair falling freely over his shoulders, like sunlight laid on them, and a neat full platinum beard, NOT braided, NO dreadlocks; steady amber eyes; a handsome, kind, serious old face with a few fine lines, fair skin, NOT tanned. '
                'The head is in natural proportion to the body and clearly readable, the face turned toward the viewer. '),
        'outfits': {
            'casual': ('He wears a marshal\'s plain off-duty uniform: a long dark navy coat with simple silver-white buttons and a high collar, no medals, a white shirt collar, dark trousers, tall black boots. He stands very straight with his hands clasped behind his back. Calm, attentive expression.'),
            'private': ('Off duty in his quarters: a plain oatmeal wool cardigan over a white shirt with the sleeves rolled up, soft dark trousers, worn slippers. He holds a torn plain white banner in one hand and a needle with thread in the other, clumsily mending its back. A quiet, slightly amused, grandfatherly smile.'),
            'battle': ('He wears bright white-steel full plate armour polished almost blinding, restrained gold edging only at the rims, a long white cape; a plain white unmarked banner on a tall lance held upright in his left hand, a famous sword left sheathed at his hip. He stands like a monument, feet planted. Grave, steady expression.'),
            'formal': ('He wears the grand marshal\'s full dress: a long white-and-gold dress uniform with a high collar, a rising-sun insignia on the chest, rows of medals kept neat, a heavy white mantle with a gold clasp, a short ceremonial baton in one hand. He looks patient and a little uncomfortable with all this honour.'),
        },
    },
}
ORDER = ['casual', 'private', 'battle', 'formal']


def head_path(k):
    return os.path.join(OUT, k, 'head.png')


def job(name):
    k, kind = name.rsplit('_', 1)
    c = CAST[k]
    stem = os.path.join(OUT, k, kind)
    base = os.path.join(OUT, k, 'casual.png')
    if kind == 'casual':
        refs = [STYLE_REF]
        lead = 'The FIRST attached picture is a style reference only, for its line and colour treatment: do not copy its people, its composition or its background. '
        if os.path.exists(head_path(k)):
            refs.append(head_path(k))
            lead += ('The SECOND attached picture shows only this character\'s face and hair: keep her or his face shape, eye colour, hair colour and hair texture, and ignore its heavy glossy rendering. ')
        p = lead + STYLE + c['who'] + c['outfits']['casual']
    elif kind == 'faces':
        refs = [base]
        p = FACES + c['who']
    else:
        refs = [base]
        p = SAME + STYLE + c['who'] + c['outfits'][kind]
    print('  开始', name, flush=True)
    out = gpt_gen.gen(stem, p, refs=refs, timeout=1200)
    print('  好了', name, out, flush=True)
    return out


def prep():
    from PIL import Image
    for k, c in CAST.items():
        if not c.get('head'):
            continue
        src = os.path.join(OLD, c['name'] + '.png')
        os.makedirs(os.path.join(OUT, k), exist_ok=True)
        Image.open(src).convert('RGB').crop(c['head']).save(head_path(k))
        print(k, 'head')


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['prep']:
        prep()
        sys.exit()
    jobs = []
    for a in args:
        if a in CAST:
            jobs += [a + '_' + o for o in ORDER[1:]] + [a + '_faces']
        else:
            jobs.append(a)
    with ThreadPoolExecutor(3) as ex:
        for f in [ex.submit(job, j) for j in jobs]:
            try:
                f.result()
            except Exception as e:
                print('  失败', e, flush=True)
