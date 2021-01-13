import datetime
import os

from PIL import Image


def process_results_queue(results_queue):
    num = 0
    path = r'C:\PROGRAMOWANIE\auto_data\photos'
    directory_name = datetime.datetime.now().strftime('%Y-%m-%d')
    directory_path = os.path.join(path, directory_name)
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)
    directory_name = datetime.datetime.now().strftime('%H_%M_%S')
    directory_path = os.path.join(directory_path, directory_name)
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)

    while not results_queue.empty():
        processed_image, image_with_line, dist, trans, diff, dist_cor, trans_cor, change_cor, direction, time_s = results_queue.get()
        if processed_image is not None:
            image_name = str(num) \
                         + '_raw'\
                         + '.png'
            Image.fromarray(processed_image).save(os.path.join(directory_path, image_name))

        if image_with_line is not None:
            image_name = str(num) \
                         + '_dst_' + str(int(dist)) + '_tra_' + str(int(trans))  + '_dif_' + str(int(diff)) \
                         + '_dstC_' + str(int(dist_cor)) + '_traC_' + str(int(trans_cor)) + '_chaC_' + str(int(change_cor)) \
                         + '_dir_' + direction + '_tim_' + str(int(time_s))\
                         + '.png'
            Image.fromarray(image_with_line).save(os.path.join(directory_path, image_name))
        num += 1
