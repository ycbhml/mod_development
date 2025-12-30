'''
/*
 *                        _oo0oo_
 *                       o8888888o
 *                       88" . "88
 *                       (| -_- |)
 *                       0\  =  /0
 *                     ___/`---'\___
 *                   .' \\|     |// '.
 *                  / \\|||  :  |||// \
 *                 / _||||| -:- |||||- \
 *                |   | \\\  - /// |   |
 *                | \_|  ''\---/''  |_/ |
 *                \  .-\__  '-'  ___/-. /
 *              ___'. .'  /--.--\  `. .'___
 *           ."" '<  `.___\_<|>_/___.' >' "".
 *          | | :  `- \`.;`\ _ /`;.`/ - ` : | |
 *          \  \ `_.   \_ __\ /__ _/   .-` /  /
 *      =====`-.____`.___ \_____/___.-`___.-'=====
 *                        `=---='
 * 
 * 
 *      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * 
 *            佛祖保佑       永不宕机     永无BUG
 */
'''

import os
from PIL import Image
from PIL import DdsImagePlugin

def flip_alpha(image):
    """翻转图像的 Alpha 通道"""
    r, g, b, a = image.split()  
    a = Image.eval(a, lambda px: 255 - px)  
    return Image.merge("RGBA", (r, g, b, a))  

def should_flip_alpha(image):
    """判断图像的默认区域 Alpha 通道是否小于127.5，若是则需要翻转"""
    center = image.crop((
        image.width // 4, 
        image.height // 4, 
        3 * image.width // 4, 
        3 * image.height // 4
    ))
    _, _, _, a = center.split()
    avg_alpha = sum(a.getdata()) / len(a.getdata())

    return avg_alpha < 127.5

def convert_dds_to_png(dds_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(dds_folder):
        if filename.endswith(".dds"):
            dds_path = os.path.join(dds_folder, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(output_folder, png_filename)
            with Image.open(dds_path) as img:
                if img.mode == 'RGBA' and should_flip_alpha(img):
                    img = flip_alpha(img)
                img.save(png_path)
            print(f"Converted {dds_path} to {png_path}")

current_folder = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(current_folder, "Textures_Png")

convert_dds_to_png(current_folder, output_folder)
