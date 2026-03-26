import cv2
import numpy as np
import tkinter as tk    # python自带的GUI库 用于弹出界面窗口
# filedialog: 用于打开文件选择对话框
# messagebox: 用于显示消息框（提示、错误等）
from tkinter import filedialog, messagebox, simpledialog


def read_image_chinese_path(path):
    """兼容 Windows 中文路径读取"""
    # 以二进制方式读取文件内容，得到字节数据
    data = np.fromfile(path, dtype=np.uint8)
    # 使用 OpenCV 从字节数据解码成图像，指定为灰度模式
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    print_matrix("img", img)
    return img


def save_image_chinese_path(path, img):
    """兼容 Windows 中文路径保存"""
    # 按照点好分割字符串，取最后一个元素作为扩展名，并转换为小写
    ext = path.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "bmp"]:
        ext = "png"
        path = path + ".png"

    # success：是否编码成功，布尔值
    # encoded：编码后的图像二进制数据
    success, encoded = cv2.imencode(f".{ext}", img)
    if not success:
        raise IOError("图片编码失败，无法保存")
    # 把编码后的图像数据写入文件，使用 tofile 方法直接写入二进制数据
    encoded.tofile(path)

def print_matrix(name, mat):
    h, w = mat.shape
    print(f"\n{name}: {h}x{w}")
    for row in mat:
        # " ".join(...) 是“用一个空格，把很多字符串连接起来”
        # f"{int(v):3d}" 是把每个像素值 v 转换成一个宽度为3的整数字符串，右对齐
        # :^3d 是居中对齐，:>3d 是右对齐，:<3d 是左对齐
        # :#04x 是以16进制格式输出，宽度为4，不足部分用0填充， # 表示在前面加上0x前缀
        print(" ".join(f"{int(v):^3d}" for v in row))

def thicken_black_strokes(gray_img, threshold_value=200, ksize=3, iterations=1):
    """
    白底黑字加粗
    gray_img: 灰度图
    threshold_value: 二值化阈值
    ksize: 膨胀核大小，3较自然，5更粗
    iterations: 膨胀次数
    """
    # 二值化：背景白、字黑
    # 大于阈值的像素值设为255（白色），小于等于阈值的像素值设为0（黑色）
    _, binary = cv2.threshold(gray_img, threshold_value, 255, cv2.THRESH_BINARY)
    # binary = gray_img  # 直接使用灰度图进行处理，保留细节

    if ksize < 1:
        ksize = 1
    if iterations < 1:
        iterations = 1

    kernel = np.ones((ksize, ksize), np.uint8)

    # 黑字加粗：反相 -> 膨胀 -> 再反相
    print_matrix("Binary", binary)
    inv = 255 - binary
    print_matrix("Inverted", inv)

    # 以矩阵的每个点为中心依此过卷积核 该卷积处理作用是使该点值变为当前卷积核覆盖区域的最大值
    # kernel是卷积核，iterations是卷积操作的次数，卷积核越大，次数越多，膨胀效果越明显
    dilated = cv2.dilate(inv, kernel, iterations=iterations)
    print_matrix("Dilated", dilated)
    result = 255 - dilated

    # # 腐蚀：直接对二值图像进行腐蚀，黑字加粗
    # result = cv2.erode(binary, kernel, iterations=iterations)
    return result


def main():
    # 创建一个 Tkinter 主窗口对象。
    # Tkinter 的各种文件框、提示框，一般都要依附这个主窗口。
    root = tk.Tk()
    # 隐藏主窗口，因为我们只需要文件对话框，不需要显示主窗口
    root.withdraw() 

    # 弹出"选择文件"对话框，允许用户选择要处理的图片文件
    input_path = filedialog.askopenfilename(
        title="请选择要加粗笔画的图片",
        filetypes=[
            ("图片文件", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("PNG", "*.png"),
            ("JPG", "*.jpg;*.jpeg"),
            ("BMP", "*.bmp"),
            ("所有文件", "*.*")
        ]
    )

    if not input_path:
        messagebox.showinfo("提示", "你没有选择图片，程序结束。")
        return

    # 读取图片
    img = read_image_chinese_path(input_path)
    if img is None:
        messagebox.showerror("错误", f"图片读取失败：\n{input_path}")
        return

    # 输入 kernel_size
    ksize = simpledialog.askinteger(
        "设置 kernel_size",
        "请输入字体加粗程度（推荐3或5）：",
        initialvalue=3,
        minvalue=1,
        maxvalue=99
    )
    if ksize is None:
        messagebox.showinfo("提示", "你取消了 kernel_size 设置，程序结束。")
        return


    # 处理：3x3 适度加粗
    result = thicken_black_strokes(img, threshold_value=200, ksize=ksize, iterations=1)

    # 选择保存路径
    output_path = filedialog.asksaveasfilename(
        title="请选择保存位置",
        defaultextension=".png",
        initialfile="thicker_result.png",
        filetypes=[
            ("PNG", "*.png"),
            ("JPG", "*.jpg"),
            ("BMP", "*.bmp")
        ]
    )

    if not output_path:
        messagebox.showinfo("提示", "你取消了保存，程序结束。")
        return

    # 保存图片
    try:
        save_image_chinese_path(output_path, result)
        messagebox.showinfo(
            "完成",
            f"处理完成，已保存到：\n{output_path}\n\n"
            f"参数： 放大程度={ksize}"
        )
    except Exception as e:
        messagebox.showerror("错误", f"保存失败：\n{e}")


if __name__ == "__main__":
    main()
