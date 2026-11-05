#!/usr/bin/env python3
# 素材工具（11-03）：一样东西一张图，白底出、抠透明，再拼四方的画。comfy_run.py 那几路是整幅一次出，这里是一件一件出。
#   from kit import gen, cut
#   gen(文件名, 提示词, w, h, seed, model='turbo'|'aesthetic', init=图, denoise=.., control=(图, 'lineart', 强度))
#   cut(带底的图, 透明图)   BiRefNet 抠图
# 已有的文件不重出。Anima 的前缀和反面词照官方模型卡，Aesthetic 不写 score_ 标签，Turbo 跑 CFG 1、8 到 12 步。
import io
import json
import os
import sys
import time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import comfy_run as C
from PIL import Image

INFO = None
MODELS = {
    'turbo': dict(unet='anima-turbo-v1.1.safetensors', steps=10, cfg=1.0, sampler='euler', scheduler='simple', pre='masterpiece, best quality, score_7, safe, ', neg=''),
    'aesthetic': dict(unet='anima-aesthetic-v1.1.safetensors', steps=30, cfg=4.0, sampler='er_sde', scheduler='simple', pre='masterpiece, best quality, safe, ',
                      neg='worst quality, low quality, artist name, blurry, jpeg artifacts, chromatic aberration, watermark, signature, text, nsfw, nude, '),
    'noob': dict(ckpt='NoobAI-XL-v1.1.safetensors', steps=28, cfg=5.5, sampler='euler_ancestral', scheduler='normal', pre='masterpiece, best quality, newest, absurdres, highres, safe, ',
                 neg='nsfw, worst quality, old, early, low quality, lowres, signature, username, logo, bad hands, mutated hands, mammal, anthro, furry, ambiguous form, feral, semi-anthro, '),
    'preview3': dict(unet='anima-preview3-base.safetensors', steps=30, cfg=4.0, sampler='er_sde', scheduler='simple', pre='masterpiece, best quality, score_7, safe, ',
                     neg='worst quality, low quality, score_1, score_2, score_3, artist name, blurry, jpeg artifacts, chromatic aberration, watermark, signature, text, nsfw, nude, '),
}
CLIP = 'qwen_3_06b_base.safetensors'
VAE = 'qwen_image_vae.safetensors'


def info():
    global INFO
    if INFO is None:
        INFO = C.get_json('/object_info', timeout=300)
    return INFO


def _run(prompt):
    hist, secs = C.queue_and_wait(prompt)
    return C.fetch_images(hist), secs


def gen(path, prompt, w, h, seed=1, model='turbo', negative='', init=None, denoise=1.0, control=None, steps=None, cfg=None, sampler=None, pre=None, mask=None, inpaint=None, lora=None):
    """出一张，存 path，回 PIL 图。init 是图生图的底，mask 是白色处重绘的遮罩（同尺寸），control=(图, 模型关键字, 强度)，lora=(文件名, 强度)。"""
    if os.path.exists(path):
        return Image.open(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    m = MODELS[model]
    g = C.Graph(info())
    if 'ckpt' in m:
        ck = g.add('CheckpointLoaderSimple', ckpt_name=m['ckpt'])
        un_ref, cl_ref, va_ref = [ck, 0], [ck, 1], [ck, 2]
    else:
        un_ref = [g.add('UNETLoader', unet_name=m['unet'], weight_dtype='default'), 0]
        cl_ref = [g.add('CLIPLoader', clip_name=CLIP, type='stable_diffusion'), 0]
        va_ref = [g.add('VAELoader', vae_name=VAE), 0]
    if lora is not None:   # 风格模型挂在底模后面，文本编码器也过一遍，不带文本编码器部分的 LoRA 这一路等于没动
        ll = g.add('LoraLoader', model=un_ref, clip=cl_ref, lora_name=lora[0], strength_model=lora[1], strength_clip=lora[1])
        un_ref, cl_ref = [ll, 0], [ll, 1]
    pos = g.add('CLIPTextEncode', text=(m['pre'] if pre is None else pre) + prompt, clip=cl_ref)
    if m['cfg'] <= 1.0 and cfg is None:
        neg = g.add('ConditioningZeroOut', conditioning=[pos, 0])
    else:
        neg = g.add('CLIPTextEncode', text=m['neg'] + negative, clip=cl_ref)
    model_ref = un_ref
    if init is not None:
        name = C.upload(init, 'kit_%s' % os.path.basename(init))
        li = g.add('LoadImage', image=name)
        lat = [g.add('VAEEncode', pixels=[li, 0], vae=va_ref), 0]
    else:
        lat = [g.add('EmptyLatentImage', width=w, height=h, batch_size=1), 0]
    if mask is not None:
        mname = C.upload(mask, 'kit_mask_%s' % os.path.basename(mask))
        lm = g.add('LoadImage', image=mname)
        im = g.add('ImageToMask', image=[lm, 0], channel='red')
        lat = [g.add('SetLatentNoiseMask', samples=lat, mask=[im, 0]), 0]
    if control is not None:
        cimg, key, strength = control
        name = C.upload(cimg, 'kit_ctl_%s' % os.path.basename(cimg))
        li = g.add('LoadImage', image=name)
        files = C.combo(info(), 'ModelPatchLoader', 'name')
        f = [x for x in files if key in x][0]
        mp = g.add('ModelPatchLoader', name=f)
        model_ref = [g.add('AnimaLLLiteApply', model=model_ref, model_patch=[mp, 0], image=[li, 0], strength=strength), 0]
    if inpaint is not None:   # 官方 LLLite 的重绘：(图, 遮罩)，遮罩白色处重画，从空 latent 起
        ip, mp_ = inpaint
        li = g.add('LoadImage', image=C.upload(ip, 'kit_ip_%s' % os.path.basename(ip)))
        lm = g.add('LoadImage', image=C.upload(mp_, 'kit_ipm_%s' % os.path.basename(mp_)))
        im = g.add('ImageToMask', image=[lm, 0], channel='red')
        mp = g.add('ModelPatchLoader', name='anima-lllite-inpainting-v2.safetensors')
        model_ref = [g.add('AnimaLLLiteApply', model=model_ref, model_patch=[mp, 0], image=[li, 0], mask=[im, 0], strength=1.0), 0]
    s = g.add('KSampler', model=model_ref, positive=[pos, 0], negative=[neg, 0], latent_image=lat, seed=seed, steps=steps or m['steps'], cfg=cfg or m['cfg'],
              sampler_name=sampler or m['sampler'], scheduler=m['scheduler'], denoise=denoise)
    d = g.add('VAEDecode', samples=[s, 0], vae=va_ref)
    g.add('SaveImage', images=[d, 0], filename_prefix='aldran/kit')
    imgs, secs = _run(g.nodes)
    im = Image.open(io.BytesIO(imgs[0])).convert('RGB')
    im.save(path)
    print(os.path.basename(path), '%.0f 秒' % secs, flush=True)
    return im


def extend(src, dst, prompt, seed=1, k=0.8, feather=24, model='turbo', tmp=None):
    """往左边和上边续画：原图缩到 k 贴到右下角，空出来的地方用官方的 LLLite 重绘补上，原来的像素不动。用来把裁到图外的手臂、剑、王冠画全。"""
    if os.path.exists(dst):
        return Image.open(dst)
    from PIL import ImageDraw, ImageFilter
    src_im = Image.open(src).convert('RGB')
    W, H = src_im.size
    nw, nh = int(W * k / 16) * 16, int(H * k / 16) * 16
    small = src_im.resize((nw, nh), Image.LANCZOS)
    x0, y0 = W - nw, H - nh
    bg = Image.new('RGB', (W, H), (255, 255, 255))
    bg.paste(small, (x0, y0))
    m = Image.new('L', (W, H), 255)
    ImageDraw.Draw(m).rectangle((x0 + feather, y0 + feather, W, H), fill=0)
    d = tmp or os.path.dirname(dst)
    os.makedirs(d, exist_ok=True)
    base = os.path.splitext(os.path.basename(dst))[0]
    ip, mp = os.path.join(d, '_%s_ip.png' % base), os.path.join(d, '_%s_mask.png' % base)
    bg.save(ip)
    m.save(mp)
    out = gen(os.path.join(d, '_%s_raw.png' % base), prompt, W, H, seed=seed, model=model, inpaint=(ip, mp))
    soft = m.filter(ImageFilter.GaussianBlur(feather / 2))
    res = Image.composite(out.convert('RGB'), bg, soft)
    res.save(dst)
    return res


def extend_right(src, dst, prompt, pad=192, seed=1, feather=24, model='turbo', tmp=None):
    """往右边续画一段，原来的像素不动。尺寸要是 16 的倍数。"""
    if os.path.exists(dst):
        return Image.open(dst)
    from PIL import ImageDraw, ImageFilter
    src_im = Image.open(src).convert('RGB')
    W, H = src_im.size
    bg = Image.new('RGB', (W + pad, H), (255, 255, 255))
    bg.paste(src_im, (0, 0))
    m = Image.new('L', bg.size, 0)
    ImageDraw.Draw(m).rectangle((W - feather, 0, W + pad, H), fill=255)
    d = tmp or os.path.dirname(dst)
    os.makedirs(d, exist_ok=True)
    base = os.path.splitext(os.path.basename(dst))[0]
    ip, mp = os.path.join(d, '_%s_ip.png' % base), os.path.join(d, '_%s_mask.png' % base)
    bg.save(ip)
    m.save(mp)
    out = gen(os.path.join(d, '_%s_raw.png' % base), prompt, W + pad, H, seed=seed, model=model, inpaint=(ip, mp))
    res = Image.composite(out.convert('RGB'), bg, m.filter(ImageFilter.GaussianBlur(feather / 2)))
    res.save(dst)
    return res


def cut(src, dst):
    """BiRefNet 抠透明底，存 dst（RGBA）。"""
    if os.path.exists(dst):
        return Image.open(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    name = C.upload(src, 'kit_cut_%s' % os.path.basename(src))
    g = C.Graph(info())
    li = g.add('LoadImage', image=name)
    lm = g.add('LoadBackgroundRemovalModel', bg_removal_name='birefnet.safetensors')
    rm = g.add('RemoveBackground', image=[li, 0], bg_removal_model=[lm, 0])
    mi = g.add('MaskToImage', mask=[rm, 0])
    g.add('SaveImage', images=[mi, 0], filename_prefix='aldran/kit_mask')
    imgs, secs = _run(g.nodes)
    m = Image.open(io.BytesIO(imgs[0])).convert('L')
    im = Image.open(src).convert('RGB')
    if m.size != im.size:
        m = m.resize(im.size, Image.LANCZOS)
    im.putalpha(m)
    im.save(dst)
    print('抠', os.path.basename(dst), '%.0f 秒' % secs, flush=True)
    return im


def sheet(paths, out, h=640, gap=8, bg=(24, 26, 34)):
    ims = [Image.open(p).convert('RGBA') for p in paths]
    ims = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    s = Image.new('RGBA', (W, h), bg + (255,))
    x = 0
    for i in ims:
        s.alpha_composite(i, (x, 0))
        x += i.width + gap
    s.convert('RGB').save(out, quality=90)
